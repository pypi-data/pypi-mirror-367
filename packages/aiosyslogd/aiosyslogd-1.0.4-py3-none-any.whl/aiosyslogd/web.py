#!/usr/bin/env python
# -*- coding: utf-8 -*-
# aiosyslogd/web.py

from .config import load_config
from .db.logs_utils import redact
from .db.sqlite_utils import get_available_databases, QueryContext, LogQuery
from datetime import datetime, timedelta
from loguru import logger
from quart import Quart, render_template, request, abort, Response
from types import ModuleType
from typing import Any, Dict, Generator
import aiosqlite
import asyncio
import sys
import time

uvloop: ModuleType | None = None
try:
    if sys.platform == "win32":
        import winloop as uvloop
    else:
        import uvloop
except ImportError:
    pass  # uvloop or winloop is an optional for speedup, not a requirement.


# --- Globals & App Setup ---
CFG: Dict[str, Any] = load_config()
WEB_SERVER_CFG: Dict[str, Any] = CFG.get("web_server", {})
DEBUG: bool = WEB_SERVER_CFG.get("debug", False)
REDACT: bool = WEB_SERVER_CFG.get("redact", False)

# Configure the loguru logger with Quart formatting.
log_level: str = "DEBUG" if DEBUG else "INFO"
logger.remove()
logger.add(
    sys.stderr,
    format="[{time:YYYY-MM-DD HH:mm:ss ZZ}] [{process}] [{level}] {message}",
    level=log_level,
)

# Create a Quart application instance.
app: Quart = Quart(__name__)
# Enable the 'do' extension for Jinja2.
app.jinja_env.add_extension("jinja2.ext.do")
# Replace the default Quart logger with loguru logger.
app.logger = logger  # type: ignore[assignment]


# --- Datetime Type Adapters for SQLite ---
def adapt_datetime_iso(val: datetime) -> str:
    """Adapt datetime.datetime to timezone-aware ISO 8601 string."""
    return val.isoformat()


def convert_timestamp_iso(val: bytes) -> datetime:
    """Convert ISO 8601 string from DB back to a datetime.datetime object."""
    return datetime.fromisoformat(val.decode())


# Registering the adapters and converters for aiosqlite.
aiosqlite.register_adapter(datetime, adapt_datetime_iso)
aiosqlite.register_converter("TIMESTAMP", convert_timestamp_iso)


# --- Main Application Logic ---
@app.before_serving
async def startup() -> None:
    """Initial setup before serving requests."""
    app.logger.info(  # Verify the event loop policy being used.
        f"{__name__.title()} is running with "
        f"{asyncio.get_event_loop_policy().__module__}."
    )


@app.route("/")
async def index() -> str | Response:
    """Main route for displaying and searching logs."""
    # Prepare the context for rendering the index page.
    context: Dict[str, Any] = {
        "request": request,
        "available_dbs": await get_available_databases(CFG),
        "search_query": request.args.get("q", "").strip(),
        "filters": {  # Dictionary comprehension to get filter values.
            key: request.args.get(key, "").strip()
            for key in ["from_host", "received_at_min", "received_at_max"]
        },
        "selected_db": None,
        "logs": [],
        "total_logs": 0,
        "error": None,
        "page_info": {
            "has_next_page": False,
            "next_last_id": None,
            "has_prev_page": False,
            "prev_last_id": None,
        },
        "debug_query": "",
        "query_time": 0.0,
    }

    # Check if the page is loaded with no specific filters.
    is_unfiltered_load = (
        not context["search_query"]
        and not context["filters"]["from_host"]
        and not context["filters"]["received_at_min"]
        and not context["filters"]["received_at_max"]
    )

    # If it's an unfiltered load, set the default time to the last hour
    # to avoid loading too many logs at once which can be slow.
    if is_unfiltered_load:
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        # The HTML input type="datetime-local" expects 'YYYY-MM-DDTHH:MM'
        context["filters"]["received_at_min"] = one_hour_ago.strftime(
            "%Y-%m-%dT%H:%M"
        )

    if not context["available_dbs"]:
        context["error"] = (
            "No SQLite database files found. "
            "Ensure `aiosyslogd` has run and created logs."
        )
        return await render_template("index.html", **context)

    selected_db = request.args.get("db_file", context["available_dbs"][0])
    if selected_db not in context["available_dbs"]:
        abort(404, "Database file not found.")
    context["selected_db"] = selected_db

    start_time: float = time.perf_counter()  # Start measuring query time.

    query_context = QueryContext(
        db_path=selected_db,
        search_query=context["search_query"],
        filters=context["filters"],
        last_id=request.args.get("last_id", type=int),
        direction=request.args.get("direction", "next").strip(),
        page_size=50,
    )

    log_query = LogQuery(query_context, logger)
    db_results = await log_query.run()

    redacted_logs: Generator[dict[Any, str | Any], None, None] | None = None
    # If REDACT is enabled, redact sensitive information in logs.
    if REDACT and db_results["logs"]:
        # This is a generator to avoid loading all logs into memory at once.
        redacted_logs = (
            # Dictionary comprehension for redacting sensitive information
            # in the "Message" field while keeping other fields intact.
            {
                key: redact(row[key], "▒") if key == "Message" else row[key]
                for key in row.keys()
            }
            for row in db_results["logs"]
        )

    context.update(
        {
            "logs": redacted_logs or db_results["logs"],
            "total_logs": db_results["total_logs"],
            "page_info": db_results["page_info"],
            "debug_query": "\n\n---\n\n".join(db_results["debug_info"]),
            "error": db_results["error"],
            "query_time": time.perf_counter() - start_time,
        }
    )

    return await render_template("index.html", **context)


def check_backend() -> bool:
    """Checks if the backend database is compatible with the web UI."""
    db_driver: str | None = CFG.get("database", {}).get("driver")
    if db_driver == "meilisearch":
        logger.info("Meilisearch backend is selected.")
        logger.warning("This web UI is for the SQLite backend only.")
        return False
    return True


def main() -> None:
    """Main entry point for the web server."""
    if not check_backend():
        sys.exit(0)
    host: str = WEB_SERVER_CFG.get("bind_ip", "127.0.0.1")
    port: int = WEB_SERVER_CFG.get("bind_port", 5141)
    logger.info(f"Starting aiosyslogd-web interface on http://{host}:{port}")
    # Install uvloop if available for better performance.
    if uvloop:
        uvloop.install()
    app.run(host=host, port=port, debug=DEBUG)


if __name__ == "__main__":
    main()
