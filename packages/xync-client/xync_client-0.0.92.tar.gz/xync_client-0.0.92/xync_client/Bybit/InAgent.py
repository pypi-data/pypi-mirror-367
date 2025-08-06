import json
from asyncio import run

import websockets
from pyro_client.client.file import FileClient
from xync_client.Bybit.etype.order import StatusChange, CountDown, SellerCancelChange, Read, Receive, Status

from xync_client.loader import TOKEN
from xync_schema import models

from xync_client.Abc.InAgent import BaseInAgentClient
from xync_client.Bybit.agent import AgentClient


class InAgentClient(BaseInAgentClient):
    agent_client: AgentClient

    async def start_listen(self):
        t = await self.agent_client.ott()
        ts = int(float(t["time_now"]) * 1000)
        await self.ws_prv(self.agent_client.actor.agent.auth["deviceId"], t["result"], ts)

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    async def request_accepted_notify(self) -> int: ...  # id

    async def ws_prv(self, did: str, tok: str, ts: int):
        u = f"wss://ws2.bybit.com/private?appid=bybit&os=web&deviceid={did}&timestamp={ts}"
        async with websockets.connect(u) as websocket:
            auth_msg = json.dumps({"req_id": did, "op": "login", "args": [tok]})
            await websocket.send(auth_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["FIAT_OTC_TOPIC", "FIAT_OTC_ONLINE_TOPIC"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"SUPER_DEAL"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"OTC_ORDER_STATUS"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"WEB_THREE_SELL"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"APPEALED_CHANGE"}']})
            await websocket.send(sub_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order-eftd-complete-privilege-event"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order-savings-product-event"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.deal-core.order-savings-complete-event"]})
            await websocket.send(sub_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["FIAT_OTC_TOPIC", "FIAT_OTC_ONLINE_TOPIC"]})
            await websocket.send(sub_msg)

            while resp := await websocket.recv():
                if data := json.loads(resp):
                    match data.get("topic"):
                        case "OTC_ORDER_STATUS":
                            match data["type"]:
                                case "STATUS_CHANGE":
                                    upd = StatusChange.model_validate(data["data"])
                                    if upd.status == Status.ws:
                                        ...
                                case "COUNT_DOWN":
                                    upd = CountDown.model_validate(data["data"])
                                case _:
                                    self.listen(data)
                        case "OTC_USER_CHAT_MSG":
                            match data["type"]:
                                case "RECEIVE":
                                    upd = Receive.model_validate(data["data"])
                                case "READ":
                                    upd = Read.model_validate(data["data"])
                                case "CLEAR":
                                    pass
                                case _:
                                    self.listen(data)
                        case "OTC_USER_CHAT_MSG_V2":
                            pass
                        case "SELLER_CANCEL_CHANGE":
                            upd = SellerCancelChange.model_validate(data["data"])
                        case None:
                            if not data.get("success"):
                                self.listen(data)
                        case _:
                            self.listen(data)

    @staticmethod
    def listen(data: dict):
        print(data)


async def main():
    from x_model import init_db
    from xync_client.loader import TORM

    _ = await init_db(TORM, True)
    # pbot = PyroClient(bot)
    # await pbot.app.start()
    # await pbot.app.create_channel("tc")
    # await pbot.app.stop()

    actor = await models.Actor.filter(ex_id=9, agent__auth__isnull=False).prefetch_related("ex", "agent").first()
    async with FileClient(TOKEN) as b:
        cl: InAgentClient = actor.in_client(b)
        _ = await cl.start_listen()
        await cl.agent_client.close()


if __name__ == "__main__":
    run(main())
