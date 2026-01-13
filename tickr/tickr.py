import typer
import requests
import os
from typing_extensions import Annotated
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

load_dotenv()

app = typer.Typer(help="CLI to pull daily updates on any stock.")
console = Console()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

@app.command()
def info(
    name: Annotated[str, typer.Argument(help="Enter the ticker symbol.")], 
    force: Annotated[bool, typer.Option(help="Skip confirmation.")] = False
):
    """
    Retrieve INFO about any stock using corresponding ticker symbol.
    """
    if not force:
        confirmed = typer.confirm(f"Retrieve data for '{name}'?", default=True)
        if not confirmed:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
    
    try:
        with console.status(f"[bold green]Fetching data for {name}...", spinner="dots"):
            api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={name}&apikey={API_KEY}"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
    except requests.exceptions.RequestException as e:
        console.print(Panel(
            f"[bold red]API Error:[/bold red] {str(e)}", 
            title="Error", 
            border_style="red"
        ))
        return
    
    # Check if we got valid data
    if "Global Quote" not in data or not data["Global Quote"]:
        console.print(f"[bold red]No data found for '{name}'. Check the ticker symbol.[/bold red]")
        return
    
    quote = data["Global Quote"]
    
    # Create a beautiful table
    table = Table(title=f"{quote['01. symbol']} Stock Quote", box=box.ROUNDED)
    
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    # Determine if price is up or down
    change = float(quote['09. change'])
    change_color = "green" if change >= 0 else "red"
    change_symbol = "▲" if change >= 0 else "▼"
    
    table.add_row("Price", f"[bold]${float(quote['05. price']):.2f}[/bold]")
    table.add_row("Change", f"[{change_color}]{change_symbol} {quote['09. change']} ({quote['10. change percent']})[/{change_color}]")
    table.add_row("Open", f"${float(quote['02. open']):.2f}")
    table.add_row("High", f"${float(quote['03. high']):.2f}")
    table.add_row("Low", f"${float(quote['04. low']):.2f}")
    table.add_row("Volume", f"{int(quote['06. volume']):,}")
    table.add_row("Previous Close", f"${float(quote['08. previous close']):.2f}")
    table.add_row("Latest Trading Day", quote['07. latest trading day'])
    
    console.print(table)

@app.command()
def search(name: Annotated[str, typer.Argument(help="Enter the company name.")]):
    """
    SEARCH for ticker symbols by company name.
    """

    common_indices = {
        "s&p 500": ("SPY", "VOO", "IVV"),
        "dow jones": ("DIA",),
        "nasdaq": ("QQQ",),
        "russell 2000": ("IWM",)
    }

    search_name = name.lower()
    for index_name, tickers in common_indices.items():
        if index_name in search_name:
            console.print(f"[yellow] '{name.upper()}' is an index. Try these ETFs instead: [/yellow]" )
            for ticker in tickers:
                console.print(f" - [cyan]{ticker}[/cyan]")
    try:
        with console.status(f"[bold green]Searching for '{name}'...", spinner="dots"):
            api_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={name}&apikey={API_KEY}"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
    except requests.exceptions.RequestException as e:
        console.print(Panel(
            f"[bold red]API Error:[/bold red] {str(e)}", 
            title="Error", 
            border_style="red"
        ))
        return
    
    if "bestMatches" not in data or not data["bestMatches"]:
        console.print(f"[bold red]No results found for '{name}'[/bold red]")
        return
    
    top3 = data["bestMatches"][:3]
    
    # Create a table for search results
    table = Table(title=f"Search Results for '{name}'", box=box.ROUNDED)
    
    table.add_column("#", style="cyan", width=3)
    table.add_column("Symbol", style="green bold")
    table.add_column("Name", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Region", style="blue")
    
    for i, match in enumerate(top3, 1):
        table.add_row(
            str(i),
            match['1. symbol'],
            match['2. name'],
            match['3. type'],
            match['4. region']
        )
    
    console.print(table)

if __name__ == "__main__":
    app()