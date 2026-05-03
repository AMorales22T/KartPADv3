from __future__ import annotations

import asyncio
import http.server
import ssl
import threading
from dataclasses import dataclass
from typing import Any

import websockets

from .config import APP_NAME, HTTP_PORT, WS_PORT
from .controller import ControllerHub
from .dsu import DSUServer
from .ssl_cert import get_ssl_context
from .web import HTTPS_PORT, WSS_PORT, MobileGateway, StaticHandler, get_local_ips


@dataclass(slots=True)
class RuntimeInfo:
    local_ips: list[str]
    dsu_port: int
    https_enabled: bool
    http_port: int = HTTP_PORT
    https_port: int = HTTPS_PORT
    ws_port: int = WS_PORT
    wss_port: int = WSS_PORT

    @property
    def primary_ip(self) -> str:
        return self.local_ips[0] if self.local_ips else "127.0.0.1"

    def http_url(self, ip: str) -> str:
        return f"http://{ip}:{self.http_port}"

    def https_url(self, ip: str) -> str:
        return f"https://{ip}:{self.https_port}"

    def preferred_browser_url(self, ip: str) -> str:
        return self.https_url(ip) if self.https_enabled else self.http_url(ip)


class KardPadRuntime:
    def __init__(self) -> None:
        self._hub = ControllerHub()
        self._gateway = MobileGateway(self._hub)
        self._dsu_server = DSUServer(self._hub)
        self._http_server: http.server.ThreadingHTTPServer | None = None
        self._https_server: http.server.ThreadingHTTPServer | None = None
        self._http_thread: threading.Thread | None = None
        self._https_thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._loop_thread: threading.Thread | None = None
        self._ws_server: Any | None = None
        self._wss_server: Any | None = None
        self._running = False
        self._info: RuntimeInfo | None = None

    @property
    def hub(self) -> ControllerHub:
        """Public accessor for the ControllerHub (used by the UI test panel)."""
        return self._hub

    @property
    def info(self) -> RuntimeInfo:
        if self._info is None:
            msg = f"{APP_NAME} runtime is not started."
            raise RuntimeError(msg)
        return self._info

    def start(self) -> RuntimeInfo:
        if self._running:
            return self.info

        local_ips = get_local_ips()
        server_ssl, ws_ssl = get_ssl_context(local_ips[0])
        https_enabled = server_ssl is not None and ws_ssl is not None
        self._info = RuntimeInfo(
            local_ips=local_ips,
            dsu_port=self._dsu_server.port,
            https_enabled=https_enabled,
        )

        try:
            self._http_server = self._build_http_server(HTTP_PORT)
            self._http_thread = self._start_http_thread(self._http_server, "HTTP", HTTP_PORT)

            if https_enabled and server_ssl is not None:
                self._https_server = self._build_http_server(HTTPS_PORT, ssl_ctx=server_ssl)
                self._https_thread = self._start_http_thread(self._https_server, "HTTPS", HTTPS_PORT)

            self._dsu_server.start()
            self._start_loop_thread()
            assert self._loop is not None
            asyncio.run_coroutine_threadsafe(
                self._start_websocket_servers(ws_ssl if https_enabled else None),
                self._loop,
            ).result(timeout=10)
            self._running = True
            return self.info
        except Exception:
            self.stop()
            raise

    def stop(self) -> None:
        if self._loop is not None:
            try:
                asyncio.run_coroutine_threadsafe(self._stop_websocket_servers(), self._loop).result(timeout=10)
            except Exception:
                pass
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._loop_thread is not None:
                self._loop_thread.join(timeout=5)
            self._loop.close()
            self._loop = None
            self._loop_thread = None

        self._shutdown_http_server(self._https_server, self._https_thread)
        self._shutdown_http_server(self._http_server, self._http_thread)
        self._https_server = None
        self._http_server = None
        self._https_thread = None
        self._http_thread = None

        self._dsu_server.stop()
        self._running = False

    async def _start_websocket_servers(self, ssl_ctx: ssl.SSLContext | None) -> None:
        self._ws_server = await websockets.serve(self._gateway.handle_connection, "0.0.0.0", WS_PORT)
        print(f"[WS] Listening on ws://0.0.0.0:{WS_PORT}")
        if ssl_ctx is not None:
            self._wss_server = await websockets.serve(
                self._gateway.handle_connection,
                "0.0.0.0",
                WSS_PORT,
                ssl=ssl_ctx,
            )
            print(f"[WSS] Listening on wss://0.0.0.0:{WSS_PORT}")

    async def _stop_websocket_servers(self) -> None:
        if self._wss_server is not None:
            self._wss_server.close()
            await self._wss_server.wait_closed()
            self._wss_server = None

        if self._ws_server is not None:
            self._ws_server.close()
            await self._ws_server.wait_closed()
            self._ws_server = None

    def _start_loop_thread(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self._loop_thread.start()

    def _run_loop(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _build_http_server(
        self,
        port: int,
        ssl_ctx: ssl.SSLContext | None = None,
    ) -> http.server.ThreadingHTTPServer:
        httpd = http.server.ThreadingHTTPServer(("0.0.0.0", port), StaticHandler)
        if ssl_ctx is not None:
            httpd.socket = ssl_ctx.wrap_socket(httpd.socket, server_side=True)
        return httpd

    def _start_http_thread(
        self,
        httpd: http.server.ThreadingHTTPServer,
        label: str,
        port: int,
    ) -> threading.Thread:
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        scheme = "https" if label == "HTTPS" else "http"
        print(f"[{label}] Serving on {scheme}://0.0.0.0:{port}")
        return thread

    def _shutdown_http_server(
        self,
        httpd: http.server.ThreadingHTTPServer | None,
        thread: threading.Thread | None,
    ) -> None:
        if httpd is None:
            return
        try:
            httpd.shutdown()
        except OSError:
            pass
        try:
            httpd.server_close()
        except OSError:
            pass
        if thread is not None:
            thread.join(timeout=5)
