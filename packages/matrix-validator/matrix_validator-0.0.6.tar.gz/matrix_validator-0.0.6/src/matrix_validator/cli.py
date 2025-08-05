"""CLI for matrix-validator."""

import logging
import sys

import click

from matrix_validator import __version__, validator_polars, validator_purepython, validator_schema

logger = logging.getLogger("matrix-validator")


@click.command()
@click.option(
    "--validator",
    type=click.Choice(["pandas", "python", "polars"], case_sensitive=False),
    default="polars",
    help="Pick validator implementation.",
)
@click.option("-c", "--config", type=click.Path(), required=False, help="Path to the config file.")
@click.option("-n", "--nodes", type=click.Path(), required=False, help="Path to the nodes TSV file.")
@click.option("-e", "--edges", type=click.Path(), required=False, help="Path to the edges TSV file.")
@click.option("-l", "--limit", type=click.INT, required=False, help="Rows to validate.  When not set, all rows are validated.")
@click.option(
    "--output-format",
    type=click.Choice(["txt", "md"], case_sensitive=False),
    default="txt",
    help="Format of the validation report.",
)
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet", is_flag=True)
@click.version_option(__version__)
def main(validator, config, nodes, edges, limit, output_format, verbose: int, quiet: bool):
    """Run the Matrix Validator CLI."""
    match verbose:
        case 2:
            level = logging.DEBUG
        case 1:
            level = logging.INFO
        case _:
            level = logging.WARNING

    if quiet:
        level = logging.ERROR

    logging.basicConfig(stream=sys.stdout, level=level)

    if quiet:
        logging.basicConfig(stream=sys.stdout, level=logging.FATAL)

    match validator:
        case "python":
            python(config, nodes, edges, limit, output_format)
        case "pandera":
            pandera(config, nodes, edges, limit, output_format)
        case "polars":
            polars(config, nodes, edges, limit, output_format)


def polars(config, nodes, edges, limit, output_format):
    """
    CLI for matrix-validator.

    This validates a knowledge graph using optional nodes and edges TSV files.
    """
    exit_code = 0
    try:
        validator = validator_polars.ValidatorPolarsFileImpl(nodes, edges, config)
        if output_format:
            validator.set_output_format(output_format)
        exit_code = validator.validate(limit)
    except Exception as e:
        logger.exception(f"Error during validation: {e}")
        click.echo("Validation failed. See logs for details.", err=True)
    sys.exit(exit_code)


def python(config, nodes, edges, limit, output_format):
    """
    CLI for matrix-validator.

    This validates a knowledge graph using optional nodes and edges TSV files.
    """
    exit_code = 0
    try:
        validator = validator_purepython.ValidatorPurePythonImpl(config)
        if output_format:
            validator.set_output_format(output_format)
        exit_code = validator.validate(nodes, edges, limit)
    except Exception as e:
        logger.exception(f"Error during validation: {e}")
        click.echo("Validation failed. See logs for details.", err=True)
    sys.exit(exit_code)


def pandera(config, nodes, edges, limit, output_format):
    """
    CLI for matrix-validator.

    This validates a knowledge graph using optional nodes and edges TSV files.
    """
    exit_code = 0
    try:
        validator = validator_schema.ValidatorPanderaImpl(config)
        if output_format:
            validator.set_output_format(output_format)
        exit_code = validator.validate(nodes, edges, limit)
    except Exception as e:
        logger.exception(f"Error during validation: {e}")
        click.echo("Validation failed. See logs for details.", err=True)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
