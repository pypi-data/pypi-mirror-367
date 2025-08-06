#!/usr/bin/env python3
import argparse
from pathlib import Path
from mcmicroprep.core import CorePipeline
from mcmicroprep.microscopes.olympus import OlympusHandler
from mcmicroprep.microscopes.rarecyte import RareCyteHandler

HANDLERS = {
    "olympus": OlympusHandler,
    "rarecyte": RareCyteHandler,
    # add more handlers here
}


def main():
    parser = argparse.ArgumentParser("Prepare data for MCMicro")
    parser.add_argument(
        "--microscope",
        choices=HANDLERS,
        required=True,
        help="Microscope vendor (e.g., olympus, rarecyte)",
    )
    parser.add_argument(
        "--image-root", required=True, help="Root folder containing slide directories"
    )
    args = parser.parse_args()

    handler = HANDLERS[args.microscope]()
    pipeline = CorePipeline(handler, Path(args.image_root))
    pipeline.run()


if __name__ == "__main__":
    main()
