import asyncio
import websockets
import capnp
from .utils import CRAES_PROTOCOL_PATH


# Load CRAES communication protocol
capnp.remove_import_hook()
protocol_capnp = capnp.load(CRAES_PROTOCOL_PATH)


async def receive_and_log(websocket, path):
    async for message in websocket: 
        new_order = protocol_capnp.OrderMsg.from_bytes(message)
        print("Got {}".format(new_order))
        empty_response = protocol_capnp.ResponseMsg.new_message() 
        await websocket.send(empty_response.to_bytes())


def run_sink_server():
    print("Start WebSocket endpoint, listening for orders.")
    start_server = websockets.serve(receive_and_log, "localhost", 8080)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
