import inquirer
import typer
from pathlib import Path
from elx.tap import Tap
from elx.cli.utils import find_instances_of_type


def invoke(
    locator: Path,
    limit: int = typer.Option(3, help="Limit the number of records to ingest"),
):
    """
    Invoke a target or tap.

    Args:
        path (str): The path to the target or tap.
    """
    # Get all instances from foo that are of type Tap
    taps = {tap.executable: tap for tap in find_instances_of_type(locator, Tap)}

    questions = [
        inquirer.List(
            "tap",
            message="Which tap do you want to invoke?",
            choices=taps.keys(),
            carousel=True,
        ),
    ]

    tap_name = inquirer.prompt(questions)["tap"]

    tap = taps[tap_name]

    streams = [
        inquirer.List(
            "stream",
            message="Which stream do you want to invoke?",
            choices=["all", *[stream.name for stream in tap.streams]],
            default="all",
            carousel=True,
        ),
    ]

    stream_name = inquirer.prompt(streams)["stream"]

    tap.invoke([stream_name], limit=limit)
