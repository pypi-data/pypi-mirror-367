import logging
import os
import sys
from pathlib import Path

import click
import yaml

from highlighter.cli.logging import ColourStr
from highlighter.client import TrainingConfigType
from highlighter.client.gql_client import HLClient
from highlighter.trainers import _scaffold

logger = logging.getLogger(__name__)


def _get_trainer(training_run_dir: Path, hl_training_config: TrainingConfigType):
    with (training_run_dir / ".hl" / "trainer-type").open("r") as f:
        trainer_type = _scaffold.TrainerType(f.readline().strip())

    if (training_run_dir / "trainer.py").exists():
        Trainer = _scaffold.load_trainer_module(training_run_dir).Trainer
    elif "yolo" in trainer_type:
        from highlighter.trainers.yolov11.trainer import YoloV11Trainer as Trainer
    else:
        logger.error(f"Unable to determine trainer from '{trainer_type}'")
        sys.exit(1)
    return Trainer(training_run_dir, hl_training_config, trainer_type)


@click.group("train")
@click.pass_context
def train_group(ctx):
    pass


def _validate_training_run_dir(training_run_dir: Path):
    if not training_run_dir.exists():
        logger.error(f"training_run_dir {training_run_dir} does not exist.")
        sys.exit(1)

    try:
        int(training_run_dir.stem)
        return training_run_dir
    except ValueError:
        logger.error(
            f"Invalid training_run_dir {training_run_dir}. Should be 'ml_training/<TRAINING_RUN_ID>'"
        )
        sys.exit(1)


@train_group.command("start")
@click.argument("training-run-dir", required=False, default=".")
@click.pass_context
def train_start(ctx, training_run_dir):

    client: HLClient = ctx.obj["client"]

    training_run_dir = Path(training_run_dir).absolute()
    training_run_dir = _validate_training_run_dir(training_run_dir)
    training_run_id = training_run_dir.stem

    client: HLClient = ctx.obj["client"]
    highlighter_training_config = TrainingConfigType.from_highlighter(client, int(training_run_id))
    trainer = _get_trainer(training_run_dir, highlighter_training_config)

    combined_ds = trainer.get_datasets(client)

    if trainer.training_data_dir.exists():
        _scaffold.ask_to_remove(trainer.training_data_dir)

    os.chdir(training_run_dir)
    _, artefact_path, _ = trainer._train(combined_ds)
    click.echo(f"Training {training_run_id} complete")
    cmd = ColourStr.green(
        f"hl training-run artefact create -i {training_run_id} -a {artefact_path.relative_to(Path.cwd())}"
    )
    click.echo(f"Next run: `{cmd}` to upload to Highlighter")


@train_group.command("evaluate")
@click.argument("training-run-dir", required=False, default=".")
@click.argument("checkpoint", required=True, type=click.Path(dir_okay=False))
@click.argument("config", required=True, type=click.Path(dir_okay=False))
@click.pass_context
def train_evaluate(ctx, training_run_dir, checkpoint, config):
    training_run_dir = Path(training_run_dir).absolute()
    training_run_dir = _validate_training_run_dir(training_run_dir)
    training_run_id = training_run_dir.stem

    client: HLClient = ctx.obj["client"]
    highlighter_training_config = TrainingConfigType.from_highlighter(client, int(training_run_id))
    trainer = _get_trainer(training_run_dir, highlighter_training_config)

    with open(config, "r") as f:
        data_yaml_path = yaml.safe_load(f)["data"]
        with open(data_yaml_path, "r") as g:
            classes = yaml.safe_load(g)["names"]

    object_classes = [(k, v) for k, v in classes.items()]
    object_classes = sorted(object_classes, key=lambda x: x[0])
    object_classes = [x[1] for x in object_classes]

    results = trainer.evaluate(checkpoint, object_classes, cfg_path=config)
    click.echo(results)


@train_group.command("export")
@click.argument("training-run-dir", required=False, default=".")
@click.argument("checkpoint", required=True, type=click.Path(dir_okay=False))
@click.argument("config", required=True, type=click.Path(dir_okay=False))
@click.pass_context
def train_export(ctx, training_run_dir, checkpoint, config):
    training_run_dir = Path(training_run_dir).absolute()
    training_run_dir = _validate_training_run_dir(training_run_dir)
    training_run_id = training_run_dir.stem

    client: HLClient = ctx.obj["client"]
    highlighter_training_config = TrainingConfigType.from_highlighter(client, int(training_run_id))
    trainer = _get_trainer(training_run_dir, highlighter_training_config)

    artefact_path = trainer._export(checkpoint)

    click.echo(f"Export {checkpoint} complete")
    cmd = ColourStr.green(
        f"hl training-run artefact create -i {training_run_id} -a {artefact_path.relative_to(Path.cwd())}"
    )
    click.echo(f"Next run: `{cmd}` to upload to Highlighter")
