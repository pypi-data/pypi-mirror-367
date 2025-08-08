import os
from typing import Union, Iterable

from django.conf import settings

from .base_provider import BaseProvider
from ..report_tools import ExcelEditor, WordEditor, change_extension, FileConverter
from .providers_config import provider_registration


@provider_registration()
class ProxyModelProvider(BaseProvider):
    """
    Класс для прокси моделей.
    Класс подставляет единичные значения
    """

    def _build_excel(self):
        report = ExcelEditor(self.file_name)
        report.replace_data(self.data)
        report.save()
        return report.get_filepath()

    def _build_word(self):
        report = WordEditor(self.file_name)
        report.docx_replace(**self.data)
        report.save()
        return report.get_filepath()

    def export(self):
        extension = os.path.basename(self.file_name).split('.')[-1]
        if extension in ['xlsx', 'xls']:
            return self._build_excel()
        elif extension in ['docx', 'doc']:
            return self._build_word()
        else:
            raise ValueError(f'Неподдерживаемое расширение файла: {extension}')


@provider_registration()
class ProxyPDFModelProvider(ProxyModelProvider):
    def __init__(self, data: Union[Iterable, dict], file_name: str):
        """
        Инициализатор класса.
        :param data: Данные для отчета.
        :param file_name: Путь к файлу.
        """
        super().__init__(data, file_name)

        converter_container_name = settings.CONVERTER_CONTAINER_NAME
        converter_container_port = settings.CONVERTER_CONTAINER_PORT

        if not converter_container_name or not converter_container_port:
            raise EnvironmentError('CONVERTER_CONTAINER_NAME и/или CONVERTER_CONTAINER_PORT отсутствуют в окружении.')

        self.converter_ip = f'http://{converter_container_name}:{converter_container_port}'

    def export(self):
        extension = os.path.basename(self.file_name).split('.')[-1]

        if extension in ['xlsx', 'xls']:
            excel_file_path = self._build_excel()
            pdf_file_path = FileConverter(excel_file_path, self.converter_ip) \
                .convert_to_pdf(change_extension(excel_file_path, 'pdf'))
            os.remove(excel_file_path)
            return pdf_file_path
        elif extension in ['docx', 'doc']:
            word_file_path = self._build_word()
            pdf_file_path = FileConverter(word_file_path, self.converter_ip) \
                .convert_to_pdf(change_extension(word_file_path, 'pdf'))
            os.remove(word_file_path)
            return pdf_file_path
        else:
            raise ValueError(f'Неподдерживаемое расширение файла: {extension}')


@provider_registration()
class TableProvider(BaseProvider):
    """
    Класс для отчетов с подстановкой таблиц в Excel шаблон.
    Шаблон отчета не должен содержать объединенные ячейки в таблицах.
    """
    def _build_excel(self):
        report = ExcelEditor(self.file_name)
        report.fill_data_from_startpoint(self.data)
        report.save()
        filepath = report.get_filepath()
        return filepath

    def export(self):
        return self._build_excel()


@provider_registration()
class MergedTableProvider(BaseProvider):
    """
    Класс для отчетов с подстановкой таблиц в Excel шаблон.
    Шаблон отчета может содержать объединенные ячейки,
    но формирование отчета будет медленнее.
    """
    def _build_excel(self):
        report = ExcelEditor(self.file_name)
        report.fill_data_from_startpoint_merged(self.data)
        report.save()
        filepath = report.get_filepath()
        return filepath

    def export(self):
        return self._build_excel()


@provider_registration()
class SingleMergedTableProvider(BaseProvider):
    """
    Класс для отчетов с подстановкой таблиц и подстановкой единичных значений в Excel шаблон.
    Шаблон отчета может содержать объединенные ячейки,
    но формирование отчета будет медленнее.
    """

    def _build_excel(self):
        report = ExcelEditor(self.file_name)
        # Подставляем значения
        report.replace_data(self.data['replace_data'])
        report.fill_data_from_startpoint_merged(self.data['table_data'])
        report.save()
        filepath = report.get_filepath()
        return filepath

    def export(self):
        return self._build_excel()


@provider_registration()
class TemplateProvider(BaseProvider):
    """
    Класс для отчетов с подставлением значений и подставлением таблиц в Excel шаблон.
    """
    def _build_excel(self):
        report = ExcelEditor(self.file_name)
        # Подставляем значения
        report.replace_data(self.data['replace_data'])
        # Подставляем таблицы
        report.fill_data_to_template(self.data['table_data'])
        report.save()
        filepath = report.get_filepath()
        return filepath

    def export(self):
        return self._build_excel()
