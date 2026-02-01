import os


class SQLProvider:

    def __init__(self, file_path):
        self.scripts = {}  # инициализируем пустой словарь
        for file in os.listdir(file_path):  # цикл по всем файлам во входной директории
            _sql = open(f'{file_path}/{file}').read()
            self.scripts[file] = _sql

    def get(self, file):  # достал sql запрос и вернул его
        _sql = self.scripts[file]
        return _sql
