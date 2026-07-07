"""Alwaseet Alamin DLP gateway as a local HTTP service.

``POST /api/gate`` accepts ``{"text": "...", "user": "..."}``, sanitizes
secrets/PII, runs the immunity check on the sanitized text and returns
``ALLOW/REVIEW/QUARANTINE/BLOCK`` plus a safe ``outbound`` payload. This is the
integration point to put in front of any AI tool used by staff.
"""

from __future__ import annotations

from http.server import ThreadingHTTPServer
from typing import Any

from .gate import decide
from .http_base import BaseServiceHandler, build_server


def _gate_route(data: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    text = str(data.get("text") or "")
    if not text.strip():
        return 400, {"ok": False, "error": "missing 'text'"}
    user = str(data.get("user") or "human")
    result = decide(text, user=user)
    return 200, {"ok": True, **result}


class Handler(BaseServiceHandler):
    post_routes = {"/api/gate": staticmethod(_gate_route)}


def create_server(host: str | None = None, port: int | None = None) -> ThreadingHTTPServer:
    return build_server(Handler, host=host, port=port)


def run_server(host: str | None = None, port: int | None = None) -> None:
    from .version import __version__

    server = create_server(host=host, port=port)
    print(f"alwaseet service v{__version__}: http://{server.server_address[0]}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
