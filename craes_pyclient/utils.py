import csv
import asyncio
import capnp
import websockets

# Absolute location of CRAES protocol. Necessary to work with Poetry.
from pathlib import Path
MODULE_DIRECTORY = Path(__file__).parents[0]
CRAES_PROTOCOL_PATH = str(MODULE_DIRECTORY.joinpath("protocol.capnp"))

# Load CRAES communication protocol
capnp.remove_import_hook()
protocol_capnp = capnp.load(CRAES_PROTOCOL_PATH)


async def send_orders(server_url, server_port, user_name, passphrase, parsed_orders):
    """Connects to CRAES, submits parsed orders and expects results."""
    uri = "ws://{}:{}".format(server_url, server_port)
    answers = list()
    async with websockets.connect(uri, extra_headers={"User": user_name,
                                                      "Password": passphrase}) as websocket:
        for order in parsed_orders:
            await websocket.send(order)
            answers.append(await websocket.recv())

    return answers


def deserialize_trades(trades_binary):
    """Deserializes response from CRAES and builds tuples of trades."""
    trades = list()
    for trade_response in trades_binary:
        executed_by_order = list()
        for trade in protocol_capnp.ResponseMsg.from_bytes(trade_response).executedtrades:
            executed_by_order.append((trade.price, trade.volume))
        trades.append(executed_by_order)

    return trades


def serialze_order(buy, volume, limitprice, condition, triggerprice, asset):
    """Parses order information into new serialized byte array."""
    new_order = protocol_capnp.OrderMsg.new_message()

    new_order.buy = buy
    new_order.volume = int(volume)

    if limitprice is None:
        new_order.limitprice.none = None
    else:
        try:
            new_order.limitprice.some = float(limitprice)
        except:
            raise ValueError("Limit price is not a valid float")

    if condition is None:
        new_order.condition.unconditional = None
    else:
        try:
            if condition == "stoploss":
                new_order.condition.stoploss = float(triggerprice)
            elif condition == "stopandreverse":
                new_order.condition.stopandreverse = float(triggerprice)
            else:
                raise ValueError("Unknown order condition")
        except:
            raise ValueError("Condition setup failed")

    new_order.assetname = asset

    return new_order.to_bytes()


def read_and_serialize_file(file):
    """Reads the provided CSV file, parses it and converts the orders to byte arrays
    ready to be sent.

    This function assumes orders to be present as lines in the form
        "buy,volume,limitprice,condition,triggerprice,asset\n"
    where:
        buy:            bool
        volume:         int (positive)
        limitprice:     float (positive) OR None
        condition:      str OR None
        triggerprice:   float (positive) OR None
        asset:          int (positive)

    This function does not attempt to guess further and simply raises an exception
    if a line was invalid.

    EXAMPLE:
    Valid lines:
        "true,3,5.0,None,None,1"
        "false,10,1.0,stoploss,2.0,2"
    Invalid lines:
        "tuer,10,1.0, None,None,"
        "false,-1,1,-1,None,None,1"
    """
    orders_as_bytes = list()
    with open(file, newline='\n') as f:
        orderreader = csv.reader(f)
        for i, entry in enumerate(orderreader):
            try:
                if entry[0] == 'true':
                    buy = True
                elif entry[0] == 'false':
                    buy = False
                else:
                    raise ValueError("Invalid buy condition.")

                volume = int(entry[1])
                if volume < 1:
                    raise ValueError("Volume not positive.")

                if entry[2] == 'None':
                    limitprice = None
                else:
                    limitprice = float(entry[2])
                    if limitprice < 0:
                        raise ValueError("Limit price not positive.")

                if entry[3] == 'None':
                    condition = None
                elif entry[3] in ('stoploss', 'stopandreverse'):
                    condition = entry[3]
                else:
                    raise ValueError("Invalid buy condition.")

                if entry[4] == 'None':
                    triggerprice = None
                else:
                    triggerprice = float(entry[4])
                    if triggerprice < 0:
                        raise ValueError("Trigger price not positive.")

                asset_id = int(entry[5])
                if volume < 0:
                    raise ValueError("Invalid asset ID: not positive.")

                orders_as_bytes.append(serialze_order(buy, volume, limitprice,
                                                      condition, triggerprice, asset_id))

            except:
                raise IOError("Error in CSV file, line {}".format(i+1))

    return orders_as_bytes
