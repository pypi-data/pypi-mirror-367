from pathlib import Path
import random
import typer
from typing import Optional
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

# Imports previously in cli/commands.py, now needed here
from mockingbird.blueprint.engine import BlueprintEngine
from mockingbird.common.exceptions import BlueprintValidationError # Import the custom exception
from mockingbird.generation.execution_context import ExecutionContext
from mockingbird.generation.dependency_resolver import resolve_dependencies
from mockingbird.generation.core import GenerationCore
from mockingbird.output.service import OutputService

# Main app definition with detailed help, epilog, and markdown enabled
app = typer.Typer(
    name="mockingbird",
    help="🐦 Mockingbird: A CLI tool for generating realistic, high-volume, and relationally-integral mock data.",
    rich_markup_mode="markdown",
    add_completion=False, # Kept from original main.py
    no_args_is_help=True, # Kept from original main.py
    epilog="""
**Examples:**\n\n

```
mockingbird init
```
\n\n


```
mockingbird generate blueprint.yaml --format json --seed 123
```
\n\n
For more help on a specific command, type:
`mockingbird [COMMAND] --help`
    """
)

# init command (copied from cli/commands.py)
@app.command()
def init(
    output_file: Path = typer.Option(
        "Blueprint.yaml",
        "--output", "-o",
        help="The name of the blueprint file to generate.",
        writable=True,
        resolve_path=True
    )
):
    """
    Initialize a Mockingbird project by generating a template `Blueprint.yaml` file.

    This command helps you get started by creating a basic blueprint file with example
    structures. You can then edit this file to define your specific data generation needs.
    \n\n
    **Future Feature Disclaimer:**
    Please note that in the current version (V1.0), this command *only* generates a template
    blueprint. Functionality to automatically generate a blueprint from an existing database
    schema (e.g., SQL DDL, Prisma schema) is planned for a future release.
    
    \n
    ### Examples:
    \n
    1. Create a blueprint file named Blueprint.yaml in the current directory. \ 
    
    $ mockingbird init
    \n\n
    2. Create a blueprint file with a custom name, \ 
    
    $ mockingbird init --output my_custom_blueprint.yaml
    """
    typer.echo(f"Initializing Mockingbird project (template for: {output_file})...")
    engine = BlueprintEngine()
    try:
        template_content = engine.generate_template_blueprint()
        with open(output_file, "w") as f:
            f.write(template_content)
        typer.secho(f"Template blueprint created at: {output_file}", fg=typer.colors.GREEN)
        typer.echo("Please edit it to define your data generation needs.")
    except Exception as e:
        typer.secho(f"Error during init: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

# generate command (copied from cli/commands.py)
@app.command()
def generate(
    blueprint_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Path to the Blueprint.yaml file."
    ),
    output_format: str = typer.Option(
        "csv",
        "--format", "-f",
        help="Output format (csv, json, parquet).",
        # rich_help_panel="Output Configuration"
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed", "-s",
        help="Random seed for reproducible generation.",
        # rich_help_panel="Advanced"
    ),
    output_dir: Path = typer.Option(
        "output_data",
        "--out-dir", "-d",
        help="Directory to save generated files.",
        file_okay=False,
        resolve_path=True,
        # rich_help_panel="Output Configuration"
    )
):
    """
    Generate mock data based on the provided `Blueprint.yaml` file.

    This command reads your blueprint, resolves entity dependencies, generates data
    according to your specifications, and outputs it in the desired format.

    ## **Examples:**

    1.  **Basic Usage**. \  

        Generate data using a blueprint in the current directory (default CSV output). \ 

        `$ mockingbird generate Blueprint.yaml`

    2.  **Specify Output Format** \ 

        Generate data in JSON format. \ 

        `$ mockingbird generate path/to/your/blueprint.yaml --format json`.  

    3.  **Ensure Reproducibility** \ 

        Generate data with a specific random seed. \ 

        `$ mockingbird generate Blueprint.yaml --seed 123`.  

    4.  **Custom Output Directory**

        Generate data and save it to a different directory. \ 

        `$ mockingbird generate Blueprint.yaml --out-dir ./my_mock_data`.  

    5.  **Combine Options**

        Generate JSON data, with a seed, to a specific directory.\ 

        `$ mockingbird generate Blueprint.yaml --format json --seed 456 --out-dir results/json`
    """
    console = Console()
    start_time = time.time()

    console.print(f"Starting data generation from: {blueprint_file}")
    if not seed:
        seed = random.randint(0, 1000000)
        console.print(f"Output format: {output_format}, Seed: {seed} (randomly generated), Output directory: {output_dir}")
    else:
        console.print(f"Output format: {output_format}, Seed: {seed}, Output directory: {output_dir}")

    try:
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        blueprint_engine = BlueprintEngine()
        parsed_blueprint = blueprint_engine.parse_blueprint(blueprint_file)
        blueprint_engine.validate_blueprint_structure(parsed_blueprint)

        # Extract global generator configs and entities
        global_generator_configs = parsed_blueprint.get('generators', {})
        entities_only_blueprint = {k: v for k, v in parsed_blueprint.items() if k != 'generators'}

        sorted_entities_list = resolve_dependencies(entities_only_blueprint)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            transient=False
        ) as progress:
            total_records = sum(parsed_blueprint.get(name, {}).get("count", 1) for name in sorted_entities_list)

            gen_progress_task = progress.add_task("[bold cyan]Generating data...", total=len(sorted_entities_list))
            execution_context = ExecutionContext(seed=seed)
            generation_core = GenerationCore(
                entities_only_blueprint,
                execution_context,
                progress,
                gen_progress_task,
                global_generator_configs=global_generator_configs
            )
            all_generated_data = generation_core.generate_data(sorted_entities_list)

            export_progress_task = progress.add_task("[bold magenta]Exporting data...", total=len(sorted_entities_list))
            output_service = OutputService(progress, export_progress_task)
            output_service.export_all_data(all_generated_data, output_format, output_dir)

        total_time = time.time() - start_time
        table = Table(title="Generation Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Total execution time", f"{total_time:.2f} seconds")
        table.add_row("Total entities generated", str(len(sorted_entities_list)))
        table.add_row("Total records generated", f"{total_records:,}")
        table.add_row("Output directory", str(output_dir))
        table.add_row("Seed used", str(seed))
        console.print(table)

        console.print(f"\n[bold green]Mock data generation successful! Output is in {output_dir}[/bold green]")
        console.print(f"To regenerate the same data, use the same blueprint file and Seed: {seed}")

    except FileNotFoundError as e:
        console.print(f"[bold red]Error: Blueprint file not found at {blueprint_file}[/bold red]")
        raise typer.Exit(code=1)
    except BlueprintValidationError as e: # Catch our specific validation error
        typer.secho(f"Blueprint Validation Error: {e}", fg=typer.colors.RED)
        # Consider adding more details or specific formatting for validation errors if needed
        # For example, if the error message contains newlines for multi-part errors:
        # typer.echo(f"Blueprint Validation Error:")
        # typer.secho(str(e), fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except ValueError as e: # Catch other parsing errors, dependency errors, etc.
        typer.secho(f"Configuration or Blueprint Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except RuntimeError as e: # Catch generation errors
        typer.secho(f"Generation Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"An unexpected error occurred: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    finally:
        if 'execution_context' in locals() and hasattr(execution_context, 'close'):
            execution_context.close() # For future use e.g. closing DB connection

# version command (kept from original main.py)
@app.command()
def version():
    """
    Show project version.
    """
    # This would ideally read from pyproject.toml or a __version__ variable
    typer.echo("Mockingbird version 0.1.0 (dummy)")

if __name__ == "__main__":
    app()
