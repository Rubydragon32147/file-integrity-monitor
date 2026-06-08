import logging
import os
from rich.console import Console
from rich.text import Text

console = Console()

def setup_logger(log_file: str):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def log_alert(change: dict):
    """Log a change event to file and print a colored alert to terminal."""
    change_type = change["type"]
    path = change["path"]
    old_h = (change["old_hash"] or "")[:12]
    new_h = (change["new_hash"] or "")[:12]

    # File log
    msg = f"{change_type} | {path} | old={old_h or 'N/A'} | new={new_h or 'N/A'}"
    logging.warning(msg)

    # Terminal output with rich
    color_map = {"MODIFIED": "red", "DELETED": "bold red", "NEW": "yellow"}
    color = color_map.get(change_type, "white")

    line = Text()
    line.append(f"[{change_type}] ", style=f"bold {color}")
    line.append(path, style="white")
    if old_h:
        line.append(f"\n  old: {old_h}...", style="dim")
    if new_h:
        line.append(f"  new: {new_h}...", style="dim")
    console.print(line)

def log_clean(path: str):
    console.print(f"[green]✓[/green] Integrity OK: {path}")

from rich.table import Table
from rich.panel import Panel
import json

def print_report(config: dict):
    """Read fims.log and print a formatted summary report."""
    log_file = config["log_file"]
    baseline_file = config["baseline_file"]

    # Count alerts from log file
    modified = deleted = new = 0
    last_scan = "No scans yet"

    if os.path.exists(log_file):
        with open(log_file) as f:
            for line in f:
                if "MODIFIED" in line:
                    modified += 1
                elif "DELETED" in line:
                    deleted += 1
                elif "NEW" in line:
                    new += 1
                # Grab timestamp from last line
                if " | " in line:
                    last_scan = line.split(" | ")[0].strip()

    # Count files in baseline
    total_files = 0
    baseline_created = "No baseline yet"
    if os.path.exists(baseline_file):
        with open(baseline_file) as f:
            data = json.load(f)
            total_files = len(data.get("files", {}))
            baseline_created = data.get("created_at", "Unknown")

    # Build report table
    console.print(Panel.fit("[bold cyan]FIMS Summary Report[/bold cyan]", border_style="cyan"))

    table = Table(show_header=True, header_style="bold cyan", border_style="dim")
    table.add_column("Metric", style="white", width=30)
    table.add_column("Value", style="bold")

    table.add_row("Files in baseline", str(total_files))
    table.add_row("Baseline created", baseline_created)
    table.add_row("Last log entry", last_scan)
    table.add_row("", "")
    table.add_row("[red]MODIFIED alerts[/red]", f"[red]{modified}[/red]")
    table.add_row("[bold red]DELETED alerts[/bold red]", f"[bold red]{deleted}[/bold red]")
    table.add_row("[yellow]NEW FILE alerts[/yellow]", f"[yellow]{new}[/yellow]")
    table.add_row("", "")
    table.add_row("Total alerts", str(modified + deleted + new))

    console.print(table)