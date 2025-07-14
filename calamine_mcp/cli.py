# -*- coding: utf-8 -*-
"""
Модуль Command Line Interface (CLI).

Использует Typer для создания удобного интерфейса командной строки
для запуска сервера.
"""
import asyncio
import os

import typer

from .server import CalamineMcpServer

# Создаем приложение Typer
app = typer.Typer()

@app.command()
def sse():
    """
    Запускает MCP сервер в режиме Server-Sent Events (SSE).

    Параметры хоста, порта и пути к файлам берутся из переменных окружения:
    - FASTMCP_HOST (по умолчанию '0.0.0.0')
    - FASTMCP_PORT (по умолчанию 8000)
    - EXCEL_FILES_PATH (по умолчанию './excel_files')
    """
    host = os.getenv("FASTMCP_HOST", "0.0.0.0")
    port = int(os.getenv("FASTMCP_PORT", 8000))
    excel_path = os.getenv("EXCEL_FILES_PATH", "./excel_files")

    typer.echo(f"Запуск SSE сервера на {host}:{port}")
    typer.echo(f"Директория с файлами: {excel_path}")

    server = CalamineMcpServer(excel_files_path=excel_path)
    
    # Запускаем асинхронный метод run_sse
    asyncio.run(server.run_sse(host=host, port=port))


if __name__ == "__main__":
    app()
