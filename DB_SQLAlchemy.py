import datetime

from sqlalchemy import Integer, String
from sqlalchemy import create_engine, MetaData, Table, Column
from sqlalchemy import select, update


class my_DB:
    engine = create_engine('sqlite:///tasks.db', future=True)
    metadata = MetaData()
    conn = engine.connect()

    messages = Table('tasks', metadata,
                     Column('number', Integer, primary_key=True),
                     Column('task', String(50)),
                     Column('date', String(50)),
                     )

    async def insert_into_db(self, task: str):
        try:
            with self.engine.begin() as bd:
                obj = {"task": f"{task}",
                       "date": f"{datetime.datetime.now()}"}
                bd.execute(self.messages.insert(), obj)
        except Exception as e:
            print(e)

    async def get_from_db(self):
        try:
            with self.engine.begin() as bd:
                r = bd.execute(select(self.messages))
                res = r.fetchall()

                return res
        except Exception as e:
            print(e)

    async def delete_from_db(self, numb):
        try:
            with self.engine.begin() as bd:
                bd.execute(self.messages.delete().
                           where(self.messages.c.number == f"{numb}"))
        except Exception as e:
            print(e)

    async def update_num(self):
        try:
            i = 1
            with self.engine.begin() as bd:
                r = bd.execute(select(self.messages))
                res = r.fetchall()
                ids = []
                for x in res:
                    ids.append(x.number)
                print(ids)
                for x in range(len(ids)):
                    bd.execute(self.messages.update().values(number=i).where(self.messages.c.number == ids[x]))
                    i += 1

        except Exception as e:
            print(e)
