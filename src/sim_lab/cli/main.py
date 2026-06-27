"""Command line interface for SimLab."""

import typer
from typing import Optional
import importlib.metadata
import os
import sys

from rich.console import Console
from rich.panel import Panel

# Create Typer app with command groups
app = typer.Typer(
    name="simlab",
    help="Business simulation toolkit for educational use",
    add_completion=False,
)

sim_app = typer.Typer(help="Run various simulations")
ui_app = typer.Typer(help="Launch different user interfaces")
util_app = typer.Typer(help="Utility commands")

app.add_typer(sim_app, name="sim")
app.add_typer(ui_app, name="ui")
app.add_typer(util_app, name="util")

# Create subgroups for simulations
stock_app = typer.Typer(help="Stock market simulation commands")
resource_app = typer.Typer(help="Resource fluctuations simulation commands")
product_app = typer.Typer(help="Product popularity simulation commands")

sim_app.add_typer(stock_app, name="stock")
sim_app.add_typer(resource_app, name="resource")
sim_app.add_typer(product_app, name="product")

# Subgroups for additional simulations
game_of_life_app = typer.Typer(help="Game of Life simulation commands")
forest_fire_app = typer.Typer(help="Forest fire simulation commands")
boids_app = typer.Typer(help="Boids flocking simulation commands")
gillespie_app = typer.Typer(help="Gillespie SSA simulation commands")

sim_app.add_typer(game_of_life_app, name="game-of-life")
sim_app.add_typer(forest_fire_app, name="forest-fire")
sim_app.add_typer(boids_app, name="boids")
sim_app.add_typer(gillespie_app, name="gillespie")

console = Console()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show the application version and exit."
    ),
):
    """SimLab CLI - Business simulation toolkit for educational use."""
    if version:
        try:
            version = importlib.metadata.version("sim-lab")
            console.print(f"SimLab version: {version}")
        except importlib.metadata.PackageNotFoundError:
            console.print("SimLab version: [italic]development[/italic]")
        raise typer.Exit()


@stock_app.command("run")
def run_stock_simulation(
    days: int = typer.Option(365, help="Number of days to simulate"),
    start_price: float = typer.Option(100.0, help="Starting stock price"),
    volatility: float = typer.Option(0.02, help="Daily volatility (0.01-0.10)"),
    drift: float = typer.Option(0.001, help="Daily price trend"),
    event_day: Optional[int] = typer.Option(None, help="Day of market event (optional)"),
    event_impact: float = typer.Option(0.0, help="Impact of market event (-0.9 to 0.9)"),
    random_seed: Optional[int] = typer.Option(None, help="Random seed for reproducibility"),
    output: Optional[str] = typer.Option(None, help="Output CSV file path"),
    viz: bool = typer.Option(False, help="Visualize the results"),
):
    """Run a stock market simulation with the specified parameters."""
    from sim_lab import StockMarketSimulation
    import matplotlib.pyplot as plt
    import pandas as pd
    import os

    console.print(Panel("Running Stock Market Simulation", style="green"))
    
    # Run simulation
    sim = StockMarketSimulation(
        start_price=start_price,
        days=days,
        volatility=volatility,
        drift=drift,
        event_day=event_day,
        event_impact=event_impact,
        random_seed=random_seed,
    )
    
    prices = sim.run_simulation()
    
    # Display results summary
    console.print(f"Simulation complete: {days} days simulated")
    console.print(f"Starting price: ${start_price:.2f}")
    console.print(f"Final price: ${prices[-1]:.2f}")
    console.print(f"Change: {((prices[-1] / start_price) - 1) * 100:.2f}%")
    
    # Save to CSV if requested
    if output:
        df = pd.DataFrame({"day": range(len(prices)), "price": prices})
        df.to_csv(output, index=False)
        console.print(f"Results saved to {output}")
    
    # Visualize if requested
    if viz:
        plt.figure(figsize=(12, 6))
        plt.plot(prices)
        plt.title("Stock Market Simulation")
        plt.xlabel("Days")
        plt.ylabel("Price ($)")
        
        if event_day is not None:
            plt.axvline(x=event_day, color='red', linestyle='--', 
                       label=f'Market Event (Impact: {event_impact*100:.1f}%)')
            plt.legend()
        
        plt.tight_layout()
        plt.show()


@resource_app.command("run")
def run_resource_simulation(
    days: int = typer.Option(365, help="Number of days to simulate"),
    start_price: float = typer.Option(100.0, help="Starting resource price"),
    volatility: float = typer.Option(0.02, help="Daily volatility (0.01-0.10)"),
    drift: float = typer.Option(0.001, help="Daily price trend"),
    disruption_day: Optional[int] = typer.Option(None, help="Day of supply disruption (optional)"),
    disruption_severity: float = typer.Option(0.0, help="Severity of disruption (0.0-1.0)"),
    random_seed: Optional[int] = typer.Option(None, help="Random seed for reproducibility"),
    output: Optional[str] = typer.Option(None, help="Output CSV file path"),
    viz: bool = typer.Option(False, help="Visualize the results"),
):
    """Run a resource fluctuations simulation with the specified parameters."""
    from sim_lab import ResourceFluctuationsSimulation
    import matplotlib.pyplot as plt
    import pandas as pd
    
    console.print(Panel("Running Resource Fluctuations Simulation", style="blue"))
    
    # Run simulation
    sim = ResourceFluctuationsSimulation(
        start_price=start_price,
        days=days,
        volatility=volatility,
        drift=drift,
        disruption_day=disruption_day,
        disruption_severity=disruption_severity,
        random_seed=random_seed,
    )
    
    prices = sim.run_simulation()
    
    # Display results summary
    console.print(f"Simulation complete: {days} days simulated")
    console.print(f"Starting price: ${start_price:.2f}")
    console.print(f"Final price: ${prices[-1]:.2f}")
    console.print(f"Change: {((prices[-1] / start_price) - 1) * 100:.2f}%")
    
    # Save to CSV if requested
    if output:
        df = pd.DataFrame({"day": range(len(prices)), "price": prices})
        df.to_csv(output, index=False)
        console.print(f"Results saved to {output}")
    
    # Visualize if requested
    if viz:
        plt.figure(figsize=(12, 6))
        plt.plot(prices)
        plt.title("Resource Price Fluctuations")
        plt.xlabel("Days")
        plt.ylabel("Price ($)")
        
        if disruption_day is not None:
            plt.axvline(x=disruption_day, color='red', linestyle='--', 
                       label=f'Supply Disruption (Severity: {disruption_severity*100:.1f}%)')
            plt.legend()
        
        plt.tight_layout()
        plt.show()


@product_app.command("run")
def run_product_simulation(
    days: int = typer.Option(365, help="Number of days to simulate"),
    initial_popularity: float = typer.Option(0.01, help="Initial popularity (0.0-1.0)"),
    virality: float = typer.Option(0.1, help="Virality factor (0.0-1.0)"),
    marketing: float = typer.Option(0.05, help="Marketing effectiveness (0.0-1.0)"),
    random_seed: Optional[int] = typer.Option(None, help="Random seed for reproducibility"),
    output: Optional[str] = typer.Option(None, help="Output CSV file path"),
    viz: bool = typer.Option(False, help="Visualize the results"),
):
    """Run a product popularity simulation with the specified parameters."""
    from sim_lab import ProductPopularitySimulation
    import matplotlib.pyplot as plt
    import pandas as pd
    
    console.print(Panel("Running Product Popularity Simulation", style="yellow"))
    
    # Run simulation
    sim = ProductPopularitySimulation(
        days=days,
        initial_popularity=initial_popularity,
        virality_factor=virality,
        marketing_effectiveness=marketing,
        random_seed=random_seed,
    )
    
    popularity = sim.run_simulation()
    
    # Display results summary
    console.print(f"Simulation complete: {days} days simulated")
    console.print(f"Initial popularity: {initial_popularity:.1%}")
    console.print(f"Final popularity: {popularity[-1]:.1%}")
    console.print(f"Peak popularity: {max(popularity):.1%}")
    
    # Save to CSV if requested
    if output:
        df = pd.DataFrame({"day": range(len(popularity)), "popularity": popularity})
        df.to_csv(output, index=False)
        console.print(f"Results saved to {output}")
    
    # Visualize if requested
    if viz:
        plt.figure(figsize=(12, 6))
        plt.plot(popularity)
        plt.title("Product Popularity Over Time")
        plt.xlabel("Days")
        plt.ylabel("Popularity (%)")
        plt.ylim(0, 1)
        
        plt.tight_layout()
        plt.show()


@game_of_life_app.command("run")
def run_game_of_life(
    pattern: str = typer.Option("glider", help="Pattern name (glider, blinker, gosper_glider_gun, ...)"),
    grid_size: int = typer.Option(50, help="Square grid size"),
    days: int = typer.Option(100, help="Number of generations"),
    random_seed: Optional[int] = typer.Option(42, help="Random seed (ignored for fixed patterns)"),
    viz: bool = typer.Option(False, help="Visualize the final grid"),
):
    """Run Conway's Game of Life from a named pattern."""
    from sim_lab.core import GameOfLifeSimulation
    sim = GameOfLifeSimulation(
        grid_size=(grid_size, grid_size), pattern=pattern, days=days, random_seed=random_seed
    )
    live = sim.run_simulation()
    console.print(f"[bold]Game of Life[/bold] - pattern '{pattern}' on {grid_size}x{grid_size}")
    console.print(f"Generations: {days} | final live cells: {int(live[-1])} | peak: {int(max(live))}")
    cycle = sim.detect_stable_pattern()
    if cycle is not None:
        console.print(f"Stable pattern detected: cycle length {cycle}")
    if viz:
        import matplotlib.pyplot as plt
        _, ax = plt.subplots()
        ax.imshow(sim.get_all_states()[-1], cmap="binary")
        ax.set_title(f"Game of Life - '{pattern}' (gen {days})")
        plt.show()


@forest_fire_app.command("run")
def run_forest_fire(
    grid_size: int = typer.Option(50, help="Square grid size"),
    initial_density: float = typer.Option(0.5, help="Initial tree fraction"),
    p: float = typer.Option(1e-4, help="Lightning (ignition) probability"),
    g: float = typer.Option(1e-2, help="Regrowth probability"),
    days: int = typer.Option(100, help="Number of generations"),
    random_seed: Optional[int] = typer.Option(42, help="Random seed"),
    viz: bool = typer.Option(False, help="Visualize tree/fire counts over time"),
):
    """Run a Drossel-Schwabl forest fire cellular automaton."""
    from sim_lab.core import ForestFireSimulation
    sim = ForestFireSimulation(
        grid_size=(grid_size, grid_size), initial_density=initial_density,
        p=p, g=g, days=days, random_seed=random_seed,
    )
    trees = sim.run_simulation()
    stats = sim.get_statistics()
    console.print("[bold]Forest Fire[/bold] (Drossel-Schwabl)")
    console.print(
        f"Mean trees: {stats['mean_trees']:.1f} | peak fires: {int(stats['max_fires'])} | "
        f"final tree fraction: {stats['final_tree_fraction']:.3f}"
    )
    if viz:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.plot(trees, label="trees")
        plt.plot(sim.fire_history, label="fires")
        plt.xlabel("Generation")
        plt.ylabel("Cells")
        plt.legend()
        plt.title("Forest Fire Simulation")
        plt.show()


@boids_app.command("run")
def run_boids(
    num_boids: int = typer.Option(100, help="Number of boids"),
    width: float = typer.Option(100.0, help="Field width"),
    height: float = typer.Option(100.0, help="Field height"),
    perception_radius: float = typer.Option(10.0, help="Neighbour perception radius"),
    days: int = typer.Option(100, help="Number of steps"),
    random_seed: Optional[int] = typer.Option(42, help="Random seed"),
    viz: bool = typer.Option(False, help="Visualize flock metrics over time"),
):
    """Run a Reynolds boids flocking simulation."""
    from sim_lab.core import BoidsSimulation
    sim = BoidsSimulation(
        num_boids=num_boids, width=width, height=height,
        perception_radius=perception_radius, days=days, random_seed=random_seed,
    )
    metrics = sim.run_simulation()
    final = metrics[-1]
    console.print("[bold]Boids[/bold] flocking (Reynolds)")
    console.print(
        f"Boids: {final['num_boids']} | mean speed: {final['mean_speed']:.3f} | "
        f"flock spread: {final['flock_spread']:.2f}"
    )
    if viz:
        import matplotlib.pyplot as plt
        steps = range(len(metrics))
        plt.figure(figsize=(10, 5))
        plt.plot(steps, [m["mean_speed"] for m in metrics], label="mean speed")
        plt.plot(steps, [m["flock_spread"] for m in metrics], label="flock spread")
        plt.xlabel("Step")
        plt.legend()
        plt.title("Boids Flock Metrics")
        plt.show()


@gillespie_app.command("run")
def run_gillespie(
    model: str = typer.Option("decay", help="Predefined model (decay)"),
    a0: int = typer.Option(100, help="Initial A molecules (decay model)"),
    rate: float = typer.Option(0.1, help="Reaction rate (decay model)"),
    max_time: float = typer.Option(50.0, help="Time horizon"),
    random_seed: Optional[int] = typer.Option(42, help="Random seed"),
    viz: bool = typer.Option(False, help="Visualize the trajectory"),
):
    """Run a Gillespie stochastic simulation (chemical kinetics)."""
    from sim_lab.core import create_decay_model
    if model != "decay":
        console.print(f"[yellow]Unknown model '{model}'; using 'decay'.[/yellow]")
    sim = create_decay_model(a0=a0, rate=rate, max_time=max_time, random_seed=random_seed)
    sim.run_simulation()
    stats = sim.get_statistics()
    console.print("[bold]Gillespie SSA[/bold] - A -> B decay")
    console.print(
        f"Events: {int(stats['events'])} | final time: {stats['final_time']:.2f} | "
        f"final A: {int(stats['A'])} | final B: {int(stats['B'])}"
    )
    if viz:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.step(sim.get_times(), sim.get_species("A"), where="post", label="A")
        plt.step(sim.get_times(), sim.get_species("B"), where="post", label="B")
        plt.xlabel("Time")
        plt.ylabel("Molecules")
        plt.legend()
        plt.title("Gillespie SSA - A -> B decay")
        plt.show()

@ui_app.command("web")
def launch_web(
    host: str = typer.Option("127.0.0.1", help="Host address to bind to"),
    port: int = typer.Option(8000, help="Port to listen on"),
):
    """Launch the web interface."""
    try:
        import uvicorn
        from sim_lab.web.app import create_app
        
        console.print(Panel(f"Launching web interface at http://{host}:{port}", style="green"))
        uvicorn.run(create_app, host=host, port=port)
    except ImportError:
        console.print(
            "Web dependencies not installed. Install with: pip install sim-lab[web]",
            style="red"
        )
        raise typer.Exit(1)


@ui_app.command("tui")
def launch_tui():
    """Launch the terminal user interface."""
    try:
        from sim_lab.tui.app import run_app
        
        console.print(Panel("Launching terminal user interface", style="blue"))
        run_app()
    except ImportError:
        console.print(
            "TUI dependencies not installed. Make sure 'textual' is installed.",
            style="red"
        )
        raise typer.Exit(1)


@util_app.command("info")
def show_info():
    """Show information about the SimLab package."""
    try:
        version = importlib.metadata.version("sim-lab")
        console.print(Panel.fit("SimLab Information", style="green"))
        console.print(f"Version: {version}")
        console.print(f"Python: {sys.version.split()[0]}")
        console.print(f"Path: {os.path.dirname(os.path.abspath(__file__))}")
    except importlib.metadata.PackageNotFoundError:
        console.print("SimLab package not installed in development mode.", style="yellow")
        console.print(f"Path: {os.path.dirname(os.path.abspath(__file__))}")


if __name__ == "__main__":
    app()