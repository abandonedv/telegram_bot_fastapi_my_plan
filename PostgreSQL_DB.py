import datetime

import psycopg2
from config import user, host, password, db_name


class DB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name)
        self.cur = self.conn.cursor()

    async def check_table_DB(self, table):
        self.cur.execute("""SELECT exists (SELECT *
           FROM information_schema.tables
           WHERE table_name = 'table_name' 
             AND table_schema = 'public') AS table_exists;""")

    async def create_DB(self):
        self.cur.execute(
            """CREATE TABLE public.messages(
                number serial PRIMARY KEY,
                task varchar(50),
                date varchar(50));"""
        )

        self.conn.commit()

    async def insert_into_db(self, tsk):
        dt = datetime.datetime.now()
        self.cur.execute(f"INSERT INTO public.messages(task, date) VALUES ('{tsk}', '{dt}');")
        self.conn.commit()

    async def get_from_db(self):
        self.cur.execute("SELECT * FROM public.messages;")
        return self.cur.fetchall()

    async def delete_from_db(self, num):
        nm = str(num)
        self.cur.execute("DELETE FROM public.messages WHERE CAST(number AS TEXT) LIKE (%s);", (nm,))
        self.conn.commit()

    async def update_num(self):
        i = 1
        self.cur.execute("SELECT * FROM public.messages;")
        res = self.cur.fetchall()
        ids = []
        for x in res:
            ids.append(x[0])
        print(ids)
        for x in range(len(ids)):
            self.cur.execute(f"UPDATE public.messages SET number = '{i}' WHERE CAST(number AS TEXT) LIKE (%s);", (str(ids[x]),))
            i += 1
        self.conn.commit()


