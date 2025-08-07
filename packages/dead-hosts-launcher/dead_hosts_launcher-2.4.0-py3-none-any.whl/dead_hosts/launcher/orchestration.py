"""
Dead Hosts's launcher - The launcher of the Dead-Hosts infrastructure.

Provides the orchestration logic. In other words, put everything
together to process a test.

Author:
    Nissar Chababy, @funilrys, contactTATAfunilrysTODTODcom

Project link:
    https://github.com/dead-hosts/infrastructure-launcher

License:
::

    MIT License

    Copyright (c) 2019, 2020, 2021, 2022, 2023, 2024, 2025 Dead Hosts Contributors
    Copyright (c) 2019, 2020. 2021, 2022, 2023, 2024 Nissar Chababy

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import logging
import os
import sys
import tempfile
from datetime import datetime, timezone
from typing import Optional

import PyFunceble
import PyFunceble.facility
import requests
from PyFunceble.cli.continuous_integration.exceptions import (
    ContinuousIntegrationException,
    StopExecution,
)
from PyFunceble.cli.continuous_integration.github_actions import GitHubActions
from PyFunceble.helpers.download import DownloadHelper
from PyFunceble.helpers.environment_variable import EnvironmentVariableHelper
from PyFunceble.helpers.file import FileHelper

import dead_hosts.launcher.defaults.envs
import dead_hosts.launcher.defaults.paths
from dead_hosts.launcher.authorization import Authorization
from dead_hosts.launcher.command import Command
from dead_hosts.launcher.info_manager import InfoManager
from dead_hosts.launcher.platform import PlatformOrchestration
from dead_hosts.launcher.updater.all import execute_all_updater
from dead_hosts.launcher.updater.pyfunceble_config import PyFuncebleConfigUpdater


class Orchestration:
    """
    Orchester the test launch.
    """

    info_manager: Optional[InfoManager] = None
    authorization_handler: Optional[Authorization] = None

    origin_file: Optional[FileHelper] = None
    output_file: Optional[FileHelper] = None

    def __init__(
        self,
        save: bool = False,
        end: bool = False,
        authorize: bool = False,
        update: bool = False,
    ) -> None:
        self.info_manager = InfoManager()

        git_name = EnvironmentVariableHelper("GIT_NAME")
        git_email = EnvironmentVariableHelper("GIT_EMAIL")

        if git_email.exists() and "funilrys" in git_email.get_value():
            git_name.set_value(dead_hosts.launcher.defaults.envs.GIT_NAME)
            git_email.set_value(dead_hosts.launcher.defaults.envs.GIT_EMAIL)

        EnvironmentVariableHelper("PYFUNCEBLE_OUTPUT_LOCATION").set_value(
            self.info_manager.WORKSPACE_DIR
            if self.info_manager.platform_optout is True
            else os.path.join(tempfile.gettempdir(), "pyfunceble", "output")
        )

        EnvironmentVariableHelper("PYFUNCEBLE_CONFIG_DIR").set_value(
            self.info_manager.pyfunceble_config_dir
        )

        self.authorization_handler = Authorization(self.info_manager)

        self.origin_file = FileHelper(
            os.path.join(
                self.info_manager.WORKSPACE_DIR,
                dead_hosts.launcher.defaults.paths.ORIGIN_FILENAME,
            )
        )

        self.output_file = FileHelper(
            os.path.join(
                self.info_manager.WORKSPACE_DIR,
                dead_hosts.launcher.defaults.paths.OUTPUT_FILENAME,
            )
        )

        if not authorize:
            logging.info("Origin file: %r", self.origin_file.path)
            logging.info("Output file: %r", self.output_file.path)

        if authorize:
            self.run_authorize()
        elif save:
            self.run_autosave()
        elif update:
            execute_all_updater(self.info_manager)
        elif end:
            self.run_end()
        else:
            logging.info("Checking authorization to run.")

            if EnvironmentVariableHelper("PLATFORM_WORKER").get_value():
                self.run_platform_worker()
            elif self.authorization_handler.is_platform_authorized():
                self.run_platform_sync()
            elif self.authorization_handler.is_test_authorized():
                PyFunceble.facility.ConfigLoader.start()
                self.fetch_file_to_test()

                self.run_test()
            else:
                logging.info(
                    "Not authorized to run a test until %r (current time) > %r",
                    datetime.now(),
                    self.authorization_handler.next_authorization_time,
                )
                sys.exit(0)

    def fetch_file_to_test(self) -> "Orchestration":
        """
        Provides the latest version of the file to test.
        """

        if self.authorization_handler.is_refresh_authorized():
            logging.info("We are authorized to refresh the lists! Let's do that.")
            logging.info("Raw Link: %r", self.info_manager.raw_link)

            if self.info_manager.raw_link:
                DownloadHelper(self.info_manager.raw_link).download_text(
                    destination=self.origin_file.path
                )

                logging.info(
                    "Could get the new version of the list. Updating the download time."
                )

                self.info_manager["last_download_datetime"] = datetime.now(timezone.utc)

                try:
                    self.info_manager["last_download_timestamp"] = self.info_manager[
                        "last_download_datetime"
                    ].timestamp()
                except (OSError, ValueError, OverflowError):
                    self.info_manager["last_download_timestamp"] = 0.0
            elif self.origin_file.exists():
                logging.info(
                    "Raw link not given or is empty. Let's work with %r.",
                    self.origin_file.path,
                )

                self.origin_file.read()

                logging.info("Emptying the download time.")

                self.info_manager["last_download_datetime"] = datetime.fromtimestamp(0)
                try:
                    self.info_manager["last_download_timestamp"] = self.info_manager[
                        "last_download_datetime"
                    ].timestamp()
                except (OSError, ValueError, OverflowError):
                    self.info_manager["last_download_timestamp"] = 0.0
            else:
                logging.info(
                    "Could not find %s. Generating empty content to test.",
                    self.origin_file.path,
                )

                self.origin_file.write("# No content yet.", overwrite=True)

                logging.info("Emptying the download time.")

                self.info_manager["last_download_datetime"] = datetime.fromtimestamp(0)

                try:
                    self.info_manager["last_download_timestamp"] = self.info_manager[
                        "last_download_datetime"
                    ].timestamp()
                except (OSError, ValueError, OverflowError):
                    self.info_manager["last_download_timestamp"] = 0.0

            logging.info("Updated %r.", self.origin_file.path)

        return self

    def run_platform_worker(self):
        """
        Run a test of the input list.
        """

        # Ensure that everything is up-to-date.
        execute_all_updater(self.info_manager)

        self.write_trigger()

        logging.info("Starting PyFunceble %r ...", PyFunceble.__version__)

        EnvironmentVariableHelper("PYFUNCEBLE_BYPASS_BYPASS").set_value("True")

        Command("pyfunceble platform").run_to_stdout()

        if not dead_hosts.launcher.defaults.envs.GITHUB_TOKEN:
            self.run_end()

    def run_test(self):
        """
        Run a test of the input list.
        """

        if not self.info_manager.currently_under_test:
            self.info_manager["currently_under_test"] = True

            self.info_manager["start_datetime"] = datetime.now(timezone.utc)

            try:
                self.info_manager["start_timestamp"] = self.info_manager[
                    "start_datetime"
                ].timestamp()
            except (OSError, ValueError, OverflowError):
                self.info_manager["start_timestamp"] = 0.0

            self.info_manager["finish_datetime"] = datetime.fromtimestamp(0)

            try:
                self.info_manager["finish_timestamp"] = self.info_manager[
                    "finish_datetime"
                ].timestamp()
            except (OSError, ValueError, OverflowError):
                self.info_manager["finish_timestamp"] = 0.0

        self.info_manager["latest_part_start_datetime"] = datetime.now(timezone.utc)

        try:
            self.info_manager["latest_part_start_timestamp"] = self.info_manager[
                "latest_part_start_datetime"
            ].timestamp()
        except (OSError, ValueError, OverflowError):
            self.info_manager["latest_part_start_timestamp"] = 0.0

        self.info_manager["latest_part_finish_datetime"] = datetime.fromtimestamp(0)

        try:
            self.info_manager["latest_part_finish_timestamp"] = self.info_manager[
                "latest_part_finish_datetime"
            ].timestamp()
        except (OSError, ValueError, OverflowError):
            self.info_manager["latest_part_finish_timestamp"] = 0.0

        logging.info("Updated all timestamps.")
        logging.info("Starting PyFunceble %r ...", PyFunceble.__version__)

        Command(f"pyfunceble -f {self.origin_file.path}").run_to_stdout()

        self.write_trigger()
        if not dead_hosts.launcher.defaults.envs.GITHUB_TOKEN:
            self.run_end()

    def run_autosave(self):
        """
        Run the autosave logic of the administration file.

        .. warning::
            This is just about the administration file not PyFunceble.
        """

        self.info_manager["latest_part_finish_datetime"] = datetime.now(timezone.utc)
        try:
            self.info_manager["latest_part_finish_timestamp"] = self.info_manager[
                "latest_part_finish_datetime"
            ].timestamp()
        except (OSError, ValueError, OverflowError):
            self.info_manager["latest_part_finish_timestamp"] = 0.0

        self.write_trigger()

        logging.info("Updated all timestamps.")

    def run_end(self):
        """
        Run the end logic.
        """

        self.info_manager["currently_under_test"] = False

        self.info_manager["latest_part_finish_datetime"] = datetime.now(timezone.utc)

        try:
            self.info_manager["latest_part_finish_timestamp"] = self.info_manager[
                "latest_part_finish_datetime"
            ].timestamp()
        except (OSError, ValueError, OverflowError):
            self.info_manager["latest_part_finish_timestamp"] = 0.0

        self.info_manager["finish_datetime"] = self.info_manager[
            "latest_part_finish_datetime"
        ]
        try:
            self.info_manager["finish_timestamp"] = self.info_manager[
                "finish_datetime"
            ].timestamp()
        except (OSError, ValueError, OverflowError):
            self.info_manager["finish_timestamp"] = 0.0

        logging.info("Updated all timestamps and indexes that needed to be updated.")

        pyfunceble_active_list = FileHelper(
            os.path.join(
                self.info_manager.WORKSPACE_DIR,
                "output",
                dead_hosts.launcher.defaults.paths.ORIGIN_FILENAME,
                "domains",
                "ACTIVE",
                "list",
            )
        )

        logging.info("PyFunceble ACTIVE list output: %s", pyfunceble_active_list.path)

        if pyfunceble_active_list.exists():
            logging.info(
                "%s exists, getting and formatting its content.",
                pyfunceble_active_list.path,
            )

            self.output_file.write(
                "\n".join(dead_hosts.launcher.defaults.paths.OUTPUT_FILE_HEADER)
                + "\n\n",
                overwrite=True,
            )

            with pyfunceble_active_list.open("r", encoding="utf-8") as file_stream:
                for line in file_stream:
                    if line.startswith("#"):
                        continue

                    self.output_file.write(line)

            self.output_file.write("\n")

            logging.info("Updated of the content of %r", self.output_file.path)

        self.write_trigger()

    def _fetch_workflows(self, token, repo):
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

        if not token:
            del headers["Authorization"]

        req = requests.get(
            url=f"https://api.github.com/repos/{repo}/actions/workflows",
            headers=headers,
            timeout=30.0,
        )

        req.raise_for_status()

        result = {}

        for data in req.json()["workflows"]:
            result[data["id"]] = data

        return result

    def _is_job_running(self, token, repo):
        workflows = self._fetch_workflows(token, repo)
        ignore_status = [
            "completed",
            "cancelled",
            "failure",
            "neutral",
            "skipped",
            "success",
            "timed_out",
        ]
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

        if not token:
            del headers["Authorization"]

        req = requests.get(
            url=f"https://api.github.com/repos/{repo}/actions/runs",
            headers=headers,
            timeout=30.0,
        )

        req.raise_for_status()

        response = req.json()["workflow_runs"]

        for data in response:
            if data["status"] in ignore_status:
                continue

            workflow_name = workflows[data["workflow_id"]]["name"].lower()

            if "checker" in workflow_name or "auth" in workflow_name:
                continue

            return True

        return False

    def write_trigger(self):
        """
        Write the trigger file.
        """

        with open(
            os.path.join(self.info_manager.WORKSPACE_DIR, ".trigger"),
            "w",
            encoding="utf-8",
        ) as file_stream:
            logging.info("Writing into: %s", file_stream.name)
            file_stream.write(str(datetime.now(timezone.utc).timestamp()) + "\n")

    def run_authorize(self):
        """
        Authorized and proceed the scheduling.
        """

        if not dead_hosts.launcher.defaults.envs.GITHUB_TOKEN:
            logging.critical("Cannot authorize: Token not found.")
            return None

        if self._is_job_running(
            token=dead_hosts.launcher.defaults.envs.GITHUB_TOKEN,
            repo=self.info_manager.repo,
        ):
            logging.critical("Cannot authorize: Job running.")
            return None

        try:
            ci_engine = GitHubActions(
                commit_message="[Dead-Hosts::Infrastructure][AuthChecker]"
            )
            ci_engine.init()
        except ContinuousIntegrationException:
            pass

        execute_all_updater(self.info_manager)

        self.write_trigger()

        try:
            ci_engine.apply_commit()
        except (StopExecution, ContinuousIntegrationException):
            pass

        logging.info("Successfully authorized.")

        return True

    def run_platform_sync(self):
        """
        Run the synchronization / Download against the platform.
        """

        logging.info("Launching the platform synchronization.")

        commit_message = PyFuncebleConfigUpdater.get_commit_message(
            f"[Final/Result][Dead-Hosts::"
            f"{dead_hosts.launcher.defaults.paths.GIT_BASE_NAME}]",
            ping=self.info_manager.get_ping_for_commit(),
        )

        try:
            ci_engine = GitHubActions(
                commit_message=commit_message, end_commit_message=commit_message
            )
            ci_engine.init()
        except ContinuousIntegrationException:
            pass

        try:
            # The commit is one of the last one.
            ci_engine.bypass()
        except (StopExecution, ContinuousIntegrationException):
            logging.info("No need to synchronize.")
            sys.exit(0)

        execute_all_updater(self.info_manager)

        platform = PlatformOrchestration(self.info_manager)

        # We upload the local information to the platform.
        platform.upload()

        try:
            # Download what's available - yet
            platform.download()
            self.write_trigger()
            ci_engine.apply_end_commit()
        except (StopExecution, ContinuousIntegrationException):
            pass

        logging.info("Successfully synchronized.")

        return True
