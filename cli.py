import logging
from pathlib import Path

import click
from warn import Runner, utils
import vcr

WARN_DATA_DIR = Path("data")
WARN_CACHE_DIR = Path("data/files")


@click.command()
@click.argument("scrapers", nargs=-1, required=False)
@click.option(
    "--list",
    default=False,
    help="Lists all scrapers",
    is_flag=True,
)
@click.option(
    "--record_mode",
    "-r",
    default="new_episodes",
    # see https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    type=click.Choice(("once", "new_episodes", "none", "all"), case_sensitive=True),
    help="Sets the mode for recording and replaying HTTP requests",
)
def main(
    scrapers: list,
    data_dir: Path = WARN_DATA_DIR,
    cache_dir: Path = WARN_CACHE_DIR,
    delete: bool = False,
    log_level: str = "DEBUG",
    record_mode: str = "new_episodes",
    list: bool = False,
):
    if list:
        print(",".join([scraper.upper() for scraper in utils.get_all_scrapers()]))
        return

    # Set higher log-level on third-party libs that use DEBUG logging,
    # In order to limit debug logging to our library
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("pdfminer").setLevel(logging.WARNING)
    logging.getLogger("vcr").setLevel(logging.WARNING)

    # Local logging config
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(message)s")

    runner = Runner(data_dir, cache_dir)

    for scrape in scrapers:
        with vcr.use_cassette(f"data/cassettes/{scrape}.yaml", record_mode=record_mode):
            runner.scrape(scrape)


if __name__ == "__main__":
    main()
