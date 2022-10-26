from typing import Any, NoReturn

import os
import sys
from collections.abc import Callable
from pathlib import Path

from loguru import logger
from PyQt5.QtWidgets import QApplication
from workflow_manager import get_version
from workflow_manager.action_script import ActionScript
from workflow_manager.config import Config
from workflow_manager.workflow_manager import WorkflowManager

from folder_structure_sync.pyqt5_ui import Ui_MainWindow

logger.add("log.log", level="TRACE", rotation="50 MB")

CONFIG = Config(
    app_name=f"Folder Structure Sync v{get_version()}",
    statusbar_text="App designed by v3services",
    about_text="App designed by v3services.",
    pos_x=0,
    pos_y=0,
    height=1200,
    width=800,
)


class FolderStructureSyncActionScript(ActionScript):
    def script(self, **kwargs: Any) -> str:
        logger.info(f"Starting: {self.__class__.__name__}.script()")

        source_folder: Path = Path(kwargs["source_folder"])
        destination_folder: Path = Path(kwargs["destination_folder"])
        folders_to_ignore: list[str] = kwargs["folders_to_ignore"]
        scan_recursively: bool = bool(kwargs["scan_recursively"])

        for root, directories, _ in os.walk(source_folder):
            # for name in files:
            #     print(os.path.join(root, name))

            # Handle Scan Recursively
            if not scan_recursively and Path(root) != Path(source_folder):
                continue

            # Handle Folders To Ignore
            str_root = str(Path(root))
            str_source_folder = str(source_folder)
            parents = str_root.replace(str_source_folder, "").split("/")
            if any(parent in folders_to_ignore for parent in parents):
                continue

            for directory in directories:

                # Handle Folders To Ignore
                if directory in folders_to_ignore:
                    continue

                # Copy Folder Structure
                target_source_folder = str(Path(os.path.join(root, directory)))
                target_destination_folder = Path(
                    target_source_folder.replace(str(source_folder), str(destination_folder))
                )
                try:
                    target_destination_folder.mkdir(exist_ok=True)
                    print(f"{target_source_folder} -> {target_destination_folder}")
                except Exception as e:
                    print(e)
                    raise e

        return "Script completed successfully!"


class FolderStructureSyncWorkflowManager(WorkflowManager):
    def __init__(self) -> None:
        self.ui = Ui_MainWindow()
        self.config: Config = CONFIG
        super().__init__()

    # Line 1 Callbacks
    def source_browse_button_clicked(self):
        """Source Browse Button"""
        self.ui.source_line_edit.setText(self._get_directory())

    def destination_browse_button(self):
        """Destination Browse Button"""
        self.ui.destination_line_edit.setText(self._get_directory())

    def folder_to_ignore_add_button(self):
        """FolderToIgnore Add Button"""
        self.ui.folder_to_ignore_list_widget.addItem(self.ui.folder_to_ignore_line_edit.text())
        self.ui.folder_to_ignore_line_edit.setText("")

    def action_run_script_button_clicked(self):
        """Run Script Button"""
        # Define Script & Input
        source_folder = self.ui.source_line_edit.text()
        destination_folder = self.ui.destination_line_edit.text()
        folders_to_ignore = [
            self.ui.folder_to_ignore_list_widget.item(index).text()
            for index in range(self.ui.folder_to_ignore_list_widget.count())
        ]
        scan_recursively = self.ui.scan_recursively_checkbox.checkState()

        script_cls: Callable[..., Any] = FolderStructureSyncActionScript

        # Validate & Run Script
        if self.inputs_are_valid(
            source_folder=source_folder, destination_folder=destination_folder
        ):
            self.run_action_script(
                script_cls=script_cls,
                source_folder=source_folder,
                destination_folder=destination_folder,
                folders_to_ignore=folders_to_ignore,
                scan_recursively=scan_recursively,
            )

    # Connections
    def connect_buttons(self):
        """Connects UI buttons the the callback function."""
        super().connect_buttons()

        # Setup Action 1
        self.ui.source_browse_button.clicked.connect(self.source_browse_button_clicked)
        self.ui.destination_browse_button.clicked.connect(self.destination_browse_button)
        self.ui.run_script_button.clicked.connect(self.action_run_script_button_clicked)
        self.ui.folder_to_ignore_line_edit.returnPressed.connect(self.folder_to_ignore_add_button)
        self.ui.folder_to_ignore_add_button.clicked.connect(self.folder_to_ignore_add_button)

    # Input Validations
    def validate_inputs(self, **kwargs: Any) -> str | None:
        """
        Validation on required inputs. ie. Ensure file exists, ensure value is int, etc.

        Return None if passes all validations.
        Return str with error if does NOT pass validation.
        """
        source_folder = kwargs["source_folder"]
        destination_folder = kwargs["destination_folder"]

        # Checks fields are not empty
        if not source_folder or not destination_folder:
            return "Field can not be empty"

        source_folder = Path(kwargs["source_folder"])
        destination_folder = Path(kwargs["destination_folder"])

        # Check that folders are not files
        if source_folder.is_file() or destination_folder.is_file():
            return "Can not choose a file. Must be a folder."

        # Check that folders already exist
        if not source_folder.exists() or not destination_folder.exists():
            return "Please choose folders that already exist."

        return None


def main() -> NoReturn:
    app = QApplication(sys.argv)
    _ = FolderStructureSyncWorkflowManager()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
