import asyncio
import ssl
import types
import typing

__all__ = ["NetworkBackend", "NetworkStream", "timeout"]


class NetworkStream:
    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, address: str = ''
    ) -> None:
        peername = writer.get_extra_info('peername')

        self._reader = reader
        self._writer = writer
        self._address = f"{peername[0]}:{peername[1]}"
        self._tls = False
        self._closed = False

    async def read(self, max_bytes: int = 64 * 1024) -> bytes:
        return await self._reader.read(max_bytes)

    async def write(self, buffer: bytes) -> None:
        self._writer.write(buffer)
        await self._writer.drain()

    async def start_tls(self, ctx: ssl.SSLContext, hostname: str | None = None) -> None:
        # Requires Python >= 3.11...
        await self._writer.start_tls(ctx, server_hostname=hostname)
        self._tls = True

    async def close(self) -> None:
        self._writer.close()
        await self._writer.wait_closed()
        self._closed = True

    def __repr__(self):
        description = ""
        description += " TLS" if self._tls else ""
        description += " CLOSED" if self._closed else ""
        return f"<NetworkStream [{self._address!r}{description}]>"

    def __del__(self):
        if not self._closed:
            import warnings
            warnings.warn("NetworkStream was garbage collected without being closed.")

    # Context managed usage...
    async def __aenter__(self) -> "NetworkStream":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ):
        await self.close()


class NetworkServer:
    def __init__(self, host: str, port: int, server: asyncio.Server):
        self.host = host
        self.port = port
        self._server = server

    # Context managed usage...
    async def __aenter__(self) -> "NetworkServer":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None = None,
        exc_value: BaseException | None = None,
        traceback: types.TracebackType | None = None,
    ):
        self._server.close()
        await self._server.wait_closed()


class NetworkBackend:
    async def connect(self, host: str, port: int) -> NetworkStream:
        """
        Connect to the given address, returning a Stream instance.
        """
        reader, writer = await asyncio.open_connection(host, port)
        return NetworkStream(reader, writer, address=f"{host}:{port}")

    async def serve(self, host: str, port: int, handler: typing.Callable[[NetworkStream], None]) -> NetworkServer:
        async def callback(reader, writer):
            stream = NetworkStream(reader, writer)
            await handler(stream)

        server = await asyncio.start_server(callback, host, port)
        return NetworkServer(host, port, server)


Semaphore = asyncio.Semaphore
Lock = asyncio.Lock
timeout = asyncio.timeout
sleep = asyncio.sleep
