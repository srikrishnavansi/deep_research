import typer
from datetime import datetime
from rich import print
from rich.console import Console
from rich.logging import RichHandler
from pathlib import Path
from typing import Optional
from config import settings, SearchDepth
from agents.research_agent import ResearchAgent
from agents.synthesis_agent import SynthesisAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

app = typer.Typer()
console = Console()

def validate_depth(value: str) -> SearchDepth:
    """Validate and convert depth parameter"""
    try:
        if value.lower() in ['basic', 'advanced']:
            return SearchDepth(value.lower())
        return SearchDepth.from_user_input(value)
    except ValueError:
        valid_values = ["basic", "advanced", "shallow", "medium", "deep"]
        raise typer.BadParameter(
            f"Invalid depth value. Please use one of: {', '.join(valid_values)}"
        )

@app.command()
def research(
    query: str = typer.Argument(..., help="Research query to process"),
    depth: str = typer.Option(
        "basic",
        "--depth",
        help="Search depth (basic/advanced or shallow/medium/deep)",
        callback=validate_depth
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        help="Optional output file path"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging"
    )
):
    """
    Execute deep research using the multi-agent system
    """
    try:
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        console.print(f"[bold blue]Starting research for query:[/bold blue] {query}")
        console.print(f"[bold blue]Search depth:[/bold blue] {depth.value}")
        
        # Log the API key status (without revealing the key)
        tavily_key = settings.tavily_api_key.get_secret_value()
        logger.debug(f"Tavily API key present: {bool(tavily_key)}")
        
        # Create research agent
        research_agent = ResearchAgent(settings)
        
        # Execute research
        with console.status("[bold green]Researching...") as status:
            research_results = research_agent.execute(query, depth.value)
            
            if not research_results:
                raise Exception("No results returned from research agent")
            
            if "error" in research_results:
                raise Exception(f"Research failed: {research_results['error']}")
            
            status.update("[bold green]Processing results...")
            
            # Create synthesis agent and process results
            synthesis_agent = SynthesisAgent(settings)
            final_results = synthesis_agent.process_results(research_results, query)
        
        # Save or display results
        if output_file:
            output_file.write_text(str(final_results))
            console.print(f"[bold green]Results saved to:[/bold green] {output_file}")
        else:
            console.print("\n[bold green]Research Results:[/bold green]")
            console.print(final_results)
            
    except Exception as e:
        logger.exception("Error during research")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()