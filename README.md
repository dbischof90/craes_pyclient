# Python client for CRAES
## A simple static CLI

This project is a simple client example for CRAES, which can be found [here](https://www.github.com/dbischof90/craes "GitHub Link to repository"). It reads CSV files of arbitrary complexity, parses and sends them to a running CRAES instance and parses the response from the exchange.

## Installation and requirements
This project assumes **Python 3.7+**. This is not a hard requirement on the exchange side but comes from `asyncio`. The easiest way to use this client is by using `poetry` (see [here](https://python-poetry.org/)). Assuming you are using `poetry`, you can run the client with
```bash
git clone 
cd craes_pyclient
poetry install
poetry run client
```
In case you do not want to use `poetry`, install the packages listed in `pyproject.toml` under the entry `[tool.poetry.dependencies]`.

## Usage
The client provides a CLI:
```bash
$ poetry run client --help
Usage: client [OPTIONS]

Options:
  --server_addr TEXT     Address CRAES is listening on
  --server_port INTEGER  Port CRAES is listening on
  --user_name TEXT       User name to authentificate with
  --passphrase TEXT      Passphrase to authentificate with
  --file TEXT            CSV file with orders to be sent
  --help                 Show this message and exit.
```
All arguments have default values that point towards a local instance with the `test_user` setup, sending the order file `orders.csv` commited in the repository. 

For quick debugging and experimenting with the protocol, this package also provides a test server, which can be launched with `poetry run testserver`. This starts a WebSocket endpoint on the local machine which accepts orders, prints them to STDOUT and responds with an empty trade response.
