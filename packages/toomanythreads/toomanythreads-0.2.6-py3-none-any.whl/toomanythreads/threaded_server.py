import threading
from functools import cached_property

import uvicorn
from fastapi import FastAPI
from httpx import AsyncClient, Limits
from loguru import logger as log
from starlette.requests import Request
from starlette.responses import Response
from toomanyports import PortManager

from toomanythreads import ManagedThread


class ThreadedServer(FastAPI):
    def __init__(
            self,
            host: str = None,
            port: int = None,
            verbose: bool = True,
    ) -> None:
        self.host = "localhost" if host is None else host
        self.port = PortManager.random_port() if port is None else port
        PortManager.kill(self.port, force=True)
        self.verbose = verbose
        super().__init__(debug=self.verbose)
        if self.verbose: log.success(f"{self}: Initialized successfully!\n  - host={self.host}\n  - port={self.port}")

    @cached_property
    def url(self):
        return f"http://{self.host}:{self.port}"

    @cached_property
    def uvicorn_cfg(self) -> uvicorn.Config:
        return uvicorn.Config(
            app=self,
            host=self.host,
            port=self.port,
            # reload=True,
            # log_config=,
        )

    @cached_property
    def thread(self) -> threading.Thread:  # type: ignore
        def proc(self):
            if self.verbose: log.info(f"[{self}]: Launching microservice on {self.host}:{self.port}")
            server = uvicorn.Server(config=self.uvicorn_cfg)
            server.run()

        return ManagedThread(proc, self)

    @cached_property
    def client(self):
        return AsyncClient(
            limits=Limits(
                max_keepalive_connections=20,
                max_connections=100
            )
        )

    async def forward(self, path: str, request: Request):
        """
        Utility for developers to easily proxy HTTP requests.
        Use cases: forward to private microservices, external api requests, etc.
        """
        url = f"{self.url}/{path}"
        log.debug(f"{self}: Attempting request to {url}")

        try:
            filtered_headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in {'host', 'content-length', 'connection'}
            }

            resp = await self.client.request(
                request.method,
                url,
                headers=filtered_headers,
                content=await request.body(),
                params=request.query_params,
                follow_redirects=True
            )

            response_headers = {
                k: v for k, v in resp.headers.items()
                if k.lower() not in {'content-encoding', 'transfer-encoding', 'content-length', 'connection'}
            }

            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=response_headers,
                media_type=resp.headers.get('content-type')  # Preserve content type
            )

        except Exception as e:
            log.error(f"{self}: Error processing request: {e}")
            return Response(
                "An unexpected error occurred.",
                status_code=500
            )
