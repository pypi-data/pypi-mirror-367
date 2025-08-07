import logging
import os
from importlib.metadata import version
from pathlib import Path

from cement import CaughtSignal, Controller, ex
from dotenv import load_dotenv
from hmd_cli_tools.hmd_cli_tools import get_env_var

from .log import build_dd_sender, get_dd_tags, setup_root_logger

VERSION_BANNER = """
hmd librarian-sync-manager version: {}
"""


class LocalController(Controller):
    class Meta:
        label = "librarian_sync_manager"
        stacked_type = "nested"
        stacked_on = "base"

        # text displayed at the top of --help output
        description = "Sync local files with librarian"

        arguments = (
            (
                ["-v", "--version"],
                {
                    "help": "display the version of the librarian-sync-manager command.",
                    "action": "version",
                    "version": VERSION_BANNER.format(
                        version("hmd_cli_librarian_sync_manager")
                    ),
                },
            ),
        )

    def _default(self):
        """Default action if no sub-command is passed."""
        self.app.args.print_help()

    @ex(
        help="read local sqlite database and push files to librarian",
        arguments=[
            (
                ["--config-file"],
                {"action": "store", "dest": "config_file", "required": False},
            )
        ],
    )
    def sync(self):
        hmd_home = Path(os.path.expandvars(get_env_var("HMD_HOME")))
        config_path_default = hmd_home / ".config" / "librarian-sync.json"
        log_file_path = hmd_home / "log" / "librarian-sync-manager.log"
        log_level = logging.INFO
        if self.app.pargs.debug:
            log_level = logging.DEBUG
        setup_root_logger(log_file_path, log_level)

        logger = logging.getLogger(__name__)

        send_datadog_event = build_dd_sender(logger)
        from .hmd_cli_librarian_sync_manager import LibrarianSyncManager

        try:
            env_path = hmd_home / ".config" / "hmd.env"
            if Path(env_path).exists():
                load_dotenv(dotenv_path=Path(env_path), override=True)
            config_path = os.environ.get("HMD_LIBRARIAN_SYNC_MANAGER_CONFIG")
            if not config_path:
                config_path = (
                    Path(self.app.pargs.config_file)
                    if self.app.pargs.config_file is not None
                    else config_path_default
                )
            logger.info(f"config: {config_path}")
            manager = LibrarianSyncManager(config_path)
            manager.sync()
        except CaughtSignal as cs:
            logger.error("Caught signal", exc_info=cs)
            send_datadog_event(
                event_type="error",
                data="Librarian Sync Manager caught signal during sync",
                ex=str(cs),
                tags=get_dd_tags(),
            )
        except BaseException as e:
            logger.error("Execution failed", exc_info=e)
            send_datadog_event(
                event_type="error",
                data="Librarian Sync Manager failed during sync",
                ex=str(e),
                tags=get_dd_tags(),
            )
        logger.info("exiting")

    @ex(
        help="watch the local sqlite database and push files to librarian",
        arguments=[
            (
                ["--config-file"],
                {"action": "store", "dest": "config_file", "required": False},
            )
        ],
    )
    def watch(self):
        hmd_home = Path(os.path.expandvars(get_env_var("HMD_HOME")))
        log_file_path = hmd_home / "log" / "librarian-sync-manager.log"
        log_level = logging.INFO
        if self.app.pargs.debug:
            log_level = logging.DEBUG
        setup_root_logger(log_file_path, log_level)

        logger = logging.getLogger(__name__)
        send_datadog_event = build_dd_sender(logger)
        from .hmd_cli_librarian_sync_manager import LibrarianSyncManager

        manager = None
        try:
            hmd_home = Path(os.path.expandvars(get_env_var("HMD_HOME")))
            env_path = hmd_home / ".config" / "hmd.env"
            if Path(env_path).exists():
                load_dotenv(dotenv_path=Path(env_path), override=True)
            config_path_default = hmd_home / ".config" / "librarian-sync.json"
            config_path = os.environ.get("HMD_LIBRARIAN_SYNC_MANAGER_CONFIG")
            logger.info(f"config path: {config_path}")
            if not config_path:
                config_path = (
                    Path(self.app.pargs.config_file)
                    if self.app.pargs.config_file is not None
                    else config_path_default
                )
            manager = LibrarianSyncManager(config_path)
            manager.start()
        except CaughtSignal as cs:
            logger.error("Caught signal", exc_info=cs)
            send_datadog_event(
                event_type="error",
                data="Librarian Sync Manager caught signal during watch",
                ex=str(cs),
                tags=get_dd_tags(),
            )
            if manager:
                manager.stop()
        except BaseException as e:
            logger.error("Execution failed", exc_info=e)
            send_datadog_event(
                event_type="error",
                data="Librarian Sync Manager failed during watch",
                ex=str(e),
                tags=get_dd_tags(),
            )
            if manager:
                manager.stop()
        logger.info("exiting")
