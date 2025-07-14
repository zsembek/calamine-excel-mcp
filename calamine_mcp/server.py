import logging
import os
import tempfile
import uuid

import calamine
from fastapi import FastAPI, UploadFile
from fastapi.responses import ORJSONResponse
from loguru import logger

# --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
# Правильный импорт с именами в верхнем регистре.
from fastmcp import MCP, MQ
# -------------------------

from .config import get_settings
from .models import Response, StatusEnum
from .services import ExcelService

# ... (остальная часть файла остается без изменений)
settings = get_settings()

if settings.debug:
    logger.add(
        os.path.join(settings.log_path, settings.log_file),
        level=settings.log_level,
        rotation="10 MB",
    )
else:
    logging.basicConfig(level=settings.log_level)


class CalamineMcpServer(MCP):

    def __init__(self, mq: MQ, excel_service: ExcelService, *args, **kwargs):
        super().__init__(mq, *args, **kwargs)
        self.excel_service = excel_service

    async def _on_startup(self):
        logger.info("Starting CalamineMcpServer")

    async def _on_shutdown(self):
        logger.info("Shutting down CalamineMcpServer")

    @MCP.handler(settings.excel_read_queue, auto_ack=True)
    async def excel_read_handler(self, file_path: str) -> dict:
        try:
            return self.excel_service.read_excel_file(file_path=file_path)
        except Exception as e:
            logger.error(f"Error reading excel file: {e}")
            return {"error": str(e)}


app = FastAPI(title="Calamine MCP Server", default_response_class=ORJSONResponse)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up CalamineMcpServer")
    app.state.excel_service = ExcelService(
        upload_path=settings.excel_files_path
    )
    # create upload path if not exists
    os.makedirs(settings.excel_files_path, exist_ok=True)

    app.state.mq = await MQ.create(
        settings.amqp_url,
        in_ram=settings.amqp_in_ram,
        no_ack=settings.amqp_no_ack,
        prefetch_count=settings.amqp_prefetch_count,
    )
    app.state.server = CalamineMcpServer(
        mq=app.state.mq,
        excel_service=app.state.excel_service,
    )
    await app.state.server.start()
    logger.info("CalamineMcpServer started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down CalamineMcpServer")
    await app.state.server.stop()
    await app.state.mq.close()
    logger.info("CalamineMcpServer stopped")


@app.get("/", response_model=Response)
async def root():
    return Response(status=StatusEnum.ok)


@app.post("/upload-excel", response_model=Response)
async def upload_excel(file: UploadFile):
    if not file.filename.endswith((".xlsx", ".xls")):
        return Response(
            status=StatusEnum.error, message="Invalid file type"
        )
    file_path = os.path.join(
        settings.excel_files_path, f"{uuid.uuid4()}_{file.filename}"
    )
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    await app.state.mq.publish(
        settings.excel_read_queue,
        file_path,
    )
    return Response(
        status=StatusEnum.ok, message="File uploaded successfully"
    )
