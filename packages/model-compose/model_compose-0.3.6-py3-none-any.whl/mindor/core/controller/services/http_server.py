from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, AsyncIterator, Any
from types import AsyncGeneratorType
from typing_extensions import Self
from pydantic import BaseModel
from mindor.dsl.schema.controller import HttpServerControllerConfig
from mindor.dsl.schema.component import ComponentConfig
from mindor.dsl.schema.listener import ListenerConfig
from mindor.dsl.schema.gateway import GatewayConfig
from mindor.dsl.schema.logger import LoggerConfig
from mindor.dsl.schema.workflow import WorkflowConfig
from mindor.core.utils.http_request import parse_request_body, parse_options_header
from mindor.core.utils.http_client import HttpEventStreamResource
from mindor.core.utils.streaming import StreamResource
from ..base import ControllerService, ControllerType, TaskState, TaskStatus, register_controller
from fastapi import FastAPI, APIRouter, Request, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse, StreamingResponse
from starlette.background import BackgroundTask
import uvicorn, json

class WorkflowTaskRequestBody(BaseModel):
    workflow_id: Optional[str] = None
    input: Optional[Any] = None
    wait_for_completion: bool = True
    output_only: bool = False

class TaskResult(BaseModel):
    task_id: str
    status: Literal[ "pending", "processing", "completed", "failed" ]
    output: Optional[Any] = None
    error: Optional[Any] = None

    @classmethod
    def from_instance(cls, instance: TaskState) -> Self:
        return cls(
            task_id=instance.task_id,
            status=instance.status,
            output=instance.output,
            error=instance.error
        )

@register_controller(ControllerType.HTTP_SERVER)
class HttpServerController(ControllerService):
    def __init__(
        self,
        config: HttpServerControllerConfig,
        components: Dict[str, ComponentConfig],
        listeners: List[ListenerConfig],
        gateways: List[GatewayConfig],
        workflows: Dict[str, WorkflowConfig],
        loggers: List[LoggerConfig],
        daemon: bool
    ):
        super().__init__(config, components, listeners, gateways, workflows, loggers, daemon)

        self.server: Optional[uvicorn.Server] = None
        self.app: FastAPI = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
        self.router: APIRouter = APIRouter()
        
        self._configure_server()
        self._configure_routes()
        self.app.include_router(self.router, prefix=self.config.base_path)

    def _configure_server(self) -> None:
        self.app.add_middleware(
            CORSMiddleware, 
            allow_origins=[self.config.origins], 
            allow_credentials=True, 
            allow_methods=["*"], 
            allow_headers=["*"],
        )

    def _configure_routes(self) -> None:
        @self.router.post("/workflows")
        async def run_workflow(
            request: Request
        ):
            body = await self._parse_workflow_body(request)
            state = await self.run_workflow(body.workflow_id, body.input, body.wait_for_completion)

            if body.output_only and not body.wait_for_completion:
                raise HTTPException(status_code=400, detail="output_only requires wait_for_completion=true.")
            
            if not body.output_only and isinstance(state.output, (StreamResource, AsyncGeneratorType)):
                raise HTTPException(status_code=400, detail="Streaming output is only allowed when output_only=true.")

            if body.output_only:
                return self._render_task_output(state)
            
            return self._render_task_state(state)

        @self.router.get("/tasks/{task_id}")
        async def get_task_state(
            task_id: str,
            output_only: bool = False
        ):
            state = self.get_task_state(task_id)

            if not state:
                raise HTTPException(status_code=404, detail="Task not found.")
            
            if not output_only and isinstance(state.output, (StreamResource, AsyncGeneratorType)):
                raise HTTPException(status_code=400, detail="Streaming output is only allowed when output_only=true.")

            if output_only:
                return self._render_task_output(state)

            return self._render_task_state(state)

    async def _serve(self) -> None:
        self.server = uvicorn.Server(uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        ))
        await self.server.serve()
        self.server = None
 
    async def _shutdown(self) -> None:
        if self.server:
            self.server.should_exit = True

    async def _parse_workflow_body(self, request: Request) -> WorkflowTaskRequestBody:
        content_type, _ = parse_options_header(request.headers, "Content-Type")

        if content_type not in [ "application/json", "multipart/form-data", "application/x-www-form-urlencoded" ]:
            if not content_type:
                raise HTTPException(status_code=400, detail="Missing or empty Content-Type header.")
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported Content-Type: {content_type}")

        try:
            return WorkflowTaskRequestBody(**await parse_request_body(request, content_type, nested=True))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid request body: {e}")

    def _render_task_state(self, state: TaskState) -> Response:
        return JSONResponse(content=TaskResult.from_instance(state).model_dump(exclude_none=True))

    def _render_task_output(self, state: TaskState) -> Response:
        if state.status in [ TaskStatus.PENDING, TaskStatus.PROCESSING ]:
            raise HTTPException(status_code=202, detail="Task is still in progress.")

        if state.status == TaskStatus.FAILED:
            raise HTTPException(status_code=500, detail=str(state.error))

        if isinstance(state.output, AsyncGeneratorType):
            return self._render_async_generator(state.output)
        
        if isinstance(state.output, HttpEventStreamResource):
            return self._render_event_stream_resource(state.output)

        if isinstance(state.output, StreamResource):
            return self._render_stream_resource(state.output)

        return JSONResponse(content=state.output)
    
    def _render_async_generator(self, generator: AsyncGeneratorType) -> Response:
        async def _event_generator() -> AsyncIterator[bytes]:
            async for chunk in generator:
                if not isinstance(chunk, str):
                    chunk = json.dumps()
                yield b"data: " + chunk.encode("utf-8") + b"\n\n"

        return StreamingResponse(
            _event_generator(),
            media_type="text/event-stream",
            headers={ "Cache-Control": "no-cache" }
        )

    def _render_event_stream_resource(self, resource: HttpEventStreamResource) -> Response:
        async def _event_generator() -> AsyncIterator[bytes]:
            async for chunk in resource:
                yield b"data: " + chunk + b"\n\n"

        async def _close_stream():
            await resource.close()

        return StreamingResponse(
            _event_generator(),
            media_type="text/event-stream",
            headers={ "Cache-Control": "no-cache" },
            background=BackgroundTask(_close_stream)
        )

    def _render_stream_resource(self, resource: StreamResource) -> Response:
        async def _close_stream():
            await resource.close() 

        return StreamingResponse(
            resource,
            media_type=resource.content_type, 
            headers=self._build_stream_resource_headers(resource), 
            background=BackgroundTask(_close_stream)
        )

    def _build_stream_resource_headers(self, resource: StreamResource) -> Dict[str, str]:
        headers: Dict[str, str] = { "Cache-Control": "no-cache" }

        if resource.filename:
            filename = resource.filename.replace('"', '\\"')
            headers["Content-Disposition"] = f'attachment; filename="{filename}"'

        return headers
