"""Logging helper module standardizing logging and reducing boilerplate."""

import argparse
import copy
import fileinput
import functools
import json
import logging
import logging.config
import os
import pathlib
import re
import sys
from datetime import datetime

from dateutil.parser import parse as parse_dt
from devtools.ansi import sformat
from pydantic import Field
from pydantic_settings import BaseSettings
from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name
from striprtf.striprtf import rtf_to_text

__all__ = ["Filter", "add_log_level", "get_log_config", "setup_logging"]

# TODO add context logger support to fully replace flywheel-common

# map of go logging level names to python ones
go_level = {
    "dbug": "DEBUG",
    "info": "INFO",
    "warn": "WARNING",
    "eror": "ERROR",
    "crit": "CRITICAL",
}

# map of mongo log severity level to python level
mongo_level = {key[0].upper(): value for key, value in go_level.items()}

# map of python logging level names to colors
level_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "magenta",
}


def setup_logging(**kwargs) -> None:
    """Configure logging with settings from `get_log_config()`."""
    logging.config.dictConfig(get_log_config(**kwargs))


def get_log_config(**kwargs) -> dict:
    """Get log config dict based on kwargs and/or envvars."""
    # create log config using kwargs (~application defaults)
    config = LogConfig(**kwargs)
    if config.handler == "file":
        color = False
    elif config.color is None:
        color = getattr(sys, config.handler).isatty()
    else:
        color = config.color
    # merge any env-configured loggers/filters (~runtime overrides)
    env_config = LogConfig()  # type: ignore
    config.loggers.update(env_config.loggers)
    config.filters.update(env_config.filters)
    # return the logconfig dict
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {"level": config.level, "handlers": [config.handler]},
        "loggers": {
            logger: {"level": level or config.level, "handlers": [config.handler]}
            for logger, level in config.loggers.items()
        },
        "filters": {
            filt: {"()": "fw_logging.Filter", "add_all": False, **kwargs}
            for filt, kwargs in config.filters.items()
        },
        "formatters": {
            "text": {
                "()": "fw_logging.Formatter",
                "fmt": config.fmt,
                "datefmt": config.datefmt,
                "callfmt": config.callfmt,
                "color": color,
            },
            "json": {
                "()": "fw_logging.JSONFormatter",
                "callfmt": config.callfmt,
                "tag": config.json_tag,
            },
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "filters": list(config.filters),
                "formatter": config.formatter,
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
                "filters": list(config.filters),
                "formatter": config.formatter,
            },
            "file": {
                # TODO custom rotation to make it multiprocessing-safe
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(config.filename),
                "delay": True,
                "maxBytes": config.max_bytes,
                "backupCount": config.backup_count,
                "filters": list(config.filters),
                "formatter": config.formatter,
            },
        },
    }


class LogConfig(BaseSettings, env_prefix="FW_LOG_"):
    """Logging config."""

    level: str = Field("INFO", pattern=r"DEBUG|INFO|WARNING|ERROR|CRITICAL")
    handler: str = Field("stdout", pattern=r"stdout|stderr|file")
    formatter: str = Field("text", pattern=r"text|json")
    loggers: dict[str, str | None] = {}
    filters: dict[str, dict[str, str]] = {}

    # options for the file handler
    filename: pathlib.Path = pathlib.Path("log.txt")
    max_bytes: int = 10 << 20  # 10 MB
    backup_count: int = 10

    # options for the text formatter
    fmt: str = "{asctime}.{msecs:03.0f} {levelname} {caller} {message}"
    datefmt: str = "%Y-%m-%dT%H:%M:%S"
    # module name regex for which to format the caller as module:lineno
    # by default, the logger name is used as the caller for all logs
    callfmt: str | None = None
    color: bool | None = None

    # options for the json formatter
    json_tag: str | None = None


class Filter(logging.Filter):
    """Log exclusion filter allowing temporary filtering as a context manager."""

    def __init__(self, *, name: str = "", msg: str = "", add_all: bool = True) -> None:
        """Add exclusion filter to all handlers attached to the root logger.

        Args:
            name (str): Logger name prefix to ignore messages from.
            msg (str): Log message pattern to ignore when matched via re.search.
            add_all (bool): Set to False to skip auto-adding on all handlers.
        """
        assert name or msg, "Filter record name and/or msg required"
        super().__init__(name)
        self.name = name
        self.msg_re = re.compile(msg) if msg else None
        if add_all:
            handlers = logging.root.handlers
            assert handlers, "No handlers found - run setup_logging() first"
            for handler in handlers:
                handler.addFilter(self)

    def __enter__(self) -> "Filter":
        """Enter 'with' context - return the filter object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Exit 'with' context - remove filter from the root handlers."""
        for handler in logging.root.handlers:
            handler.removeFilter(self)

    def filter(self, record: logging.LogRecord) -> bool:
        """Return True if the record doesn't match all of the exclude filters."""
        exclude = []
        if self.name:
            exclude.append(super().filter(record))
        if self.msg_re:
            exclude.append(bool(self.msg_re.search(record.msg)))
        return not all(exclude)


class Formatter(logging.Formatter):
    """Log formatter with color support.

    See https://github.com/encode/uvicorn/blob/0.12.3/uvicorn/logging.py
    """

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        callfmt: str | None = None,
        color: bool = False,
    ) -> None:
        """Initialize Formatter."""
        super().__init__(fmt=fmt, datefmt=datefmt, style="{")
        self.callfmt = callfmt
        self.color = color

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Colorize levelname if color is enabled."""
        record_ = copy.copy(record)
        record_.__dict__["levelname"] = get_levelname(record.levelno, self.color)
        record_.__dict__["caller"] = get_caller(record, self.callfmt, self.color)
        return super().formatMessage(record_)


@functools.lru_cache()
def get_levelname(levelno: int, color: bool = False) -> str:
    """Return 4 char long log level name, optionally colorized (cached)."""
    levelname = logging._levelToName.get(levelno, f"LV{levelno:02d}")[:4]
    if not color:
        return levelname
    format_args = ["bold"]
    for level, color_name in level_colors.items():
        if levelno <= getattr(logging, level):
            format_args.append(color_name)
            break
    return sformat(levelname, *format_args)


def get_caller(
    record: logging.LogRecord,
    callfmt: str | None = None,
    color: bool = False,
) -> str:
    """Return log record caller information, optionally colorized."""
    module_path = get_module_path(record.pathname)
    if callfmt and re.match(callfmt, module_path):
        caller = f"{module_path}:{record.lineno}"
    else:
        caller = record.name  # pragma: no cover
    if not color:
        return caller
    return sformat(caller, "blue")


@functools.lru_cache()
def get_module_path(filepath: str) -> str:
    """Return python module path from the given filepath (cached)."""
    path = pathlib.Path(filepath)
    pkg, module_path = path.parent, path.stem
    while (pkg / "__init__.py").exists() or (pkg / "__init__.pyc").exists():
        module_path = f"{pkg.name}.{module_path}"
        pkg = pkg.parent
    return module_path


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def __init__(
        self,
        callfmt: str | None = None,
        tag: str | None = None,
    ) -> None:
        """Initialize JSONFormatter."""
        self.callfmt = callfmt
        self.tag = tag
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format the given LogRecord as a JSON string."""
        dt = datetime.fromtimestamp(record.created)
        ts = dt.isoformat(timespec="milliseconds")[:23]
        record_dict = {
            "message": record.getMessage(),
            "severity": record.levelname,
            "timestamp": ts,
            "caller": get_caller(record, self.callfmt),
            "process": record.process,
            "thread": record.thread,
        }
        if record.exc_info:
            record_dict["exc"] = self.formatException(record.exc_info)
        if "tag" in record.__dict__ or self.tag:
            record_dict["tag"] = record.__dict__.get("tag") or self.tag
        return json.dumps(record_dict, indent=None, separators=(",", ":"))


def logformat(argv=None) -> None:
    """Read logs and print them in a human-readable format."""
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description=logformat.__doc__)
    file_help = "input file to read logs from (default: stdin)"
    parser.add_argument("file", metavar="FILE", nargs="?", default="-", help=file_help)
    color_vals = ["never", "auto", "always"]
    color_help = "color output always|auto|never (default: auto)"
    color_kw: dict = dict(choices=color_vals, default="auto", help=color_help)
    parser.add_argument("-c", "--color", metavar="WHEN", **color_kw)
    args = parser.parse_args(argv)
    if args.color == "always":
        color = True
    elif args.color == "never":
        color = False
    else:
        color = sys.stdout.isatty()
    try:
        # json support for gcp/aws cloud logs
        if args.file.lower().endswith("json"):  # pragma: no cover
            with open(args.file, encoding="utf8") as file:
                lines = []
                for log in json.load(file):
                    log = log.get("jsonPayload") or log.get("@message")
                    msg = log["message"]
                    record = msg if isinstance(msg, dict) else {"msg": msg}
                    record["pod"] = log["kubernetes"]["pod_name"]
                    lines.append(json.dumps(record))
        # rtf support for tss providing logs in rich text
        elif args.file.lower().endswith("rtf"):  # pragma: no cover
            with open(args.file, encoding="utf8") as file:
                lines = rtf_to_text(file.read()).splitlines()
        # nondescript extension or piped input - format line by line
        else:
            lines = fileinput.input(files=(args.file,))
        for line in lines:
            if line := line.rstrip():  # noqa PLW2901
                print(format_line(line, color=color))
                sys.stdout.flush()
    except (KeyboardInterrupt, BrokenPipeError):  # pragma: no cover
        sys.stdout = open(os.devnull, "w", encoding="utf8")


tb_lexer = get_lexer_by_name("pytb")
json_lexer = get_lexer_by_name("json")
term_formatter = get_formatter_by_name("terminal")


def format_line(line: str, color: bool = False) -> str:
    """Return a human-readable log line from a (possibly) JSON log record."""
    # grok and strip kubectl/stern pod prefixes
    pod, line = get_pod(line), re.sub(rf"^{pod_re}", "", line, flags=re.X)
    # grok and strip kubectl/stern timestamps
    time, line = get_time(line), re.sub(rf"^{time_re}", "", line, flags=re.I | re.X)
    # grok level, start creating the record
    record = {"pod": pod, "time": time, "lvl": get_lvl(line)}
    # split prefixes from otherwise good json records
    prefix = ""
    if "{" in line and not line.startswith("{"):
        pos = line.index("{")
        prefix, line = line[:pos], line[pos:]
    # try to parse the remainder as json
    try:
        parsed = {k: v for k, v in parse_json(line).items() if v}
        record.update(parsed)
    except (AssertionError, KeyError, ValueError):
        record["msg"] = line
    if prefix:
        record["msg"] = f"{prefix}{record['msg']}"
    # get time, format and colorize
    time = record.get("time") or ""
    time = f"{time:>23.23}"
    time = sformat(time, "dim") if color else time
    # get level, map go to py, pad/truncate, colorize
    lvl = record.get("lvl") or ""
    lvl = go_level.get(lvl) or mongo_level.get(lvl) or lvl
    lvl = f"{lvl:4.4}".upper()
    lvl = sformat(lvl, lvl_clr.get(lvl, "bold")) if color else lvl
    # get caller, colorize
    caller = record.get("caller") or ""
    caller = sformat(caller, "blue") if caller and color else caller
    # get msg, strip timestamp
    msg = record.get("msg") or ""
    msg = re.sub(rf"^{time_re}", "", msg, flags=re.I | re.X)
    # colorize python traces
    if color and "Traceback (most recent call last)" in msg:
        msg = highlight(msg, tb_lexer, term_formatter).rstrip()
    # format and colorize mongo attr jsons
    if mongo_attr := record.get("mongo_attr"):
        pretty = json.dumps(mongo_attr, indent=2)
        compact = json.dumps(mongo_attr, separators=(",", ":"))
        attr = pretty if "Slow query" in msg else compact
        if color:
            attr = highlight(attr, json_lexer, term_formatter)
        if color and "Slow query" in msg:
            ms = int(re.sub(r'.*"durationMillis":(\d+).*', r"\1", compact))
            clr = "green" if ms < 500 else "yellow" if ms < 10000 else "red"
            attr = re.sub(str(ms), sformat(str(ms), "bold", clr), attr)
        attr = attr.rstrip()
        join = "\n" if "\n" in attr else " "
        msg += f"{join}{attr}"
    # put together the output parts in order
    parts = [time, lvl]
    if pod := record.get("pod"):
        # TODO colorize
        parts.append(pod)
    if caller:
        parts.append(caller)
    # indent multiline msgs
    parts.append(msg.replace("\n", "\n  "))
    return " ".join(parts)


ansi_re = r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]"
pod_re = rf"""
(\[pod/)?
(?P<cpod> ({ansi_re})? (?P<pod>[a-z][a-z0-9]+(-[a-z0-9]+)+) ({ansi_re})?)
[/ ]
(?P<ccont>({ansi_re})? (?P<cont>[a-z][a-z0-9-]+)            ({ansi_re})?)
\]? [ ]?
"""


def get_pod(line: str) -> str:
    """Return the pod prefix parsed from a kubectl/stern log line (if present)."""
    match = re.match(pod_re, line, flags=re.X)
    if not match:
        return ""
    groups = match.groupdict()
    if groups["cont"] in groups["pod"] or groups["cont"] == "dicom-json-indexer":
        return groups["cpod"]
    return f"{groups['cpod']}/{groups['ccont']}"  # pragma: no cover


time_re = r"""
((
(?P<y1>\d\d\d\d) -   (?P<m1>\d\d)    -   (?P<d1>\d\d) |
(?P<d2>\d\d)    [/ ] (?P<m2>\w\w\w) [/ ] (?P<y2>\d\d\d\d)
) [T: ] )?
(?P<H>\d\d)      :   (?P<M>\d\d)     :   (?P<S>\d\d)
( [.,] (?P<N>\d+)            )?
( [ ]? ([+-]?\d\d:?\d\d | Z) )? [ ]?
"""


def get_time(line: str) -> str:
    """Return the first timestamp parsed from a log line (if present)."""
    match = re.search(time_re, line, flags=re.I | re.X)
    if not match:
        return ""
    groups = match.groupdict()
    groups["N"] = groups["N"] or "0"
    for key in "ymd":
        groups[key] = groups[f"{key}1"] or groups[f"{key}2"]
        if not groups[key]:
            return "{H}:{M}:{S}.{N:0<3.3}".format_map(groups)  # pragma: no cover
    dt_str = "{y}-{m}-{d} {H}:{M}:{S}.{N}".format_map(groups)
    return parse_dt(dt_str).isoformat(timespec="milliseconds")


lvl_re = r"crit|erro|eror|warn|info|debu|dbug"
lvl_clr = {lvl[:4]: clr for lvl, clr in level_colors.items()}


def get_lvl(line: str) -> str:
    """Return the log level parsed from a log line."""
    match = re.search(lvl_re, line, flags=re.I)
    if match:
        return match.group()
    return ""


def parse_json(line: str) -> dict:
    """Return log record dict with common fields from a JSON log line."""
    record = json.loads(line)
    assert isinstance(record, dict), f"dict expected, got {type(record)}"
    # fw-logging+flywheel-common:timestamp / engine:t
    time = record.get("timestamp") or record.get("t")
    time = time.get("$date") if isinstance(time, dict) else time  # mongo
    # fw-logging+flywheel-common:severity / engine:lvl / mongo:s
    lvl = record.get("severity") or record.get("lvl") or record.get("s")
    # fw-logging+engine:caller / flywheel-common:filename+lineno
    try:
        caller = "{filename}:{lineno}".format_map(record)
    except KeyError:
        caller = record.get("caller")
    # fw-logging+flywheel-common:message / engine:msg
    msg = record.get("message") or record.get("msg")
    # perimeter http access
    if not msg and record.get("method") and record.get("uri"):
        msg = '{remote_ip} - "{method} {uri}" {status}'.format_map(record)
    assert msg  # typing
    # engine+perimeter: prefix action
    action = record.get("action")
    msg = f"({action}) {msg}" if action else msg
    # perimeter heartbeat: suffix stats
    stats = record.get("stats")
    msg = f"{msg} {stats}" if stats else msg
    # fw-logging:exc / flywheel-common:exc_info
    exc = record.get("exc") or record.get("exc_info")
    msg = f"{msg}\n{exc}" if exc else msg
    # engine:err - usually a single line
    if record.get("err"):
        msg = f"{msg}: {record['err']}"
    return dict(
        time=time,
        lvl=lvl,
        caller=caller,
        msg=msg,
        pod=record.get("pod"),
        mongo_attr=record.get("attr"),
    )


def add_log_level(name: str, num: int) -> None:
    """Add a custom log level to the logging module.

    * add `name.upper()` attribute to the logging module with value num.
    * add `name.lower()` function/method to the logging module/logger class.

    References:
    * https://docs.python.org/3/library/logging.html#logging-levels
    * https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#logseverity
    """
    name = name.upper()
    func = name.lower()

    def _root_log(msg, *args, **kwargs):
        kwargs.setdefault("stacklevel", 3)
        logging.log(num, msg, *args, **kwargs)

    def _logger_log(self, msg, *args, **kwargs):  # pragma: no cover
        if self.isEnabledFor(num):
            self._log(num, msg, args, **kwargs)

    _root_log.__doc__ = f"Log a message with severity '{name}' on the root logger."
    _logger_log.__doc__ = f"Log 'msg % args' with severity '{name}'."

    logging.addLevelName(num, name)
    setattr(logging, name, num)
    setattr(logging, func, _root_log)
    setattr(logging.getLoggerClass(), func, _logger_log)
