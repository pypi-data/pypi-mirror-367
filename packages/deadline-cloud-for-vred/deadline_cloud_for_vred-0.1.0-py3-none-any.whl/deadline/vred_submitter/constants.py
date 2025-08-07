# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""Provides a Constants class that focuses on the backend submitter component"""

from pathlib import Path
from typing import Final


class ConstantsMeta(type):
    """Metaclass to prevent modification of class attributes."""

    def __setattr__(cls, name, value):
        """Prevent modification of class attributes."""
        raise AttributeError(f"Cannot modify constant '{name}'")

    def __delattr__(cls, name):
        """Prevent deletion of class attributes."""
        raise AttributeError(f"Cannot delete constant '{name}'")


class Constants(metaclass=ConstantsMeta):
    """Constants class for backend submitter component"""

    ANIMATION_SETTINGS_DIALOG_NAME: Final[str] = "Animation Settings"
    ASSET_REFERENCES_FILENAME: Final[str] = "asset_references.yaml"
    BASE_TEN: Final[int] = 10
    CONDA_CHANNELS_FIELD: Final[str] = "CondaChannels"
    CONDA_CHANNELS_OVERRIDE_ENV_VAR: Final[str] = "CONDA_CHANNELS"
    CONDA_PACKAGES_FIELD: Final[str] = "CondaPackages"
    CONDA_PACKAGES_OVERRIDE_ENV_VAR: Final[str] = "CONDA_PACKAGES"
    CUSTOM_SPEED_FIELD_NAME: Final[str] = "_customSpeed"
    DEADLINE_CLOUD_FOR_VRED_PACKAGE_PREFIX: Final[str] = "deadline_cloud_for_vred"
    DEADLINE_CLOUD_FOR_VRED_SUBMITTER_VERSION_FIELD: Final[str] = (
        "deadline-cloud-for-vred-submitter-version"
    )
    DEADLINE_CLOUD_MENU_NAME: Final[str] = "Deadline Cloud"
    DEADLINE_HOME: Final[str] = str(Path.home() / ".deadline")
    DEFAULT_FIELD: Final[str] = "default"
    DEFAULT_JOB_TEMPLATE_FILENAME: Final[str] = "default_vred_job_template.yaml"
    DEFAULT_SCENE_FILE_FPS_COUNT: Final[float] = 24.0
    DESCRIPTION_FIELD: Final[str] = "description"
    ENVIRONMENT_FIELD: Final[str] = "environment"
    ERROR_ANIMATION_SETTINGS_DIALOG_NOT_FOUND: Final[str] = "Animation settings dialog not found"
    ERROR_FILE_NOT_FOUND_ISSUE: Final[str] = "File not found"
    ERROR_FILE_PERMISSIONS_ISSUE: Final[str] = "Permission denied accessing file"
    ERROR_FILE_WRITE_ISSUE: Final[str] = "Permission denied writing file"
    ERROR_FRAME_RANGE_FORMAT_INVALID: Final[str] = (
        "Invalid frame range format. Please revise and retry."
    )
    ERROR_OUTPUT_FILENAME_INVALID: Final[str] = (
        "Output filename contains invalid characters. Please revise and retry."
    )
    ERROR_OUTPUT_PATH_INVALID: Final[str] = (
        "Output path does not exist or is invalid. Please revise and retry."
    )
    ERROR_PREFERENCES_BUTTON_NOT_FOUND: Final[str] = "Preferences button not found"
    ERROR_QUEUE_PARAM_CONFLICT: Final[str] = (
        "The following queue parameters conflict with the VRED job parameters:\n"
    )
    ERROR_SCENE_FILE_UNDEFINED_BODY: Final[str] = (
        "The active scene has not yet been saved to a file. Please save the scene file prior to submitting a render "
        "job or exporting to a job bundle."
    )
    ERROR_SPEED_SETTINGS_WIDGET_NOT_FOUND: Final[str] = "Speed widget not found"
    ERROR_TIMELINE_ACTION_NOT_FOUND: Final[str] = "Timeline action not found"
    ERROR_TIMELINE_TOOLBAR_NOT_FOUND: Final[str] = "Timeline toolbar not found"
    ERROR_YAML_GENERAL_ERROR: Final[str] = "Unexpected error reading YAML file"
    ERROR_YAML_INVALID_FORMAT: Final[str] = "Invalid YAML format in"
    ERROR_YAML_OBJECT_NOT_FOUND: Final[str] = "YAML file must contain a dictionary/object, got"
    ERROR_YAML_NOT_FOUND: Final[str] = "YAML file not found"
    FILENAME_UNICODE_REGEX: Final[str] = r"^[\w\-\.]+$"
    FRAME_RANGE_FORMAT_REGEX: Final[str] = r"^(-?\d+)-(-?\d+)(?:x(\d+))?$"
    FRAME_START_STOP_DELIMITER: Final[str] = "-"
    HOST_REQUIREMENTS_FIELD: Final[str] = "hostRequirements"
    JOB_BUNDLE_SCRIPTS_FOLDER_PATH: Final[str] = str(Path(DEADLINE_HOME) / "scripts")
    JOB_ENVIRONMENTS_FIELD: Final[str] = "jobEnvironments"
    NAME_FIELD: Final[str] = "name"
    NAN: Final[str] = "NaN"
    NEGATIVE_INFINITY: Final[str] = "-inf"
    PARAMETER_DEFINITIONS_FIELD: Final[str] = "parameterDefinitions"
    PARAMETER_VALUES_FIELD: Final[str] = "parameterValues"
    PARAMETER_VALUES_FILENAME: Final[str] = "parameter_values.yaml"
    POSITIVE_INFINITY: Final[str] = "inf"
    READ_FLAG: Final[str] = "r"
    SCENE_FILE_NOT_SAVED_TITLE: Final[str] = "Warning: scene file not saved"
    SCENE_FILE_NOT_SAVED_BODY: Final[str] = (
        "The scene file has unsaved local changes that will not be included in the job "
        "submission.\n\nDo you want to save the scene file before submitting?"
    )
    SUBMIT_TO_DEADLINE_CLOUD_ACTION_NAME: Final[str] = "Submit To Deadline Cloud"
    STEPS_FIELD: Final[str] = "steps"
    TEMPLATE_FILENAME: Final[str] = "template.yaml"
    TILE_ASSEMBLY_STEP_NAME: Final[str] = "Tile Assembly"
    TIMELINE_ACTION_NAME: Final[str] = "Timeline"
    TIMELINE_ANIMATION_PREFS_BUTTON_NAME: Final[str] = "_prefs"
    TIMELINE_TOOLBAR_NAME: Final[str] = "Timeline_Toolbar"
    UTF8_FLAG: Final[str] = "utf-8"
    VALUE_FIELD: Final[str] = "value"
    VRED_CORE_CONDA_PACKAGE_PREFIX: Final[str] = "vredcore"
    VRED_PRO_CONDA_PACKAGE_PREFIX: Final[str] = "vred"
    VRED_RENDER_SCRIPT_FILENAME: Final[str] = "VRED_RenderScript_DeadlineCloud.py"
    VRED_VERSION_FIELD: Final[str] = "vred-version"
    WRITE_FLAG: Final[str] = "w"

    def __new__(cls):
        """Prevent instantiation of this class."""
        raise TypeError("Constants class cannot be instantiated")
