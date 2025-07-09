from binance.client import Client
from binance.enums import *
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import print
import logging
import sys

# --- Logging Configuration ---
logging.basicConfig(filename='bot.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

console = Console()

class SpotBot:
    def __init__(self, api_key, api_secret, testnet=True):
        try:
            self.client = Client(api_key, api_secret)
            if testnet:
                self.client.API_URL = 'https://testnet.binance.vision/api'

            # Test account connection
            account_info = self.client.get_account()
            console.print("[bold green]✅ Connected to Binance Spot Testnet[/bold green]")
            logging.info("Connected to Binance Spot Testnet.")

        except Exception as e:
            console.print(f"[bold red]❌ Connection failed: {e}[/bold red]")
            logging.error(f"Connection failed: {e}")
            sys.exit()

    def place_order(self, symbol, side, order_type, quantity, price=None):
        try:
            logging.info(f"Placing {order_type} {side} order on {symbol}, qty={quantity}, price={price}")
            if order_type == "MARKET":
                order = self.client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity
                )
            elif order_type == "LIMIT":
                order = self.client.create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    price=price
                )
            else:
                raise ValueError("Only MARKET and LIMIT orders are supported on Spot Testnet.")

            logging.info(f"✅ Order placed: {order}")
            console.print(f"[bold cyan]✅ Order Placed[/bold cyan]: {order['symbol']} | {order['side']} | {order['type']} | Qty: {order['origQty']}")
            return order

        except Exception as e:
            logging.error(f"❌ Order failed: {e}")
            console.print(f"[bold red]❌ Order failed: {e}[/bold red]")
            return None

# --- CLI Menu ---
def main():
    console.rule("[bold yellow]Binance Spot Testnet Trading Bot")

    api_key = Prompt.ask("[bold blue]Enter API Key")
    api_secret = Prompt.ask("[bold blue]Enter API Secret", password=True)

    bot = SpotBot(api_key, api_secret)

    while True:
        console.rule("[green]New Order")
        symbol = Prompt.ask("Enter trading pair", default="BTCUSDT").upper()
        side = Prompt.ask("Enter side", choices=["BUY", "SELL"], default="BUY").upper()
        order_type = Prompt.ask("Order type", choices=["MARKET", "LIMIT"], default="MARKET")
        quantity = float(Prompt.ask("Enter quantity"))

        price = None
        if order_type == "LIMIT":
            price = round(float(Prompt.ask("Enter LIMIT price")), 2)

        table = Table(title="Order Summary")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Symbol", symbol)
        table.add_row("Side", side)
        table.add_row("Order Type", order_type)
        table.add_row("Quantity", str(quantity))
        if price:
            table.add_row("Price", str(price))
        console.print(table)

        confirm = Prompt.ask("[bold yellow]Confirm order? (y/n)", choices=["y", "n"], default="y")
        if confirm == 'y':
            bot.place_order(symbol, side, order_type, quantity, price)
        else:
            console.print("[red]❌ Order canceled.[/red]")

        again = Prompt.ask("Place another order? (y/n)", choices=["y", "n"], default="y")
        if again != 'y':
            console.print("[bold green]👋 Exiting bot. Goodbye![/bold green]")
            logging.info("Bot session ended.")
            break

if __name__ == "__main__":
    main()
