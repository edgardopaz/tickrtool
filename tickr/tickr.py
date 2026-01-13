import typer, requests, json, os
from typing_extensions import Annotated
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(help="CLI to pull daily updates on any stock.")
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


@app.command()
def info(name: Annotated[str, typer.Argument(help="Enter the ticker symbol.")], force: Annotated[bool, typer.Option(prompt="Have you entered a valid ticker symbol?", help="Force information retrieval without confirmation.")]):
    """
    Retrive INFO about any stock using corresponding ticker symbol.

    If --force is not used, will ask for confirmation.
    """
    if force:
        api_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={name}&apikey={API_KEY}"
        response = requests.get(api_url)
        data = response.json()
        formatted_json = json.dumps(data, indent=4)

        print(formatted_json)
    else:
        print("Operation cancelled.\nUse the 'search' command to find the correct symbol ticker.")

@app.command()
def search(name: Annotated[str, typer.Argument(help="Enter the company name to find the right ticker symbol.")]):
    """
    SEARCH for ticker symbols by inputting the company name to retrieve the most relevant results.
    """
    api_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={name}&apikey={API_KEY}"
    response = requests.get(api_url)
    data = response.json()
    top3 = data["bestMatches"][:3]
    
    formatted_json = json.dumps(top3, indent=4)

    print(formatted_json)

if __name__ == "__main__":
    app()
