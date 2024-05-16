import sqlite3

DATABASE_NAME = 'database.sqlite'


def execute_query(sql_query, data=None, db_path=f'{DATABASE_NAME}'):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)

    connection.commit()
    connection.close()


# Функция для выполнения любого sql-запроса для получения данных (возвращает значение)
def execute_selection_query(sql_query, data=None, db_path=f'{DATABASE_NAME}'):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    connection.close()
    return rows


# Функция для создания новой таблицы (если такой ещё нет)
# Получает название
# Создаёт запрос CREATE TABLE IF NOT EXISTS имя_таблицы (колонка1 ТИП, колонка2 ТИП)
def create_users_table():
    sql_query = f'CREATE TABLE IF NOT EXISTS users ' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INT, ' \
                f'sessions INT, ' \
                f'tokens_used INT, ' \
                f'blocks_used INT, ' \
                f'symbols_used INT);'
    execute_query(sql_query)


# Функция для создания таблицы где будут храниться все его сообщения
def create_users_content_table():
    sql_query = f'CREATE TABLE IF NOT EXISTS users_content' \
                f'(id INTEGER PRIMARY KEY, ' \
                f'user_id INT, ' \
                f'role TEXT, ' \
                f'content TEXT);'
    execute_query(sql_query)


# Функция для вставки новой строки в таблицу
# Принимает список значений для каждой колонки и названия колонок
# Создаёт запрос INSERT INTO имя_таблицы (колонка1, колонка2) VALUES (?, ?)[значение1, значение2]
def insert_row_users(values):
    sql = f'INSERT INTO users (user_id, sessions, tokens_used, blocks_used, symbols_used) VALUES (?, ?, ?, ?, ?);'
    execute_query(sql, values)


def insert_row_users_content(values):
    sql = f'INSERT INTO users_content (user_id, role, content) VALUES (?, ?, ?);'
    execute_query(sql, values)


# Обновить значение в указанной строке и колонки
def update_row_value(user_id, column_name, new_value):
    sql = f'UPDATE users SET {column_name}={new_value} WHERE user_id={user_id};'
    execute_query(sql)


# Функция для получения данных для указанного пользователя
def get_data_for_user(user_id):
    sql = f"SELECT * FROM users WHERE user_id={user_id};"
    return execute_selection_query(sql)

def get_data(table_name):
    sql = f"SELECT * FROM {table_name};"
    return execute_selection_query(sql)

def delete_row_value(user_id):
    sql = f'DELETE FROM users WHERE user_id = {user_id};'
    execute_query(sql)