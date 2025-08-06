import json
import os
from pathlib import Path

import inquirer
from rich.console import Console
from rich.table import Table
from rich.json import JSON
from elx.runner import Runner
from elx.cli.utils import obfuscate_secrets, find_instances_of_type
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn


def select_runner(runners: dict[str, Runner]) -> Runner:
    """
    Select a runner from a list of runners.
    """
    # If there are no runners found, exit
    if not runners:
        print("No runners found.")
        return

    questions = [
        inquirer.List(
            "runner",
            message="Which runner do you want to invoke?",
            choices=runners.keys(),
            carousel=True,
        ),
    ]

    # If there is only one runner, select it
    if len(runners) == 1:
        return list(runners.values())[0]

    # Otherwise, prompt the user to select a runner
    runner_name = inquirer.prompt(questions)["runner"]
    return runners[runner_name]


def debug(locator: str):
    """
    Debug an elx runner.
    """
    # Get all the runners from the variables
    runners = {
        runner.name: runner for runner in find_instances_of_type(locator, Runner)
    }

    runner = select_runner(runners)

    if not runner:
        return

    console = Console()

    table = Table(
        show_header=False,
        show_lines=True,
        highlight=True,
    )
    table.add_column("Setting", style="bold")
    table.add_column("Value")

    table.add_row(
        "Runner name",
        runner.name,
    )
    table.add_row(
        "Tap name",
        runner.tap.executable,
    )
    table.add_row(
        "Target name",
        runner.target.executable,
    )
    table.add_row(
        "State path",
        f"{runner.state_manager.base_path}/{runner.state_file_name}",
    )
    table.add_row(
        "State client",
        runner.state_manager.state_client.__class__.__name__,
    )
    table.add_row(
        "State",
        json.dumps(runner.load_state(), indent=2),
    )
    table.add_row(
        "Streams",
        ", ".join([stream.name for stream in runner.tap.catalog.streams]),
    )
    table.add_row(
        "Tap config",
        json.dumps(obfuscate_secrets(runner.tap.config), indent=2),
    )
    table.add_row(
        "Target config",
        json.dumps(obfuscate_secrets(runner.target.config), indent=2),
    )

    console.print(table)

    # runner.tap.invoke()

    # with Progress(
    #     "[progress.description]{task.description}",
    #     BarColumn(),
    #     "[progress.percentage]{task.percentage:>3.0f}%",
    #     TextColumn("[bold blue]{task.fields[stream]}"),
    #     # TimeElapsedColumn(),
    # ) as progress:
    #     task = progress.add_task(
    #         "Testing tap streams",
    #         stream="stream",
    #         total=len(runner.tap.streams),
    #     )

    #     for stream in runner.tap.streams:
    #         progress.update(task, advance=1, stream=stream.name)
    #         runner.tap.invoke([stream.name], limit=2, debug=False)
