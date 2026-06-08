import argparse
import time
import schedule
import json
import os
from rich.console import Console
from rich.panel import Panel

from baseline import create_baseline, load_baseline, compare_to_baseline
from hasher import hash_directory
from logger import setup_logger, log_alert, log_clean
from monitor import start_monitor

console = Console()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config():
    config_path = os.path.join(BASE_DIR, "config.json")
    with open(config_path) as f:
        config = json.load(f)
    config["baseline_file"] = os.path.join(BASE_DIR, config["baseline_file"])
    config["log_file"] = os.path.join(BASE_DIR, config["log_file"])
    return config

def run_manual_scan(config, baseline):
    """Do a full re-scan and compare against baseline."""
    current = {}
    for path in config["watch_paths"]:
        current.update(hash_directory(path, config["ignored_extensions"]))

    changes = compare_to_baseline(current, baseline)

    if not changes:
        console.print("[green]✓ All files intact. No changes detected.[/green]")
    else:
        console.print(f"\n[bold red]⚠ {len(changes)} change(s) detected:[/bold red]\n")
        for change in changes:
            log_alert(change)

    return changes

def main():
    parser = argparse.ArgumentParser(description="File Integrity Monitoring System")
    parser.add_argument("--report", action="store_true", help="Print summary report")
    parser.add_argument("--baseline", action="store_true", help="Create a new baseline snapshot")
    parser.add_argument("--scan",     action="store_true", help="Run a one-time manual scan")
    parser.add_argument("--watch",    action="store_true", help="Start real-time monitoring")
    parser.add_argument("--restore", type=str, metavar="FILEPATH", help="Restore a file to its baseline state")
    args = parser.parse_args()

    config = load_config()
    setup_logger(config["log_file"])

    console.print(Panel.fit("[bold cyan]File Integrity Monitoring System[/bold cyan]", border_style="cyan"))

    if args.baseline:
        console.print("[yellow]Creating baseline snapshot...[/yellow]")
        snapshot = create_baseline(config)
        count = len(snapshot["files"])
        console.print(f"[green]✓ Baseline created: {count} files indexed.[/green]")

    elif args.scan:
        baseline = load_baseline(config)
        if baseline is None:
            console.print("[red]No baseline found. Run with --baseline first.[/red]")
            return
        run_manual_scan(config, baseline)

    elif args.watch:
        baseline = load_baseline(config)
        if not baseline:
            console.print("[red]No baseline found. Run with --baseline first.[/red]")
            return

        console.print(f"[green]Watching {len(config['watch_paths'])} path(s). Press Ctrl+C to stop.[/green]\n")
        observer = start_monitor(baseline, config)

        interval = config.get("check_interval_seconds", 60)
        schedule.every(interval).seconds.do(run_manual_scan, config, baseline)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            console.print("\n[yellow]FIMS stopped.[/yellow]")
        observer.join()
    elif args.report:
        from logger import print_report
        print_report(config)
    

    elif args.restore:
        from baseline import restore_file
        path = args.restore
        success = restore_file(path)
        if success:
            console.print(f"[green]✓ Restored: {path}[/green]")
        else:
            console.print(f"[red]✗ No baseline copy found for: {path}[/red]")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()