import logging

_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    """Never log AGENT_TOKEN or any other secret."""
    logging.basicConfig(level=level, format=_FORMAT, force=True)
