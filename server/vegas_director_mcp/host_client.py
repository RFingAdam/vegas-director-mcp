"""Client for the vegas-director MCP <-> VEGAS script host RPC channel.

Two transports are supported:
  - "pipe": Windows named pipe, same machine as VEGAS (default, lowest
    latency, no network exposure).
  - "tcp": loopback TCP, useful when the MCP server runs on a different
    machine than VEGAS (tunnel it, don't expose it directly -- see
    docs/PROTOCOL.md).

This module intentionally has zero VEGAS-specific knowledge -- it is a thin,
generic JSON-RPC-over-a-stream client. All VEGAS semantics live in the tool
functions in server/tools.py, which call VegasHostClient.call(method, params).
"""
from __future__ import annotations

import json
import os
import socket
from dataclasses import dataclass
from typing import Any


class VegasHostError(RuntimeError):
    """Raised when the script host returns a JSON-RPC error object."""

    def __init__(self, code: int, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


@dataclass
class VegasHostConfig:
    transport: str = "pipe"
    pipe_name: str = "vegas-director"
    tcp_host: str = "127.0.0.1"
    tcp_port: int = 8752

    @classmethod
    def from_env(cls) -> "VegasHostConfig":
        return cls(
            transport=os.environ.get("VEGAS_HOST_TRANSPORT", "tcp"),
            pipe_name=os.environ.get("VEGAS_HOST_PIPE_NAME", "vegas-director"),
            tcp_host=os.environ.get("VEGAS_HOST_ADDRESS", "127.0.0.1"),
            tcp_port=int(os.environ.get("VEGAS_HOST_PORT", "8752")),
        )


class VegasHostClient:
    """Blocking, one-request-per-connection JSON-RPC client.

    Kept deliberately simple for the Phase 0/1 scaffold: opens a fresh
    connection per call. Once real usage patterns emerge (e.g. many calls in
    a tight edit loop), switch to a persistent connection with a
    request-id-keyed response dispatcher rather than prematurely optimizing
    now.
    """

    def __init__(self, config: VegasHostConfig | None = None):
        self.config = config or VegasHostConfig.from_env()
        self._next_id = 1

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        req_id = self._next_id
        self._next_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {},
        }
        line = json.dumps(request) + "\n"

        raw_response = self._send(line)
        response = json.loads(raw_response)

        if "error" in response:
            err = response["error"]
            raise VegasHostError(err.get("code", -32000), err.get("message", "unknown error"))
        return response.get("result")

    def _send(self, line: str) -> str:
        if self.config.transport == "tcp":
            return self._send_tcp(line)
        if self.config.transport == "pipe":
            return self._send_pipe(line)
        raise ValueError(f"Unknown transport: {self.config.transport!r}")

    def _send_tcp(self, line: str) -> str:
        with socket.create_connection(
            (self.config.tcp_host, self.config.tcp_port), timeout=30
        ) as sock:
            sock.sendall(line.encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks).decode("utf-8").strip()

    def _send_pipe(self, line: str) -> str:
        # Named pipes are Windows-only and use a distinct API from sockets.
        # win32file is provided by pywin32 -- imported lazily so this module
        # still imports cleanly on non-Windows dev machines (e.g. for
        # running the media-analysis tools' unit tests without a Windows
        # box), and only fails at call time if pipe transport is actually
        # requested on a platform that can't support it.
        try:
            import win32file  # type: ignore
            import win32pipe  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Named-pipe transport requires pywin32 and a Windows host. "
                "Install pywin32, or set VEGAS_HOST_TRANSPORT=tcp instead."
            ) from exc

        pipe_path = rf"\\.\pipe\{self.config.pipe_name}"
        handle = win32file.CreateFile(  # type: ignore[misc]
            pipe_path,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None,
        )
        try:
            win32file.WriteFile(handle, line.encode("utf-8"))  # type: ignore[arg-type]
            _, data = win32file.ReadFile(handle, 65536)  # type: ignore[arg-type]
            data_bytes: bytes = data if isinstance(data, bytes) else data.encode("utf-8")
            return data_bytes.decode("utf-8").strip()
        finally:
            handle.Close()
