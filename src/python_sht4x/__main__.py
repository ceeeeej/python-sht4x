"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Python SHT4X."""


if __name__ == "__main__":
    main(prog_name="python-sht4x")  # pragma: no cover
