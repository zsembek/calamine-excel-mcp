# -*- coding: utf-8 -*-
"""
Модуль для работы с Excel-файлами с использованием python-calamine.

Этот модуль предоставляет класс Workbook, который является оберткой над
python-calamine для чтения данных из файлов .xlsx, .xls, .ods.

Важно: python-calamine - это библиотека только для чтения.
Любые операции по изменению файлов не поддерживаются.
"""
import os
import threading
from typing import Any, Dict, List, Optional

from python_calamine import CalamineWorkbook

# Кэш для хранения открытых экземпляров книг.
# Это предотвращает повторное чтение одного и того же файла с диска при каждом запросе.
# Ключ - полный путь к файлу, значение - экземпляр CalamineWorkbook.
_WORKBOOKS_CACHE: Dict[str, CalamineWorkbook] = {}
# Блокировка для обеспечения потокобезопасности при доступе к кэшу.
_CACHE_LOCK = threading.Lock()


class Workbook:
    """
    Класс для чтения данных из Excel-файла с помощью python-calamine.
    Обеспечивает кэширование открытых файлов для повышения производительности.
    """

    def __init__(self, file_path: str):
        """
        Инициализирует экземпляр Workbook.

        Args:
            file_path (str): Полный путь к Excel-файлу.

        Raises:
            FileNotFoundError: Если файл по указанному пути не найден.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден по пути: {file_path}")

        self.file_path = file_path
        self._workbook = self._get_or_load_workbook()

    def _get_or_load_workbook(self) -> CalamineWorkbook:
        """
        Получает экземпляр CalamineWorkbook из кэша или загружает его с диска.
        Метод является потокобезопасным.
        """
        with _CACHE_LOCK:
            if self.file_path in _WORKBOOKS_CACHE:
                return _WORKBOOKS_CACHE[self.file_path]
            
            # Если в кэше нет, загружаем и сохраняем
            workbook = CalamineWorkbook.from_path(self.file_path)
            _WORKBOOKS_CACHE[self.file_path] = workbook
            return workbook

    @property
    def sheet_names(self) -> List[str]:
        """
        Возвращает список имен всех листов в книге.

        Returns:
            List[str]: Список имен листов.
        """
        return self._workbook.sheet_names

    def get_sheet_by_name(self, name: str):
        """
        Возвращает объект листа по его имени.

        Args:
            name (str): Имя листа.

        Returns:
            Объект листа из python-calamine.
        
        Raises:
            KeyError: Если лист с таким именем не найден.
        """
        if name not in self.sheet_names:
            raise KeyError(f"Лист с именем '{name}' не найден в файле '{self.file_path}'")
        return self._workbook.get_sheet_by_name(name)

    def get_cell_value(self, sheet_name: str, row: int, col: int) -> Any:
        """
        Получает значение ячейки по имени листа и координатам (1-индексация).

        Args:
            sheet_name (str): Имя листа.
            row (int): Номер строки (начиная с 1).
            col (int): Номер колонки (начиная с 1).

        Returns:
            Any: Значение ячейки. Может быть str, int, float, bool, datetime.
        """
        sheet = self.get_sheet_by_name(sheet_name)
        # python-calamine использует 0-индексацию, поэтому вычитаем 1
        cell = sheet.get_cell((row - 1, col - 1))
        return cell.value if cell else None

    def get_all_rows(self, sheet_name: str, include_empty_rows: bool = False) -> List[List[Any]]:
        """
        Получает все строки с данными на листе в виде списка списков.

        Args:
            sheet_name (str): Имя листа.
            include_empty_rows (bool): Включать ли пустые строки в результат.

        Returns:
            List[List[Any]]: Двумерный список со значениями ячеек.
        """
        sheet = self.get_sheet_by_name(sheet_name)
        # Метод to_python() возвращает данные в удобном формате
        return sheet.to_python(skip_empty_rows=not include_empty_rows)

    # --- Операции записи (Set/Write) не реализованы, ---
    # --- так как python-calamine является read-only. ---
    # --- Если в будущем потребуется запись, нужно будет ---
    # --- выбрать другую библиотеку (например, openpyxl или xlsxwriter) ---
    # --- и добавить соответствующие методы. ---

