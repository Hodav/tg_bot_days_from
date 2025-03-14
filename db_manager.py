import sqlite3


class DBManager:
    @classmethod
    def create(cls, chat_id, event_name, date):
        sql = '''
        insert into users (chat_id, event_name, event_dates) values (?, ?, ?)
        '''

        cls.execute(sql, chat_id, event_name, str(date))

    @classmethod
    def read(cls, chat_id):
        sql = '''
        select chat_id, event_name, event_dates from users where chat_id = ?
        '''
        data = cls.execute(sql, chat_id)
        if data:
            return data[0]
        return None

    @classmethod
    def read_all(cls):
        sql = '''
        select chat_id, event_name, event_dates from users
        '''
        data = cls.execute(sql)
        return data

    @classmethod
    def update(cls, chat_id, event_name, event_dates):
        sql = '''
        update users set event_name = ?, event_dates = ? where chat_id = ?
        '''
        cls.execute(sql, event_name, str(event_dates), chat_id)

    @classmethod
    def delete(cls, chat_id):
        sql = '''
        delete from users where chat_id = ?
        '''
        cls.execute(sql, chat_id)

    @classmethod
    def execute(cls, sql, *args):

        connection = sqlite3.connect('bd_bot_days_from')
        cursor = connection.cursor()
        try:
            cursor.execute(sql, args)
            data = cursor.fetchall()
            connection.commit()
        finally:
            connection.close()
        return data

    @classmethod
    def create_table(cursor):
        cursor.execute('''
        create table if not exists users (
        id integer primary key,
        chat_id integer not null unique,
        event_name text not null,
        event_dates text)
        ''')


if __name__ == '__main__':
    DBManager.create_table()