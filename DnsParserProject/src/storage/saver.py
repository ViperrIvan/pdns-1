import pandas as pd
import sqlite3
from abc import abstractmethod
from typing import List, Dict, Any


class DataSaver:
    @classmethod
    @abstractmethod
    def save_data(cls, params_dict, file_name):
        pass


class ExcelDataSaver(DataSaver):
    @classmethod
    def save_data(cls, params_dict, file_name):
        if not params_dict:
            print(f"Нет данных для сохранения в {file_name}")
            return

        df = pd.DataFrame(params_dict)
        df.to_excel(f'{file_name}.xlsx', index=False)
        print(f"Данные успешно сохранены в {file_name}.xlsx")


class SQLDataSaver(DataSaver):
    @classmethod
    def save_data(cls, params_dict, table_name):
        if not params_dict:
            print(f"Нет данных для сохранения в таблицу {table_name}")
            return

        conn = sqlite3.connect(r'C:\Users\user\PycharmProjects\ComplectPC\ComplectPC\db.sqlite3', uri=True)
        cursor = conn.cursor()

        # Получаем все уникальные ключи из всех словарей
        all_keys = set()
        for d in params_dict:
            if d:
                all_keys.update(d.keys())

        if not all_keys:
            print("Нет валидных ключей для создания таблицы")
            return

        columns = list(all_keys)
        safe_table_name = f'"{table_name}"'
        safe_columns = [f'"{col}" TEXT' for col in columns]

        # Создаем таблицу
        create_query = f"""
            CREATE TABLE IF NOT EXISTS {safe_table_name} (
                {', '.join(safe_columns)}
            )
        """

        try:
            cursor.execute(create_query)

            # Вставляем данные
            for d in params_dict:
                if not d:
                    continue

                placeholders = ', '.join(['?'] * len(columns))
                values = [str(d.get(col, '')) for col in columns]
                insert_query = f"""
                    INSERT INTO {safe_table_name} ({', '.join(f'"{col}"' for col in columns)})
                    VALUES ({placeholders})
                """
                cursor.execute(insert_query, values)

            conn.commit()
            print(f"Данные успешно сохранены в таблицу {table_name}")

        except sqlite3.Error as e:
            print(f"Ошибка SQLite при работе с таблицей {table_name}: {e}")
            conn.rollback()
        finally:
            conn.close()

    @classmethod
    def clear_database(cls, db_file):
        """Удаляет все данные из всех таблиц, сохраняя структуру"""
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"DELETE FROM {table}")

        cursor.execute("VACUUM")
        conn.commit()
        conn.close()