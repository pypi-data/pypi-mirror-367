import io
from typing import NoReturn


class BaseEditor:
    """
    Базовый класс для создания отчетов.
    """
    def __init__(self, file_name: str = None):
        self.output = io.BytesIO()
        self.file_name = file_name
        #: Workbook
        self.book = None

    @staticmethod
    def get_search_text(search_text):
        """
        Статический метод для формирования текста поиска (ключа) на основе переданного текста.
        :param search_text: Текст, на основе которого формируется ключ для поиска.
        :return: Строка, представляющая ключ для поиска.
        """
        return '${' + search_text + '}'

    def get_filepath(self):
        """
        Метод для получения рабочей книги (workbook) класса.
        :return: Рабочая книга (workbook).
        """
        return self.file_name

    def save(self, new_file_name=None) -> NoReturn:
        """
        Метод для сохранения Excel-файла с новым именем (если указано) или перезаписи текущего.
        :param new_file_name: Новое имя файла (по умолчанию перезапись текущего файла).
        """
        self.file_name = new_file_name if new_file_name else self.file_name
        self.book.save(self.file_name)
