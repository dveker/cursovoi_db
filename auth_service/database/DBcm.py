from pymysql import connect  # объект соединения с БД
from pymysql.err import OperationalError  # информация об ошибках


class DBContextManager:
    def __init__(self, db_connect: dict):  # Инициализация
        self.conn = None
        self.cursor = None
        self.db_connect = db_connect

    def __enter__(self):
        try:
            self.conn = connect(**self.db_connect)
            self.cursor = self.conn.cursor()
            self.conn.begin()  # Обозначение начала транзакции
            return self.cursor
        except OperationalError as err:
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(exc_type)
            print(exc_val)
        if self.cursor:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.cursor.close()  # Зачистка курсора
            self.conn.close()  # Зачистка подключения
        return True
