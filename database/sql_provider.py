import os

class SQLProvider:

    def __init__(self, file_path):
        self.scripts = {}
        for file in os.listdir(file_path):
            with open(f'{file_path}/{file}', 'r', encoding='utf-8') as f:
                _sql = f.read()
            self.scripts[file] = _sql

    def get(self, file):
        _sql = self.scripts[file]
        return _sql