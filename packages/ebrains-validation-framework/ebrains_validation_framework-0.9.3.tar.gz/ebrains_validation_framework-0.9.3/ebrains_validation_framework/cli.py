"""


"""

import click

from . import TestLibrary
from .utils import run_test, run_test_offline, run_test_standalone, prepare_run_test_offline

"""
$ validate run --model=bianchi_2012@SciUnit-v1.0 --test=Hippocampus_CA1_BackpropagatingAPTest@1.3.5 --store-results
$ validate prepare --model=bianchi_2012@SciUnit-v1.0 --test=Hippocampus_CA1_BackpropagatingAPTest@1.3.5 --output=test_config.json
$ validate run --use-config=test_config.json --output=validation_output.zip
$ validate store validation_output.zip
"""


@click.group()
def main():
    pass


@main.command()
@click.option("--model", required=True)
@click.option("--test", required=True)
@click.option("--project")
def run(model, test, project):
    """Example script."""
    click.echo(f"Validating {model} using {test}.")
    if project:
        click.echo(f"Storing results to '{project}'")
    else:
        click.echo("Not storing results")

    # todo: error handling for format of "model"
    model_alias, model_version = model.split("@")
    test_alias, test_version = test.split("@")

    response, score = run_test_standalone(
        model="",
        test_alias=test_alias,
        test_version=test_version,
        storage_collab_id=project,
        storage_type="bucket",
        register_result=bool(project),
    )

@main.command()
@click.option("--username", required=True)
@click.option("--password")
def login(username, password):
    test_library = TestLibrary(username, password)
    # todo: handle authentication failure
