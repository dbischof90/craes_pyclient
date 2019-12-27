import asyncio
import click

from .utils import send_orders, deserialize_trades, read_and_serialize_file, MODULE_DIRECTORY


@click.command()
@click.option("--server_addr", default="127.0.0.1", help="Address CRAES is listening on")
@click.option("--server_port", default=8080, help="Port CRAES is listening on")
@click.option("--user_name", default="test_user", help="User name to authentificate with")
@click.option("--passphrase", default="password", help="Passphrase to authentificate with")
@click.option("--file", default=str(MODULE_DIRECTORY.joinpath("orders.csv")), help="CSV file with orders to be sent")
def run_client(server_addr, server_port, user_name, passphrase, file):
    print("Loading order file.")
    orders_as_bytes = read_and_serialize_file(file)
    print("Read {} orders successfully. Connect to CRAES.".format(
        len(orders_as_bytes)))

    response = asyncio.get_event_loop()\
                      .run_until_complete(send_orders(server_addr, server_port,
                                                      user_name, passphrase, orders_as_bytes))
    parsed_response = deserialize_trades(response)
    print("Orders sent. Responses:")
    print(parsed_response)
