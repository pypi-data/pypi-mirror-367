"""A Python library that stores assets shared between multiple Sun (NeuroAI) lab data pipelines.

See https://github.com/Sun-Lab-NBB/sl-shared-assets for more details.
API documentation: https://sl-shared-assets-api-docs.netlify.app/
Authors: Ivan Kondratyev (Inkaros), Kushaan Gupta, Natalie Yeung
"""

from ataraxis_base_utilities import console

from .tools import (
    ProjectManifest,
    resolve_p53_marker,
    transfer_directory,
    generate_project_manifest,
    calculate_directory_checksum,
)
from .server import Job, Server, JupyterJob, ServerCredentials
from .data_classes import (
    RawData,
    DrugData,
    ImplantData,
    SessionData,
    SubjectData,
    SurgeryData,
    SessionTypes,
    InjectionData,
    ProcedureData,
    ProcessedData,
    MesoscopePaths,
    ZaberPositions,
    ExperimentState,
    ExperimentTrial,
    MesoscopeCameras,
    TrackerFileNames,
    ProcessingTracker,
    AcquisitionSystems,
    MesoscopePositions,
    RunTrainingDescriptor,
    LickTrainingDescriptor,
    MesoscopeHardwareState,
    WindowCheckingDescriptor,
    MesoscopeMicroControllers,
    MesoscopeAdditionalFirmware,
    MesoscopeSystemConfiguration,
    MesoscopeExperimentDescriptor,
    MesoscopeExperimentConfiguration,
    generate_manager_id,
    get_processing_tracker,
    get_system_configuration_data,
    set_system_configuration_file,
)

# Ensures console is enabled when this library is imported
if not console.enabled:
    console.enable()

__all__ = [
    # Server package
    "Server",
    "ServerCredentials",
    "Job",
    "JupyterJob",
    # Data classes package
    "DrugData",
    "ImplantData",
    "SessionData",
    "RawData",
    "ProcessedData",
    "SubjectData",
    "SurgeryData",
    "InjectionData",
    "ProcessingTracker",
    "ProcedureData",
    "ZaberPositions",
    "ExperimentState",
    "MesoscopePositions",
    "MesoscopeHardwareState",
    "RunTrainingDescriptor",
    "LickTrainingDescriptor",
    "MesoscopeExperimentConfiguration",
    "MesoscopeExperimentDescriptor",
    "MesoscopeSystemConfiguration",
    "MesoscopePaths",
    "MesoscopeCameras",
    "MesoscopeMicroControllers",
    "MesoscopeAdditionalFirmware",
    "get_system_configuration_data",
    "set_system_configuration_file",
    "ExperimentTrial",
    "SessionTypes",
    "AcquisitionSystems",
    "WindowCheckingDescriptor",
    "get_processing_tracker",
    "generate_manager_id",
    "TrackerFileNames",
    # Tools package
    "ProjectManifest",
    "resolve_p53_marker",
    "transfer_directory",
    "calculate_directory_checksum",
    "generate_project_manifest",
]
