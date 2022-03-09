import asyncio
from datetime import datetime
import pprint
from sys import exit
from time import time
import requests
import uvicorn
from fastapi import FastAPI, Request
from httpx import AsyncClient
from pyngrok import ngrok
from fastapi_utils.tasks import repeat_every
from DB_SQLAlchemy import my_DB
from validations import MessageBodyModel, ResponseToMessage

TOKEN = "5141013666:AAFDkri_oHLhSxP5fbu0qFEAgm_BDwZ2Hn4"
TELEGRAM_SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
TELEGRAM_SET_WEBHOOK_URL = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
HOST_URL = None
LAST_MESSAGE = "/start"
TM = datetime.now().minute
TIMER = 30

# https://github.com/FarukOzderim/Telegram-Bot-Python-FastAPI


app = FastAPI()
db = my_DB()

if TOKEN == "":
    exit("No secret found, exiting now!")


def gather_tasks(res):
    s = ""
    for x in res:
        s = s + f"№{x.number}: {x.task} " \
                f"\n{x.date[:19]} \n\n"
    d = {"text": f"{s}",
         "chat_id": 427305163}
    return d


@app.on_event("startup")
@repeat_every(seconds=TIMER)
async def show_again():
    try:
        res = await db.get_from_db()
        if res:
            my_dict = gather_tasks(res)
            requests.post(TELEGRAM_SEND_MESSAGE_URL, json=my_dict)
    except Exception as e:
        print(e)


@app.post("/webhook/{TOKEN}")
async def post_process_telegram_update(message: MessageBodyModel, request: Request):
    """Чуть чуть адаптированная функция"""
    global LAST_MESSAGE
    try:
        my_dict = None
        mes = message.message.text
        if mes.startswith("/"):
            if mes == "/add":
                my_dict = {"text": "Пожалуйста напишите что вы собираетесь сделать",
                           "chat_id": message.message.chat.id}

            elif mes == "/delete":
                my_dict = {"text": "Пожалуйста напишите что вы уже сделали",
                           "chat_id": message.message.chat.id}

            elif mes == "/show":
                res = await db.get_from_db()
                my_dict = gather_tasks(res)

            elif mes == "/start":
                my_dict = {"text": "Добрый день!",
                           "chat_id": message.message.chat.id}

            # elif mes == "/timer":
            #     my_dict = {"text": "Какой таймер вы хотите поставить?",
            #                "chat_id": message.message.chat.id}

            elif mes == "/menu":
                my_dict = {
                    "text": "/add : Добавить новое задание\n/delete : Стереть задание\n/show : Показать весь cписок",
                    "chat_id": message.message.chat.id}

        elif LAST_MESSAGE.startswith("/"):
            if LAST_MESSAGE == "/add":
                await db.insert_into_db(mes)
                my_dict = {"text": "Добавлено!",
                           "chat_id": message.message.chat.id}
                await db.update_num()

            elif LAST_MESSAGE == "/delete":
                await db.delete_from_db(mes)
                my_dict = {"text": "Удалено!", "chat_id": message.message.chat.id}
                await db.update_num()


            # elif LAST_MESSAGE == "/timer":
            #     try:
            #         TIMER = int(mes)
            #         my_dict = {"text": "Изменено!", "chat_id": message.message.chat.id}
            #         await show_again()
            #     except:
            #         raise Exception

        if my_dict is None:
            raise Exception


    except Exception as e:
        print(e)
        my_dict = {"text": "Извините, но вы что-то не так ввели!", "chat_id": message.message.chat.id}

    finally:
        js = ResponseToMessage(**my_dict)
        LAST_MESSAGE = mes
        return js


async def request(url: str, payload: dict, debug: bool = False):
    """ПОЛНОСТЬЮ СКОПИРОВАННАЯ ФУНКЦИЯ"""
    async with AsyncClient() as client:
        request = await client.post(url, json=payload)
        if debug:
            print(request.json())
        return request


# async def send_a_message_to_user(telegram_id: int, message: str) -> bool:
#     message = ResponseToMessage(
#         **{
#             "text": message,
#             "chat_id": telegram_id,
#         }
#     )
#     req = await request(TELEGRAM_SEND_MESSAGE_URL, message.dict())
#     return req.status_code == 200


async def set_telegram_webhook_url() -> bool:
    """ПОЛНОСТЬЮ СКОПИРОВАННАЯ ФУНКЦИЯ"""
    payload = {"url": f"{HOST_URL}/webhook/{TOKEN}"}
    req = await request(TELEGRAM_SET_WEBHOOK_URL, payload)
    return req.status_code == 200


if __name__ == "__main__":
    PORT = 8000
    http_tunnel = ngrok.connect(PORT, bind_tls=True)
    public_url = http_tunnel.public_url
    HOST_URL = public_url

    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(set_telegram_webhook_url())
    if success:
        uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="info")
    else:
        print("Fail, closing the app.")
