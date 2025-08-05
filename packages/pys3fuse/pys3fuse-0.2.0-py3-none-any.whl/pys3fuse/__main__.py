import logging
from argparse import ArgumentParser

from fuse import FUSE

from .core.log_config import (
    file_queue_listener,
    pys3fuse_logger as logger,
    queue_listener,
)
from .fs.passthrough import Passthrough

if __name__ == "__main__":
    queue_listener.start()
    file_queue_listener.start()

    parser = ArgumentParser("PyS3FUSE")

    parser.add_argument(
        "source",
        type=str,
        help="Directory tree to mirror",
    )
    parser.add_argument(
        "mountpoint",
        type=str,
        help="Where to mount the file system",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debugging output",
    )

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        FUSE(
            Passthrough(args.source),
            args.mountpoint,
            foreground=True,
            allow_other=True,
        )
    finally:
        queue_listener.stop()
        file_queue_listener.start()
