# pytestlab/cli.py
import sys
import typer
from typing_extensions import Annotated # For older Python, or just use `typing.Annotated` for Py 3.9+
from typing import Optional # Ensure Optional is imported
from pathlib import Path
import yaml
import rich # For pretty printing
from rich.syntax import Syntax
import importlib.util # For finding profile paths
import pkgutil # For finding profile paths
import types # For creating a simple namespace for the replay bench
import importlib.util

import os
import shutil
import difflib
import code

# Assuming these imports are valid after recent refactors
from pytestlab.config.loader import load_profile, resolve_profile_key_to_path
from pytestlab.instruments import AutoInstrument
from pytestlab.instruments.backends.recording_backend import RecordingBackend
from pytestlab.instruments.backends.session_recording_backend import SessionRecordingBackend
from pytestlab.instruments.backends.replay_backend import ReplayBackend
# For bench commands (anticipating section 6.2)
from pytestlab.config.bench_config import BenchConfigExtended
from pytestlab.bench import Bench
import time # For sleep functionality

# Import version for CLI
from pytestlab import __version__

def version_callback(value: bool):
    if value:
        rich.print(f"PyTestLab version {__version__}")
        raise typer.Exit()

app = typer.Typer(help="PyTestLab: Scientific test & measurement toolbox CLI.")

@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True,
        help="Show version and exit."
    )
):
    """PyTestLab: Scientific test & measurement toolbox CLI."""
    pass
profile_app = typer.Typer(name="profile", help="Manage instrument profiles.")
instrument_app = typer.Typer(name="instrument", help="Interact with instruments.")
bench_app = typer.Typer(name="bench", help="Manage bench configurations.")
sim_profile_app = typer.Typer(name="sim-profile", help="Manage simulation profiles.")

# Create a new Typer app for replay commands
replay_app = typer.Typer(name="replay", help="Record and replay complex measurement sessions.")
app.add_typer(replay_app)

app.add_typer(profile_app)
app.add_typer(instrument_app)
app.add_typer(bench_app)
app.add_typer(sim_profile_app)

# --- Simulation Profile Helpers ---
def get_user_override_path(profile_key: str) -> Path:
   """Gets the path to the user's override profile."""
   home_dir = Path.home()
   key_path = Path(profile_key.replace("/", os.sep) + ".yaml")
   return home_dir / ".config" / "pytestlab" / "profiles" / key_path

def get_user_recorded_profile_path(profile_key: str) -> Path:
    """Gets the path for a recorded simulation profile in the user's cache."""
    home_dir = Path.home()
    key_path = Path(profile_key.replace("/", os.sep) + ".yaml")
    return home_dir / ".config" / "pytestlab" / "recorded_sim_profiles" / key_path

# --- Simulation Profile Commands ---

@sim_profile_app.command("edit")
def sim_profile_edit(profile_key: Annotated[str, typer.Argument(help="Profile key (e.g., keysight/DSOX1204G).")]):
   """Opens the user's override profile in their default text editor."""
   try:
       official_path = resolve_profile_key_to_path(profile_key)
       override_path = get_user_override_path(profile_key)

       if not override_path.exists():
           rich.print(f"No user override found for '{profile_key}'. Creating one from the official profile.")
           override_path.parent.mkdir(parents=True, exist_ok=True)
           shutil.copy(official_path, override_path)
           rich.print(f"Copied official profile to: {override_path}")

       rich.print(f"Opening '{override_path}' in your default editor...")
       typer.launch(str(override_path))

   except FileNotFoundError:
       rich.print(f"[bold red]Error: Official profile for key '{profile_key}' not found.[/bold red]")
       raise typer.Exit(code=1)
   except Exception as e:
       rich.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
       raise typer.Exit(code=1)

@sim_profile_app.command("reset")
def sim_profile_reset(profile_key: Annotated[str, typer.Argument(help="Profile key to reset.")]):
   """Deletes the user's override profile, reverting to the official one."""
   override_path = get_user_override_path(profile_key)
   if override_path.exists():
       try:
           os.remove(override_path)
           rich.print(f"[bold green]Successfully deleted override profile:[/bold green] {override_path}")
           rich.print(f"Simulations for '{profile_key}' will now use the official profile.")
       except OSError as e:
           rich.print(f"[bold red]Error deleting file '{override_path}': {e}[/bold red]")
           raise typer.Exit(code=1)
   else:
       rich.print(f"[bold yellow]No user override profile to reset for '{profile_key}'.[/bold yellow]")


@sim_profile_app.command("diff")
def sim_profile_diff(profile_key: Annotated[str, typer.Argument(help="Profile key to compare.")]):
   """Shows a diff between the user's override and the official profile."""
   try:
       official_path = resolve_profile_key_to_path(profile_key)
       override_path = get_user_override_path(profile_key)

       if not override_path.exists():
           rich.print(f"[bold yellow]No user override profile found for '{profile_key}'. Nothing to compare.[/bold yellow]")
           raise typer.Exit()

       with open(official_path) as f_official, open(override_path) as f_override:
           official_lines = f_official.readlines()
           override_lines = f_override.readlines()

       diff = difflib.unified_diff(
           official_lines,
           override_lines,
           fromfile=f"official/{profile_key}",
           tofile=f"user/{profile_key}",
       )

       diff_str = "".join(diff)
       if not diff_str:
           rich.print("[bold green]No differences found between the official and user profiles.[/bold green]")
           return

       rich.print(f"[bold]Diff for {profile_key}:[/bold]")
       syntax = Syntax(diff_str, "diff", theme="monokai")
       rich.print(syntax)

   except FileNotFoundError:
       rich.print(f"[bold red]Error: Official profile for key '{profile_key}' not found.[/bold red]")
       raise typer.Exit(code=1)
   except Exception as e:
       rich.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
       raise typer.Exit(code=1)


@sim_profile_app.command("record")
def sim_profile_record(
    profile_key: Annotated[str, typer.Argument(help="Profile key of the instrument to record.")],
    address: Annotated[Optional[str], typer.Option(help="VISA address of the instrument.")] = None,
    output_path: Annotated[Optional[Path], typer.Option(help="Output path for the recorded YAML profile. If not provided, it will be saved to the user's cache.")] = None,
    script: Annotated[Optional[Path], typer.Option(help="Path to a Python script to run against the instrument.")] = None,
    simulate: Annotated[bool, typer.Option(help="Use a simulated instrument for recording.")] = False,
):
    """Records instrument interactions to create a simulation profile."""
    instrument = None
    try:
        if not simulate and not address:
            rich.print("[bold red]Error: The --address option is required for recording from a real instrument.[/bold red]")
            raise typer.Exit(code=1)

        final_output_path = output_path
        if not final_output_path:
            final_output_path = get_user_recorded_profile_path(profile_key)
            final_output_path.parent.mkdir(parents=True, exist_ok=True)
            rich.print(f"[yellow]No output path provided. Saving to user cache:[/yellow] {final_output_path}")

        if simulate:
            rich.print(f"Connecting to simulated instrument '{profile_key}'...")
        else:
            rich.print(f"Connecting to instrument '{profile_key}' at address '{address}'...")

        instrument = AutoInstrument.from_config(
            config_source=profile_key,
            simulate=simulate,
            address_override=address
        )
        instrument.connect_backend()

        # Wrap the real backend with the recording backend
        base_profile_model = load_profile(profile_key)
        base_profile = base_profile_model.model_dump()
        recording_backend = RecordingBackend(instrument._backend, str(final_output_path), base_profile=base_profile)
        instrument._backend = recording_backend

        rich.print("[bold green]Connection successful. Recording started.[/bold green]")

        if script:
            rich.print(f"\n[bold]Running script:[/bold] {script}")
            spec = importlib.util.spec_from_file_location("script_module", script)
            if spec and spec.loader:
                script_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(script_module)
                if hasattr(script_module, "main"):
                    script_module.main(instrument)
                else:
                    rich.print("[bold yellow]Warning: No 'main(instrument)' function found in script.[/bold yellow]")
            else:
                rich.print(f"[bold red]Error: Could not load script '{script}'.[/bold red]")
        else:
            rich.print("\n[bold]Starting interactive REPL. Press Ctrl+D or type 'exit()' to quit.[/bold]")
            # Basic async-unsafe REPL for demonstration
            code.interact(
                banner="PyTestLab Interactive Recording Session",
                local=dict(globals(), **{'instrument': instrument}),
                exitmsg="REPL finished."
            )

    except Exception as e:
        import traceback
        rich.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        traceback.print_exc()
        raise typer.Exit(code=1)
    finally:
        if instrument:
            rich.print("\nClosing connection and saving profile...")
            instrument.close()
            rich.print(f"[bold green]Profile saved to {final_output_path}.[/bold green]")

# --- Profile Commands ---
@profile_app.command("list")
def list_profiles(profile_dir: Annotated[Optional[Path], typer.Option(help="Custom directory for profiles.")] = None):
    """Lists available YAML instrument profiles."""
    try:
        profile_paths = []
        # Logic to find profiles in default package dir (pytestlab/profiles)
        spec = importlib.util.find_spec("pytestlab.profiles")
        if spec and spec.origin:
            default_profile_pkg_path = Path(spec.origin).parent
            for vendor_dir in default_profile_pkg_path.iterdir():
                if vendor_dir.is_dir() and vendor_dir.name != "__pycache__":
                    for profile_file in vendor_dir.glob("*.yaml"):
                        # Store as key like "vendor/file_name"
                        profile_key = f"{vendor_dir.name}/{profile_file.stem}"
                        profile_paths.append(profile_key)
        else:
            rich.print("[bold red]Error: Could not find the default profiles package.[/bold red]")
            raise typer.Exit(code=1)

        # Add logic for custom_dir if provided
        if profile_dir:
            if profile_dir.is_dir():
                for profile_file in profile_dir.glob("*.yaml"): # Assuming flat structure in custom_dir for now
                    profile_paths.append(str(profile_file.resolve()))
            else:
                rich.print(f"[bold yellow]Warning: Custom profile directory '{profile_dir}' not found.[/bold yellow]")

        if not profile_paths:
            rich.print("[bold yellow]No profiles found.[/bold yellow]")
            return

        table = rich.table.Table(title="[bold]Available Profiles[/bold]")
        table.add_column("Profile Key", style="cyan", no_wrap=True)
        for p_path in sorted(list(set(profile_paths))): # Use set to avoid duplicates if custom overlaps
            table.add_row(p_path)
        rich.print(table)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred while listing profiles: {e}[/bold red]")
        raise typer.Exit(code=1)

@profile_app.command("show")
def show_profile(profile_key_or_path: Annotated[str, typer.Argument(help="Profile key (e.g., keysight/DSOX1204G) or direct path to YAML file.")]):
    """Shows the content of a specific instrument profile."""
    try:
        profile_path = Path(profile_key_or_path)
        if not profile_path.is_file():
            profile_path = resolve_profile_key_to_path(profile_key_or_path)

        with open(profile_path) as f:
            content = f.read()
            rich.print(f"[bold]Profile: {profile_key_or_path}[/bold]")
            syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
            rich.print(syntax)
    except FileNotFoundError:
        rich.print(
            f"[bold red]Error: Profile '{profile_key_or_path}' not found.[/bold red]\n"
            "Please check for typos or ensure the profile exists in the 'pytestlab/profiles' directory."
        )
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        rich.print(f"[bold red]Error parsing YAML file '{profile_key_or_path}': {e}[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred while showing profile '{profile_key_or_path}': {e}[/bold red]")
        raise typer.Exit(code=1)


@profile_app.command("validate")
def validate_profiles(
    profiles_path: Annotated[Path, typer.Argument(help="Path to a directory of profiles or a single profile file.")]
):
    """Validates YAML profiles against their corresponding Pydantic models."""
    if not profiles_path.exists():
        rich.print(f"[bold red]Error: Path '{profiles_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    profile_files = []
    if profiles_path.is_dir():
        profile_files.extend(list(profiles_path.glob("*.yaml")))
        profile_files.extend(list(profiles_path.glob("*.yml")))
    elif profiles_path.is_file():
        if profiles_path.suffix in [".yaml", ".yml"]:
            profile_files.append(profiles_path)
        else:
            rich.print(f"[bold red]Error: '{profiles_path}' is not a YAML file.[/bold red]")
            raise typer.Exit(code=1)

    if not profile_files:
        rich.print(f"[bold yellow]No YAML profiles found in '{profiles_path}'.[/bold yellow]")
        raise typer.Exit()

    rich.print(f"[bold]Validating {len(profile_files)} profile(s) in '{profiles_path}'...[/bold]")

    success_count = 0
    error_count = 0

    for profile_file in profile_files:
        try:
            load_profile(profile_file)
            rich.print(f"  [green]✔[/green] [cyan]{profile_file.name}[/cyan] - Valid")
            success_count += 1
        except Exception as e:
            rich.print(f"  [bold red]✖[/bold red] [cyan]{profile_file.name}[/cyan] - [red]Invalid[/red]")
            rich.print(f"    [dim]Reason: {e}[/dim]")
            error_count += 1

    if error_count > 0:
        rich.print(f"\n[bold]Validation complete:[/bold] [green]{success_count} valid[/green], [red]{error_count} invalid[/red].")
        raise typer.Exit(code=1)
    else:
        rich.print(f"\n[bold green]All {success_count} profiles are valid.[/bold green]")


# --- Instrument Commands ---
@instrument_app.command("idn")
def instrument_idn(
    profile_key_or_path: Annotated[str, typer.Option(help="Profile key or path.")],
    address: Annotated[Optional[str], typer.Option(help="VISA address. Overrides profile if provided.")] = None,
    simulate: Annotated[bool, typer.Option(help="Run in simulation mode.")] = False
):
    """Connects to an instrument and prints its *IDN? response."""
    instrument = None  # Initialize instrument to None
    try:
        inst_config_model = load_profile(profile_key_or_path)

        instrument = AutoInstrument.from_config(
            config_source=inst_config_model,
            simulate=simulate,
            address_override=address
        )
        instrument.connect_backend()
        idn_response = instrument.id()
        rich.print(f"[bold green]IDN Response:[/bold] {idn_response}")

    except FileNotFoundError:
        rich.print(
            f"[bold red]Error: Profile '{profile_key_or_path}' not found.[/bold red]\n"
            "Please check for typos or ensure the profile exists in the 'pytestlab/profiles' directory."
        )
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An error occurred during the instrument IDN query: {e}[/bold red]")
        # rich.print_exception(show_locals=True) # Uncomment for more detailed debug info
        raise typer.Exit(code=1)
    finally:
        if instrument:
            instrument.close()

# Implement other commands: instrument selftest, instrument config dump, repl
# For REPL:
# @instrument_app.command("repl")
# def instrument_repl(...):
#     # ... setup instrument ...
#     # import code
#     # local_vars = {"instrument": instrument, "np": np}
#     # code.interact(local=local_vars, banner="PyTestLab REPL...")
#     typer.echo("Async REPL not yet fully implemented. Instrument is set up.")
#     # instrument.close()


# --- Bench Commands (Implement if Bench system from 6.2 is ready) ---
@bench_app.command("ls")
def bench_ls(bench_yaml_path: Annotated[Path, typer.Argument(help="Path to the bench.yaml file.")]):
    """Lists instruments in a bench configuration."""
    try:
        with open(bench_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        config = BenchConfigExtended.model_validate(data) # Validate
        table = rich.table.Table(title=f"Bench: {config.bench_name}")
        table.add_column("Alias", style="cyan")
        table.add_column("Profile", style="magenta")
        table.add_column("Address", style="green")
        table.add_column("Backend Type", style="yellow")
        table.add_column("Simulate", style="blue")

        for alias, entry in config.instruments.items():
            sim_status = "Global" if entry.simulate is None else str(entry.simulate)
            addr = entry.address or "N/A (simulated)"
            backend_type = (entry.backend.get("type") if entry.backend and entry.backend.get("type") else
                          config.backend_defaults.get("type", "visa") if config.backend_defaults else "visa")
            table.add_row(alias, entry.profile, addr, backend_type, sim_status)
        rich.print(table)
    except FileNotFoundError:
        rich.print(f"[bold red]Error: Bench configuration file not found at '{bench_yaml_path}'.[/bold red]")
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        rich.print(f"[bold red]Error parsing YAML file '{bench_yaml_path}': {e}[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred while listing the bench instruments: {e}[/bold red]")
        raise typer.Exit(code=1)

@bench_app.command("validate")
def bench_validate_cli(bench_yaml_path: Annotated[Path, typer.Argument(help="Path to the bench.yaml file.")]):
    """Validates a bench configuration file (dry-run)."""
    try:
        with open(bench_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        config = BenchConfig.model_validate(data) # This will raise ValidationError on issues
        rich.print(f"[bold green]Bench configuration '{bench_yaml_path}' is valid.[/bold green]")

        rich.print("Validating individual instrument profiles...")
        all_profiles_valid = True
        for alias, entry in config.instruments.items():
            try:
                load_profile(entry.profile)
                rich.print(f"  [green]✔[/green] Profile '[magenta]{entry.profile}[/magenta]' for alias '[cyan]{alias}[/cyan]' loaded successfully.")
            except FileNotFoundError:
                all_profiles_valid = False
                rich.print(
                    f"  [bold red]✖ Error:[/bold red] Profile '[magenta]{entry.profile}[/magenta]' for alias '[cyan]{alias}[/cyan]' not found."
                )
            except Exception as e_profile:
                all_profiles_valid = False
                rich.print(f"  [bold red]✖ Error:[/bold red] Failed to load profile '[magenta]{entry.profile}[/magenta]' for alias '[cyan]{alias}[/cyan]': {e_profile}")

        if not all_profiles_valid:
            raise typer.Exit(code=1)

    except FileNotFoundError:
        rich.print(f"[bold red]Error: Bench configuration file not found at '{bench_yaml_path}'.[/bold red]")
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        rich.print(f"[bold red]Error parsing YAML file '{bench_yaml_path}': {e}[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred during bench validation: {e}[/bold red]")
        raise typer.Exit(code=1)

@bench_app.command("id")
def bench_id_cli(bench_yaml_path: Annotated[Path, typer.Argument(help="Path to the bench.yaml file.")]):
    """Connects to real instruments in a bench and prints their *IDN? responses."""
    bench = None
    try:
        bench = Bench.open(bench_yaml_path)
        rich.print(f"Querying *IDN? for instruments in bench: [bold]{bench.config.bench_name}[/bold]")

        table = rich.table.Table(title="Instrument IDN Responses")
        table.add_column("Alias", style="cyan")
        table.add_column("Profile", style="magenta")
        table.add_column("IDN Response / Status", style="green")

        for alias, instrument in bench._instrument_instances.items():
            entry = bench.config.instruments[alias]
            is_simulated = bench.config.simulate
            if entry.simulate is not None:
                is_simulated = entry.simulate

            if not is_simulated:
                try:
                    idn_str = instrument.id()
                    table.add_row(alias, entry.profile, idn_str)
                except Exception as e_idn:
                    table.add_row(alias, entry.profile, f"[bold red]Error querying IDN - {e_idn}[/bold red]")
            else:
                table.add_row(alias, entry.profile, "[blue]Simulated[/blue]")

        rich.print(table)
    except FileNotFoundError:
        rich.print(f"[bold red]Error: Bench configuration file not found at '{bench_yaml_path}'.[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred during the bench ID query: {e}[/bold red]")
        raise typer.Exit(code=1)
    finally:
        if bench:
            bench.close_all()

@bench_app.command("sim")
def bench_sim_cli(bench_yaml_path: Annotated[Path, typer.Argument(help="Path to the bench.yaml file.")],
                  output_path: Annotated[Optional[Path], typer.Option(help="Output path for the simulated descriptor.")] = None):
    """Converts a bench descriptor to full simulation mode."""
    try:
        with open(bench_yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        config = BenchConfig.model_validate(data)

        sim_config_data = config.model_dump(mode='python') # Get dict representation
        sim_config_data['simulate'] = True # Global simulate
        for alias_key in sim_config_data['instruments']:
            sim_config_data['instruments'][alias_key]['simulate'] = True
            sim_config_data['instruments'][alias_key]['address'] = "sim"
            # Ensure backend is also sim if present
            if sim_config_data['instruments'][alias_key].get('backend'):
               sim_config_data['instruments'][alias_key]['backend']['type'] = "sim"
            else: # If no backend entry, create one for sim
               sim_config_data['instruments'][alias_key]['backend'] = {'type': 'sim', 'timeout_ms': 5000} # Default timeout

        sim_yaml = yaml.dump(sim_config_data, sort_keys=False)

        if output_path:
            with open(output_path, 'w') as f_out:
                f_out.write(sim_yaml)
            rich.print(f"[bold green]Simulated bench descriptor saved to:[/bold green] {output_path}")
        else:
            syntax = Syntax(sim_yaml, "yaml", theme="monokai", line_numbers=True)
            rich.print(syntax)

    except FileNotFoundError:
        rich.print(f"[bold red]Error: Bench configuration file not found at '{bench_yaml_path}'.[/bold red]")
        raise typer.Exit(code=1)
    except yaml.YAMLError as e:
        rich.print(f"[bold red]Error parsing YAML file '{bench_yaml_path}': {e}[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rich.print(f"[bold red]An unexpected error occurred while converting the bench to simulation mode: {e}[/bold red]")
        raise typer.Exit(code=1)

# --- Replay Commands ---
@replay_app.command("record")
def replay_record(
    script: Annotated[Path, typer.Argument(help="Path to the Python script to execute.")],
    bench_config: Annotated[Path, typer.Option("--bench", help="Path to the bench.yaml configuration file.")],
    output: Annotated[Path, typer.Option("--output", help="Path to save the recorded session YAML file.")],
):
    """Records a measurement session by running a script against a real bench."""
    rich.print(f"[bold cyan]Starting recording session...[/bold cyan]")
    rich.print(f"Bench Config: {bench_config}")
    rich.print(f"Script: {script}")
    rich.print(f"Output File: {output}")

    bench = None
    try:
        bench = Bench.open(bench_config)
        recorded_data = {}

        rich.print("\n[bold]Wrapping instrument backends for recording:[/bold]")
        for alias, instrument in bench.instruments.items():
            profile_key = bench.config.instruments[alias].profile
            session_log = []
            recorded_data[alias] = {"profile": profile_key, "log": session_log}
            instrument._backend = SessionRecordingBackend(instrument._backend, session_log)
            rich.print(f"  - Wrapped '{alias}'")

        rich.print("\n[bold]Executing script...[/bold]")
        spec = importlib.util.spec_from_file_location("script_module", script)
        if not spec or not spec.loader:
            raise FileNotFoundError(f"Could not load script module from {script}")
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)

        if hasattr(script_module, "main"):
            script_module.main(bench)
        else:
            raise TypeError("Script must contain an async function `main(bench)`.")

        rich.print("[bold green]Script execution finished.[/bold green]")

    except Exception as e:
        rich.print(f"[bold red]An error occurred during recording: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)
    finally:
        if bench:
            bench.close_all()

    rich.print(f"\n[bold]Saving recorded session to {output}...[/bold]")
    with open(output, "w") as f:
        yaml.dump(recorded_data, f, sort_keys=False, default_flow_style=False)
    rich.print("[bold green]Recording complete.[/bold green]")


@replay_app.command("run")
def replay_run(
    script: Annotated[Path, typer.Argument(help="Path to the Python script to execute.")],
    session: Annotated[Path, typer.Option("--session", help="Path to the recorded session YAML file.")],
):
    """Replays a recorded measurement session against a simulated bench."""
    # Convert to Path objects if they're strings (for direct function calls)
    if isinstance(script, str):
        script = Path(script)
    if isinstance(session, str):
        session = Path(session)

    rich.print(f"[bold cyan]Starting replay session...[/bold cyan]")
    rich.print(f"Session File: {session}")
    rich.print(f"Script: {script}")

    if not session.exists():
        rich.print(f"[bold red]Error: Session file not found at {session}[/bold red]")
        raise typer.Exit(code=1)

    with open(session) as f:
        session_data = yaml.safe_load(f)

    replay_bench = types.SimpleNamespace()
    instrument_instances = {}
    instrument_aliases = list(session_data.keys())

    try:
        rich.print("\n[bold]Building replay bench from session file:[/bold]")
        for alias in instrument_aliases:
            data = session_data[alias]
            profile_key = data["profile"]
            session_log = data["log"]

            replay_backend = ReplayBackend(session_log, model_name=alias)

            instrument = AutoInstrument.from_config(
                config_source=profile_key,
                backend_override=replay_backend
            )
            instrument.connect_backend() # Connects the replay backend

            setattr(replay_bench, alias, instrument)
            instrument_instances[alias] = instrument
            rich.print(f"  - Created instrument '{alias}' for replay.")

        replay_bench.instruments = instrument_instances

        rich.print("\n[bold]Executing script in replay mode...[/bold]")
        spec = importlib.util.spec_from_file_location("script_module", script)
        if not spec or not spec.loader:
            raise FileNotFoundError(f"Could not load script module from {script}")
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)

        if hasattr(script_module, "main"):
            script_module.main(replay_bench)
        else:
            raise TypeError("Script must contain an async function `main(bench)`.")

        rich.print("[bold green]Script execution finished successfully.[/bold green]")

    except Exception as e:
        rich.print(f"[bold red]An error occurred during replay: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)
    finally:
        for inst in instrument_instances.values():
            inst.close()

    rich.print("[bold green]Replay complete.[/bold green]")

@app.command("run")
def run_command(
    script: Annotated[Path, typer.Argument(help="Path to the Python script to execute.")],
    bench_config: Annotated[Path, typer.Option("--bench", help="Path to the bench.yaml configuration file.")],
    simulate: Annotated[bool, typer.Option("--simulate", help="Force simulation mode.")] = False,
    output: Annotated[Optional[Path], typer.Option("--output", help="Path to save measurement results.")] = None,
):
    """Execute a measurement script against a bench configuration."""
    rich.print(f"[bold cyan]Running measurement script...[/bold cyan]")
    rich.print(f"Script: {script}")
    rich.print(f"Bench Config: {bench_config}")
    rich.print(f"Simulation Mode: {simulate}")

    if not script.exists():
        rich.print(f"[bold red]Error: Script file not found at {script}[/bold red]")
        raise typer.Exit(code=1)

    if not bench_config.exists():
        rich.print(f"[bold red]Error: Bench config file not found at {bench_config}[/bold red]")
        raise typer.Exit(code=1)

    bench = None
    try:
        # Load bench configuration
        if simulate:
            # Modify config to force simulation
            with open(bench_config, 'r') as f:
                config_data = yaml.safe_load(f)
            config_data['simulate'] = True
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
                yaml.dump(config_data, temp_file)
                temp_bench_config = Path(temp_file.name)
            bench = Bench.open(temp_bench_config)
            temp_bench_config.unlink()  # Clean up temp file
        else:
            bench = Bench.open(bench_config)

        rich.print(f"[bold green]Bench '{bench.config.bench_name}' loaded successfully[/bold green]")

        # Load and execute the script
        spec = importlib.util.spec_from_file_location("measurement_script", script)
        if not spec or not spec.loader:
            raise FileNotFoundError(f"Could not load script module from {script}")

        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)

        # Execute main function if it exists
        if hasattr(script_module, "main"):
            rich.print("[bold]Executing script main function...[/bold]")
            result = script_module.main(bench)

            # Save results if output path specified
            if output and result:
                rich.print(f"[bold]Saving results to {output}...[/bold]")
                with open(output, 'w') as f:
                    if isinstance(result, dict):
                        yaml.dump(result, f)
                    else:
                        f.write(str(result))
                rich.print(f"[bold green]Results saved to {output}[/bold green]")

            rich.print("[bold green]Script execution completed successfully[/bold green]")
        else:
            rich.print(f"[bold yellow]Warning: No 'main' function found in {script}[/bold yellow]")
            rich.print("[bold yellow]Script was loaded but no main function was executed[/bold yellow]")

    except Exception as e:
        rich.print(f"[bold red]Error during execution: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        raise typer.Exit(code=1)
    finally:
        if bench:
            bench.close_all()

@app.command("list")
def list_command(
    resource: Annotated[str, typer.Argument(help="Resource type to list: 'profiles', 'benches', 'examples'")] = "profiles"
):
    """List available resources (profiles, bench configs, examples)."""

    if resource == "profiles":
        rich.print("[bold cyan]Available instrument profiles:[/bold cyan]")
        try:
            # Find built-in profiles
            spec = importlib.util.find_spec("pytestlab.profiles")
            if spec and spec.origin:
                profiles_dir = Path(spec.origin).parent
                table = rich.table.Table(title="Instrument Profiles")
                table.add_column("Profile Key", style="cyan")
                table.add_column("Vendor", style="magenta")
                table.add_column("Model", style="green")

                for vendor_dir in profiles_dir.iterdir():
                    if vendor_dir.is_dir() and vendor_dir.name != "__pycache__":
                        vendor = vendor_dir.name
                        for profile_file in vendor_dir.glob("*.yaml"):
                            model = profile_file.stem
                            profile_key = f"{vendor}/{model}"
                            table.add_row(profile_key, vendor, model)

                rich.print(table)
            else:
                rich.print("[bold red]Could not find profiles directory[/bold red]")

        except Exception as e:
            rich.print(f"[bold red]Error listing profiles: {e}[/bold red]")

    elif resource == "benches":
        rich.print("[bold cyan]Searching for bench configurations:[/bold cyan]")
        bench_files = []

        # Search in common locations
        search_paths = [
            Path.cwd(),
            Path.cwd() / "examples",
            Path.cwd() / "configs",
            Path.cwd() / "benches"
        ]

        for search_path in search_paths:
            if search_path.exists():
                bench_files.extend(search_path.glob("*bench*.yaml"))
                bench_files.extend(search_path.glob("bench.yaml"))

        if bench_files:
            table = rich.table.Table(title="Bench Configurations")
            table.add_column("File", style="cyan")
            table.add_column("Path", style="green")

            for bench_file in sorted(set(bench_files)):
                table.add_row(bench_file.name, str(bench_file.parent))

            rich.print(table)
        else:
            rich.print("[bold yellow]No bench configuration files found[/bold yellow]")
            rich.print("Searched in: " + ", ".join(str(p) for p in search_paths))

    elif resource == "examples":
        rich.print("[bold cyan]Available examples:[/bold cyan]")
        try:
            # Find examples directory
            examples_dir = Path.cwd() / "examples"
            if not examples_dir.exists():
                # Try to find examples relative to package
                spec = importlib.util.find_spec("pytestlab")
                if spec and spec.origin:
                    pkg_dir = Path(spec.origin).parent.parent
                    examples_dir = pkg_dir / "examples"

            if examples_dir.exists():
                table = rich.table.Table(title="Example Scripts")
                table.add_column("Script", style="cyan")
                table.add_column("Description", style="green")

                for script_file in examples_dir.glob("*.py"):
                    description = "Python script"
                    # Try to read first line of docstring for description
                    try:
                        with open(script_file, 'r') as f:
                            lines = f.readlines()
                            for line in lines[:10]:  # Check first 10 lines
                                if '"""' in line and len(line.strip()) > 3:
                                    description = line.strip().replace('"""', '').strip()
                                    if description:
                                        break
                    except:
                        pass

                    table.add_row(script_file.name, description[:60] + "..." if len(description) > 60 else description)

                rich.print(table)
            else:
                rich.print("[bold yellow]Examples directory not found[/bold yellow]")

        except Exception as e:
            rich.print(f"[bold red]Error listing examples: {e}[/bold red]")

    else:
        rich.print(f"[bold red]Unknown resource type: {resource}[/bold red]")
        rich.print("Available resource types: profiles, benches, examples")
        raise typer.Exit(code=1)

def run_app():
    """Main entry point for the CLI."""
    app()

def main():
    if "sim-profile" in sys.argv and "record" in sys.argv:
        # Direct call to sim_profile_record
        from pytestlab.cli import sim_profile_record
        # This is a simplified parser. A more robust solution would use
        # a proper argument parsing library.
        kwargs = {}
        for i, arg in enumerate(sys.argv):
            if arg.startswith("--"):
                if i + 1 < len(sys.argv) and not sys.argv[i + 1].startswith("--"):
                    kwargs[arg[2:].replace("-", "_")] = sys.argv[i + 1]
                else:
                    kwargs[arg[2:].replace("-", "_")] = True

        # Direct function call
        sim_profile_record(
            profile_key=sys.argv[3],
            **kwargs
        )
    elif "replay" in sys.argv and ("record" in sys.argv or "run" in sys.argv):
        # Handle async replay commands
        if "record" in sys.argv:
            from pytestlab.cli import replay_record
            # Parse arguments for replay record
            script_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
            bench_config = None
            output = None

            for i, arg in enumerate(sys.argv):
                if arg == "--bench" and i + 1 < len(sys.argv):
                    bench_config = Path(sys.argv[i + 1])
                elif arg == "--output" and i + 1 < len(sys.argv):
                    output = Path(sys.argv[i + 1])

            if script_path and bench_config and output:
                replay_record(script_path, bench_config, output)
            else:
                rich.print("[bold red]Error: Missing required arguments for replay record[/bold red]")
                sys.exit(1)

        elif "run" in sys.argv:
            from pytestlab.cli import replay_run
            # Parse arguments for replay run
            script_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
            session = None

            for i, arg in enumerate(sys.argv):
                if arg == "--session" and i + 1 < len(sys.argv):
                    session = Path(sys.argv[i + 1])

            if script_path and session:
                replay_run(script_path, session)
            else:
                rich.print("[bold red]Error: Missing required arguments for replay run[/bold red]")
                sys.exit(1)
    else:
        run_app()

if __name__ == "__main__":
    main()
