# -*- coding: utf-8 -*-
"""
Основной модуль MCP-сервера.

Определяет класс CalamineMcpServer, который обрабатывает запросы
от клиентов через fastmcp.
"""
import logging
import os
from typing import Any, Dict, List

# fastmcp recently changed its public API, moving the main classes
# under the ``server`` submodule.  To remain compatible with both the
# old and the new versions we attempt the old style import first and
# fall back to the new location if needed.
try:  # pragma: no cover - import paths depend on installed version
    from fastmcp import Mcp, Mq
except ImportError:  # pragma: no cover - for new fastmcp versions
    from fastmcp.server import Mcp, Mq

from .workbook import Workbook

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CalamineMcpServer:
    """
    MCP-сервер для обработки запросов на чтение Excel-файлов.
    """

    def __init__(self, excel_files_path: str):
        """
        Инициализация сервера.

        Args:
            excel_files_path (str): Базовый путь к директории с Excel-файлами.
        """
        if not os.path.isdir(excel_files_path):
            logger.warning(
                f"Директория для Excel файлов не найдена: {excel_files_path}. "
                f"Пожалуйста, убедитесь, что volume смонтирован правильно."
            )
            # Создаем директорию, если ее нет, чтобы избежать ошибок при запуске
            os.makedirs(excel_files_path, exist_ok=True)
            
        self.excel_files_path = excel_files_path
        self.mcp = Mcp(self, "excel_mcp")

    def _get_full_path(self, filename: str) -> str:
        """
        Формирует полный путь к файлу, предотвращая выход за пределы рабочей директории.
        """
        # os.path.normpath для удаления '..' и других относительных путей
        base_path = os.path.abspath(self.excel_files_path)
        # Убираем начальные слэши, чтобы join работал корректно
        safe_filename = os.path.normpath(filename.lstrip('/\\'))
        full_path = os.path.join(base_path, safe_filename)

        # Проверка, что путь не выходит за пределы разрешенной директории
        if not full_path.startswith(base_path):
            raise PermissionError("Доступ за пределы рабочей директории запрещен.")
            
        return full_path

    @Mcp.handler
    async def get_sheet_names(self, mq: Mq, filename: str) -> List[str]:
        """
        Возвращает список имен листов в указанном файле.

        Args:
            filename (str): Имя файла (относительно EXCEL_FILES_PATH).

        Returns:
            List[str]: Список имен листов.
        """
        logger.info(f"Запрос get_sheet_names для файла: {filename}")
        try:
            full_path = self._get_full_path(filename)
            wb = Workbook(full_path)
            return wb.sheet_names
        except Exception as e:
            logger.error(f"Ошибка при получении имен листов для '{filename}': {e}", exc_info=True)
            # Возвращаем ошибку клиенту
            return Mq.error(str(e))

    @Mcp.handler
    async def get_cell(self, mq: Mq, filename: str, sheet_name: str, row: int, col: int) -> Any:
        """
        Возвращает значение ячейки.

        Args:
            filename (str): Имя файла.
            sheet_name (str): Имя листа.
            row (int): Номер строки (1-индексация).
            col (int): Номер колонки (1-индексация).

        Returns:
            Any: Значение ячейки.
        """
        logger.info(f"Запрос get_cell для {filename} -> {sheet_name} [{row}, {col}]")
        try:
            full_path = self._get_full_path(filename)
            wb = Workbook(full_path)
            return wb.get_cell_value(sheet_name, row, col)
        except Exception as e:
            logger.error(f"Ошибка в get_cell для '{filename}': {e}", exc_info=True)
            return Mq.error(str(e))

    @Mcp.handler
    async def get_all_rows(self, mq: Mq, filename: str, sheet_name: str) -> List[List[Any]]:
        """
        Возвращает все строки с данными листа.

        Args:
            filename (str): Имя файла.
            sheet_name (str): Имя листа.

        Returns:
            List[List[Any]]: Двумерный список со значениями.
        """
        logger.info(f"Запрос get_all_rows для {filename} -> {sheet_name}")
        try:
            full_path = self._get_full_path(filename)
            wb = Workbook(full_path)
            return wb.get_all_rows(sheet_name)
        except Exception as e:
            logger.error(f"Ошибка в get_all_rows для '{filename}': {e}", exc_info=True)
            return Mq.error(str(e))

    @Mcp.handler
    async def get_file_metadata(self, mq: Mq, filename: str) -> Dict[str, Any]:
        """
        Возвращает метаданные о файле.

        Args:
            filename (str): Имя файла.

        Returns:
            Dict[str, Any]: Словарь с метаданными (размер, дата изменения).
        """
        logger.info(f"Запрос get_file_metadata для файла: {filename}")
        try:
            full_path = self._get_full_path(filename)
            if not os.path.exists(full_path):
                 raise FileNotFoundError(f"Файл не найден: {full_path}")
            
            stat = os.stat(full_path)
            return {
                "size": stat.st_size,
                "modified_at": stat.st_mtime,
                "is_readonly": True # Явно указываем, что сервер read-only
            }
        except Exception as e:
            logger.error(f"Ошибка в get_file_metadata для '{filename}': {e}", exc_info=True)
            return Mq.error(str(e))

    async def run_sse(self, host: str, port: int):
        """Запускает сервер в режиме Server-Sent Events."""
        logger.info(f"Запуск Calamine MCP сервера в режиме SSE на {host}:{port}")
        logger.info(f"Путь к файлам Excel: {self.excel_files_path}")
        await self.mcp.run_sse(host=host, port=port)

