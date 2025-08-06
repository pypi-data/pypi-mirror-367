#!/usr/bin/python3
import os
import sys
from json import JSONDecodeError

import umu_commander.configuration as config
import umu_commander.database as db
from umu_commander import tracking, umu_config
from umu_commander.classes import ExitCode
from umu_commander.configuration import CONFIG_DIR, CONFIG_NAME


def print_help():
    print(
        "umu-commander is an interactive CLI tool to help you manage Proton versions used by umu, as well as create enhanced launch configs.",
        "",
        "For details, explanations, and more, see the README.md file, or visit https://github.com/Mpaxlamitsounas/umu-commander.",
        sep="\n",
    )


def main() -> ExitCode:
    try:
        config.load()
    except (JSONDecodeError, KeyError):
        config_path: str = os.path.join(CONFIG_DIR, CONFIG_NAME)
        print(f"Config file at {config_path} could not be read.")
        os.rename(config_path, os.path.join(CONFIG_DIR, CONFIG_NAME + ".old"))

    try:
        db.load()
    except JSONDecodeError:
        db_path: str = os.path.join(config.DB_DIR, config.DB_NAME)
        print(f"Tracking file at {db_path} could not be read.")
        os.rename(db_path, os.path.join(config.DB_DIR, config.DB_NAME + ".old"))

    if len(sys.argv) == 1:
        print_help()
        return ExitCode.SUCCESS.value

    verb: str = sys.argv[1]
    match verb:
        case "track":
            tracking.track()
        case "untrack":
            tracking.untrack()
        case "users":
            tracking.users()
        case "delete":
            tracking.delete()
        case "create":
            umu_config.create()
        case "run":
            umu_config.run()
        case _:
            print("Invalid verb.")
            print_help()
            return ExitCode.INVALID_SELECTION.value

    tracking.untrack_unlinked()
    db.dump()
    config.dump()

    return ExitCode.SUCCESS.value


if __name__ == "__main__":
    exit(main())
