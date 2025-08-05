"""
HXRSnD IPython Shell
"""
import logging
import os  # nos
import socket
import sys
import warnings
from importlib import reload  # noqa
from pathlib import Path  # noqa
from typing import Any, Dict

from IPython import start_ipython

# Ignore python warnings (Remove when ophyd stops warning about 'signal_names')
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


def _load_scripts_and_devices() -> Dict[str, Any]:
    try:
        import snd_devices  # noqa
    except Exception as e:
        logger.exception(
            "Failed to create SplitAndDelay class on '%s'. Got error: %s",
            socket.gethostname(), e
        )
        raise

    logger.warning(
        "Loaded devices: %s",
        ", ".join(
            sorted(device for device in dir(snd_devices) if not device.startswith("_"))
        ),
    )

    logger.debug(
        "Successfully created SplitAndDelay class on '%s'",
        socket.gethostname()
    )

    # Try importing from the scripts file if we succeeded at making the snd
    # object
    try:
        import scripts  # noqa
    except Exception as e:
        # There was some problem in the file
        logger.exception(
            "Failed to load scripts file, got the following error: %s",
            e
        )
        raise

    logger.warning(
        "Loaded scripts: %s",
        ", ".join(
            sorted(script for script in dir(scripts) if not script.startswith("_"))
        ),
    )
    logger.info(
        "Successfully initialized new SnD session on '{}'".format(
            socket.gethostname()
        )
    )

    scripts_and_devices = {}
    scripts_and_devices.update(vars(snd_devices))
    scripts_and_devices.update(vars(scripts))
    return scripts_and_devices


def _maybe_modify_path():
    try:
        import scripts  # noqa
        import snd_devices  # noqa
    except Exception:
        logger.warning(
            "Failed to pre-import snd_devices/scripts; "
            "adding the working directory to the path as maybe things are "
            "there."
        )
        sys.path.insert(0, os.path.abspath(os.curdir))


def main():
    logging.basicConfig()
    _maybe_modify_path()
    devices = _load_scripts_and_devices()
    namespace = dict(globals())
    namespace.update(devices)
    start_ipython(argv=["--quick"], user_ns=devices)


if __name__ == "__main__":
    main()
