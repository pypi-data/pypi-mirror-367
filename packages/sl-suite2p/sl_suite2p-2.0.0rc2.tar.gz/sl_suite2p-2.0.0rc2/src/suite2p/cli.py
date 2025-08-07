"""
This module provides general command-line interfaces (CLIs) that are installed into the host-environment together with
sl-suite2p library. The CLIs from this module provide a complete terminal-based interface to run all pipelines
supported by the sl-suite2p library.
"""

import ast
from typing import Any
from pathlib import Path

import click
import numpy as np
from sl_shared_assets import (
    SessionData,
    SessionTypes,
    TrackerFileNames,
    ProcessingTracker,
    AcquisitionSystems,
    get_processing_tracker,
    generate_project_manifest,
)
from ataraxis_base_utilities import LogLevel, console, ensure_directory_exists

from .multi_day import run_s2p_multiday, resolve_multiday_ops, discover_multiday_cells, extract_multiday_fluorescence
from .single_day import run_s2p, resolve_ops, process_plane, combine_planes, resolve_binaries
from .configuration import (
    MultiDayS2PConfiguration,
    SingleDayS2PConfiguration,
    generate_default_ops,
    generate_default_multiday_ops,
)


@click.command()
@click.option(
    "-o",
    "--output_directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="The absolute path to the directory where to generate the requested configuration file(s).",
)
@click.option(
    "-sd",
    "--single_day",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to generate the precursor configuration file for the single-day suite2p pipeline.",
)
@click.option(
    "-md",
    "--multi_day",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to generate the precursor configuration file for the multi-day suite2p pipeline.",
)
def generate_configuration_file(output_directory: Path, single_day: bool, multi_day: bool) -> None:
    """Generates the requested suite2p pipeline configuration .yaml files under the specified directory.

    Use this command to generate the human-editable configuration files for the single-day pipeline, the multi-day
    pipeline, or both. Modifying the parameters stored in this file allows configuring all aspects of each suite2p
    pipeline. Provide the path to the modified file to the 'run_ss2p' CLI command to execute the desired pipeline with
    the parameters specified inside the file.
    """
    output_directory = Path(output_directory)

    # If both options are disabled, ends runtime early with a warning message
    if not single_day and not multi_day:
        message = (
            f"Warning! Both configuration class output options are disabled, so no configuration file will be created. "
            f"Pass either the '--single_day' (-sd), '--multi_day' (-md), or both flags when calling this CLI command."
        )
        console.echo(message=message, level=LogLevel.WARNING)
        return

    precursor: SingleDayS2PConfiguration | MultiDayS2PConfiguration
    if single_day:
        precursor = generate_default_ops(as_dict=False)  # type: ignore
        precursor.to_config(output_directory=output_directory)

        message = (
            f"Default single-day pipeline configuration file: generated in the {output_directory} directory. Modify "
            f"the configuration parameters as necessary for your specific use case."
        )
        console.echo(message=message, level=LogLevel.SUCCESS)

    if multi_day:
        precursor = generate_default_multiday_ops(as_dict=False)  # type: ignore
        precursor.to_config(output_directory=output_directory)
        message = (
            f"Default multi-day pipeline configuration file: generated in the {output_directory} directory. Modify "
            f"the configuration parameters as necessary for your specific use case."
        )
        console.echo(message=message, level=LogLevel.SUCCESS)

    message = (
        f"See the original suite2p documentation (https://suite2p.readthedocs.io/en/latest/) and the Sun lab "
        f"repository (https://github.com/Sun-Lab-NBB/suite2p) for more information about suite2p and its "
        f"configuration parameters. Note! The sun-lab suite2p library overlaps, but does not have the same "
        f"configuration parameters as the original suite2p library."
    )
    console.echo(message=message, level=LogLevel.INFO)


@click.command()
@click.option(
    "-i",
    "--input_path",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help=(
        "The absolute path to the configuration .yaml file that stores the runtime parameters for the target pipeline."
    ),
)
@click.option(
    "-b",
    "--binarize",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to run single-day suite2p pipeline step 1 (resolve binary files).",
)
@click.option(
    "-p",
    "--process",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to run single-day suite2p pipeline step 2 (process planes).",
)
@click.option(
    "-c",
    "--combine",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to run single-day suite2p pipeline step 3 (combined processed plane data).",
)
@click.option(
    "-d",
    "--discover",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to run multi-day suite2p pipeline step 1 (discover cells trackable across days).",
)
@click.option(
    "-e",
    "--extract",
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Determines whether to run multi-day suite2p pipeline step 2 (extract fluorescence from cells tracked "
        "across days)."
    ),
)
@click.option(
    "-t",
    "--target",
    type=str,
    default="-1",
    help=(
        "The index of the plane to process, if running single-day pipeline, or the ID of the session to extract "
        "fluorescence from, if running multi-day pipeline. Setting this to '-1' (default value) will process all "
        "planes and sessions sequentially."
    ),
)
@click.option(
    "-o",
    "--overrides",
    type=str,
    default="{}",
    help=(
        "Additional processing parameters used to augment or override the parameters loaded from the configuration "
        "file. The input parameters have to be provided as a dictionary-formatted string, e.g.: "
        "{parallel_workers: 5, progress_bars: False}"
    ),
)
def run_pipeline(
    input_path: Path,
    binarize: bool,
    process: bool,
    combine: bool,
    discover: bool,
    extract: bool,
    target: str,
    overrides: str,
) -> None:
    """Runs the requested single-day or multi-day sl-suite2p pipeline step(s) based on the provided configuration
    parameters.

    This command functions as the central entry point for running all suite2p pipeline functions via the terminal. It
    can be flexibly configured using parameters stored in .yaml configuration files and provided as manual 'overrides'.
    Additionally, it can be used to flexibly execute one or more steps from each pipeline, which is especially
    beneficial in the context of distributing the workload in a remote compute server or cluster. Note; the type of
    pipeline is determined by the configuration file name, which should be either 'single_day_s2p_configuration.yaml' or
    'multi_day_s2p_configuration.yaml'.
    """
    input_path = Path(input_path)

    # Ensures the input configuration file is valid
    if input_path.suffix != ".yaml":
        message = (
            f"Unable to run the requested suite2p processing pipeline. Expected the configuration file to end with a "
            f"'.yaml' extension, but encountered the file with extension {input_path.suffix}."
        )
        console.error(message=message, error=FileNotFoundError)
    if input_path.stem != "single_day_s2p_configuration" and input_path.stem != "multi_day_s2p_configuration":
        message = (
            f"Unable to run the suite2p pipeline specified by the input configuration file. Expected the configuration "
            f"file to use the 'single_day_s2p_configuration' name or the 'multi_day_s2p_configuration' name, but "
            f"encountered the file with name {input_path.stem}."
        )
        console.error(message=message, error=FileNotFoundError)

    # Parses the additional or override parameters as a 'db' dictionary.
    db = _parse_db(overrides)

    # Single-day pipeline
    if input_path.stem == "single_day_s2p_configuration":
        # Loads configuration data from the provided file. Immediately converts it to dictionary format.
        ops = SingleDayS2PConfiguration.from_yaml(file_path=input_path).to_ops()  # type: ignore

        # Generates the ops.npy file for the runtime, using the 'ops' loaded above and additional overrides, 'db'
        # (if any)
        ops_path = resolve_ops(ops=ops, db=db)

        # Loads the resolved ops file to access the runtime configuration parameters below.
        final_ops = np.load(ops_path, allow_pickle=True).item()

        # If all three single-day steps are set to the same values, runs the entire single-day pipeline. Note, since
        # it does not make sense to call the single-day pipeline with all steps disabled, this function treats the case
        # where all are disabled the same as when all are enabled.
        if binarize == process == combine:
            run_s2p(ops_path=ops_path)
            return  # Explicit return to prevent repeating processing steps below

        # Otherwise, executes the requested single-day pipeline steps.
        if binarize:  # Step 1
            resolve_binaries(ops_path=ops_path)

        if process:  # Step 2
            # Either processes all available planes sequentially or only the requested plane
            if target != "-1":
                index = int(target)
                process_plane(ops_path=ops_path, plane_index=index)
            else:
                for plane in final_ops["nplanes"]:
                    process_plane(ops_path=ops_path, plane_index=plane)

        if combine:  # Step 3
            combine_planes(ops_path=ops_path)

    # Multi-day pipeline
    elif input_path.stem == "multi_day_s2p_configuration":
        # Loads configuration data from the provided file. Immediately converts it to dictionary format.
        ops = MultiDayS2PConfiguration.from_yaml(file_path=input_path).to_ops()  # type: ignore

        # Generates the ops.npy file for the runtime, using the 'ops' loaded above and additional overrides, 'db'
        # (if any)
        ops_path = resolve_multiday_ops(ops=ops, db=db)

        # Loads the resolved ops file to access the runtime configuration parameters below.
        final_ops = np.load(ops_path, allow_pickle=True).item()

        # Same idea as in the single-day pipeline: If both flags are set to the same value, this is interpreted as
        # a request to run the entire multi-day pipeline.
        if discover == extract:
            run_s2p_multiday(ops_path=ops_path)
            return

        if discover:  # Step 1
            discover_multiday_cells(ops_path=ops_path)

        if extract:  # Step 2
            # Same idea as with single-day planes, either processes all sessions sequentially or only the target session
            if target != "-1":
                session_id = target
                extract_multiday_fluorescence(ops_path=ops_path, session_id=session_id)
            else:
                for session in final_ops["session_ids"]:
                    extract_multiday_fluorescence(ops_path=ops_path, session_id=session)
    else:
        message = (
            f"Unable to run the requested suite2p processing pipeline, as none of the processing flags were enabled "
            f"when calling the 'ss2p-run' CLI command. Call this CLI with at least one of the flags specifying the "
            f"type of single-day or multi-day processing to perform."
        )
        console.echo(message=message, level=LogLevel.WARNING)


@click.command()
@click.option(
    "-i",
    "--input_path",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help=(
        "The absolute path to the configuration .yaml file that stores the runtime parameters for the single day "
        "suite2p pipeline. This file will be further specialized to process the target session."
    ),
)
@click.option(
    "-sp",
    "--session_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help=(
        "The absolute path to the session acquired by one of the supported Sun lab data acquisition systems, to "
        "process with the suite2p single-day pipeline."
    ),
)
@click.option(
    "-id",
    "--manager_id",
    type=int,
    required=True,
    default=0,
    show_default=True,
    help=(
        "The xxHash-64 hash value that represents the unique identifier for the process that manages this runtime. "
        "This is primarily used when calling this CLI on remote compute servers to ensure that only a single process "
        "can execute the processing pipeline for the target session at a time."
    ),
)
@click.option(
    "-pdr",
    "--processed_data_root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help=(
        "The absolute path to the directory where processed data from all projects is stored on the machine that runs "
        "this command. This argument is used when calling the CLI on the BioHPC server, which uses different data "
        "volumes for raw and processed data. Note, the input path must point to the root directory, as it will be "
        "automatically modified to include the project name, the animal id, and the session ID. Do not provide this "
        "argument if processed and raw data roots are the same."
    ),
)
@click.option(
    "-t",
    "--target",
    type=int,
    default=-1,
    help=(
        "The index of the plane to process. Setting this to -1 (default value) will process all planes sequentially."
    ),
)
@click.option(
    "-b",
    "--binarize",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to run single-day suite2p pipeline step 1 (convert raw data to suite2p binary files).",
)
@click.option(
    "-p",
    "--process",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to run single-day suite2p pipeline step 2 (process planes).",
)
@click.option(
    "-c",
    "--combine",
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Determines whether to run single-day suite2p pipeline step 3 (combine processed plane data into a unified "
        "dataset)."
    ),
)
@click.option(
    "-w",
    "--workers",
    type=int,
    default=20,
    help=(
        "The number of parallel workers to use when executing multiprocessing tasks. Most runtimes should set this to "
        "a value between 10 and 20. Setting this to a value of -1 or 0 makes the system use all available cores to "
        "parallelize multiprocessing tasks."
    ),
)
@click.option(
    "-cpd",
    "--create_processed_directories",
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Determines whether to create the processed data hierarchy. Typically, this flag only needs to be enabled when "
        "this command is called outside the typical data processing pipeline used in the Sun lab. Usually, processed "
        "data directories are created at an earlier stage of data processing, if it is carried out on the remote "
        "compute server."
    ),
)
@click.option(
    "-pb",
    "--progress_bars",
    type=bool,
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Determines whether to use progress bars during long-running tasks to visualize progress. This option should "
        "be disabled when running the pipeline in the headless (server-side) mode."
    ),
)
@click.option(
    "-um",
    "--update_manifest",
    is_flag=True,
    help=(
        "Determines whether to (re)generate the manifest file for the processed session's project. This flag "
        "should always be enabled when this CLI is executed on the remote compute server(s) to ensure that the "
        "manifest file always reflects the most actual state of each project."
    ),
)
def run_single_day_pipeline(
    input_path: Path,
    session_path: Path,
    manager_id: int,
    processed_data_root: Path | None,
    binarize: bool,
    process: bool,
    combine: bool,
    target: int,
    workers: int,
    create_processed_directories: bool,
    progress_bars: bool,
    update_manifest: bool,
) -> None:
    # Instantiates the SessionData instance for the processed session
    session_data = SessionData.load(
        session_path=session_path,
        processed_data_root=processed_data_root,
        make_processed_data_directory=create_processed_directories,
    )

    # Ensures the input configuration file is valid
    if input_path.suffix != ".yaml":
        message = (
            f"Unable to specialize the single-day sl-suite2p configuration file to process the session "
            f"'{session_data.session_name}' performed by animal '{session_data.animal_id}' for the "
            f"'{session_data.project_name}' project. Expected the configuration file to use the '.yaml' extension, "
            f"but encountered the file {input_path.name}."
        )
        console.error(message=message, error=FileNotFoundError)

    # Loads the configuration file into memory
    config: SingleDayS2PConfiguration = SingleDayS2PConfiguration.from_yaml(file_path=input_path)  # type: ignore

    # Specialization for Mesoscope-VR acquisition system
    if session_data.acquisition_system == AcquisitionSystems.MESOSCOPE_VR:
        config.main.progress_bars = progress_bars
        config.main.parallel_workers = workers
        config.file_io.save_path0 = str(session_data.processed_data.mesoscope_data_path)
        config.file_io.data_path = [str(session_data.raw_data.mesoscope_data_path)]

    else:
        # Raises an error if the session uses an unsupported acquisition system.
        supported_systems = tuple(AcquisitionSystems)
        message = (
            f"Unable to specialize the single-day sl-suite2p configuration file for the session "
            f"'{session_data.session_name}' performed by animal '{session_data.animal_id}' for the "
            f"'{session_data.project_name}' project. The session was acquired using an unsupported acquisition system "
            f"'{session_data.acquisition_system}'. Currently, only the following acquisition systems are "
            f"supported: {', '.join(supported_systems)}."
        )
        console.error(message=message, error=ValueError)

    supported_sessions = (SessionTypes.MESOSCOPE_EXPERIMENT,)
    if session_data.session_type not in supported_sessions:
        message = (
            f"Unable to run the single-day suite2p pipeline for the session '{session_data.session_name}' performed by "
            f"animal '{session_data.animal_id}' for the '{session_data.project_name}' project. The session is of an "
            f"unsupported type '{session_data.session_type}'. Currently, only the following session types are "
            f"supported: {', '.join(supported_sessions)}."
        )
        console.error(message=message, error=ValueError)

    # Converts the specialized configuration file into an 'ops' dictionary for the runtime.
    ops = config.to_ops()

    # Generates the ops.npy file for the runtime, using the 'ops' loaded above. Does not use the 'db' dictionary due to
    # explicit main config overriding behavior above
    ops_path = resolve_ops(ops=ops, db={})

    # Loads the resolved ops file to access the runtime configuration parameters below.
    final_ops = np.load(ops_path, allow_pickle=True).item()

    # Instantiates the ProcessingTracker instance for single-day suite2p processing and configures the underlying
    # tracker file to indicate that the processing is ongoing.
    tracker = get_processing_tracker(
        root=session_data.processed_data.processed_data_path, file_name=TrackerFileNames.SUITE2P
    )
    tracker.start(manager_id=manager_id)

    try:
        # If all three single-day steps are set to the same values, runs the entire single-day pipeline. Note, since
        # it does not make sense to call the single-day pipeline with all steps disabled, this function treats the case
        # where all are disabled the same as when all are enabled.
        if binarize == process == combine:
            run_s2p(ops_path=ops_path)
            tracker.stop(manager_id=manager_id)  # Configures the tracker to indicate that the processing is finished.
            return  # Explicit return to prevent repeating processing steps below

        # Otherwise, executes the requested single-day pipeline steps.
        if binarize:  # Step 1
            resolve_binaries(ops_path=ops_path)

        if process:  # Step 2
            # Either processes all available planes sequentially or only the requested plane
            if target != -1:
                process_plane(ops_path=ops_path, plane_index=target)
            else:
                for plane in final_ops["nplanes"]:
                    process_plane(ops_path=ops_path, plane_index=plane)

        if combine:  # Step 3
            combine_planes(ops_path=ops_path)

            # Configures the tracker to indicate that the processing is finished. Note, the pipeline is considered
            # finished only after it completes the third data processing step. Until then, no other manager would be
            # able to run the pipeline for the target session.
            tracker.stop(manager_id=manager_id)

    except Exception:
        # If the runtime encounters an error, configures the tracker to indicate that the processing runtime was
        # interrupted due to an error. This opens the session up for being processed by another manager process.
        if tracker.is_running:
            tracker.error(manager_id=manager_id)

    finally:
        # If the runtime is configured to generate the project manifest file, attempts to generate and overwrite the
        # existing manifest file for the target project.
        if update_manifest:
            # All sessions are stored under root/project/animal/session. SessionData exposes paths to either raw_data or
            # processed_data subdirectories under the root session directory on each volume. Indexing parents of
            # SessionData paths returns the project-specific directory at index 2 and the root for that directory at
            # index 3.
            raw_directory = session_data.raw_data.raw_data_path.parents[2]
            processed_directory = session_data.processed_data.processed_data_path.parents[3]

            # Generates the manifest file inside the root raw data project directory
            generate_project_manifest(
                raw_project_directory=raw_directory,
                processed_data_root=processed_directory,
                output_directory=raw_directory,
            )


@click.command()
@click.option(
    "-i",
    "--input_path",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help=(
        "The absolute path to the configuration .yaml file that stores the runtime parameters for the multi-day "
        "suite2p pipeline. This file will be further specialized to specifically process the target sessions."
    ),
)
@click.option(
    "-o",
    "--output_path",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help=(
        "The absolute path to the directory where to set up the output multi-day suite2p data hierarchy and save the "
        "pipeline output data."
    ),
)
@click.option(
    "-sp",
    "--session_paths",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    multiple=True,
    required=True,
    help=(
        "Two or more absolute paths to the Sun lab acquired sessions from the same animal that contain "
        "single-day suite2p processed cells to be tracked across days. Can be specified multiple times."
    ),
)
@click.option(
    "-pdr",
    "--processed_data_root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help=(
        "The absolute path to the directory where processed data from all projects is stored on the machine that runs "
        "this command. This argument is used when calling the CLI on the BioHPC server, which uses different data "
        "volumes for raw and processed data. Note, the input path must point to the root directory, as it will be "
        "automatically modified to include the project name, the animal id, and the session ID. Do not provide this "
        "argument if processed and raw data roots are the same."
    ),
)
@click.option(
    "-d",
    "--discover",
    is_flag=True,
    show_default=True,
    default=False,
    help="Determines whether to run multi-day suite2p pipeline step 1 (discover cells trackable across days).",
)
@click.option(
    "-e",
    "--extract",
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Determines whether to run multi-day suite2p pipeline step 2 (extract fluorescence from cells tracked "
        "across days)."
    ),
)
@click.option(
    "-t",
    "--target",
    type=str,
    default="-1",
    help=(
        "The ID of the session to extract the across-day-tracked fluorescence from. Setting this to '-1' "
        "(default value) will process all sessions sequentially."
    ),
)
@click.option(
    "-w",
    "--workers",
    type=int,
    default=20,
    help=(
        "The number of parallel workers to use when executing multiprocessing tasks. Most runtimes should set this to "
        "a value between 10 and 20. Setting this to a value of -1 or 0 makes the system use all available cores to "
        "parallelize multiprocessing tasks."
    ),
)
@click.option(
    "-cpd",
    "--create_processed_directories",
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Determines whether to create the processed data hierarchy. Typically, this flag only needs to be enabled when "
        "this command is called outside of the typical data processing pipeline used in the Sun lab. Usually, "
        "processed data directories are created at an earlier stage of data processing, if it is carried out on the "
        "remote compute server."
    ),
)
@click.option(
    "-pb",
    "--progress_bars",
    type=bool,
    is_flag=True,
    show_default=True,
    default=False,
    help=(
        "Determines whether to use progress bars during long-running tasks to visualize progress. This option should "
        "be disabled when running the pipeline in the headless (server-side) mode."
    ),
)
def run_multi_day_pipeline(
    input_path: Path,
    output_path: Path,
    session_paths: list[Path],
    processed_data_root: Path | None,
    discover: bool,
    extract: bool,
    target: str,
    workers: int,
    create_processed_directories: bool,
    progress_bars: bool,
) -> None:
    # Ensures the input configuration file is valid
    if input_path.suffix != ".yaml":
        message = (
            f"Unable to specialize the multi-day sl-suite2p configuration file for the target set of Sun lab sessions. "
            f"Expected the configuration file to use the '.yaml' extension, but encountered the file {input_path.name}."
        )
        console.error(message=message, error=FileNotFoundError)

    # Loops over sessions and builds the list of input session folder paths
    session_inputs = []
    animal_id = ""
    for session in session_paths:
        # Instantiates the SessionData instance for the processed session
        session_data = SessionData.load(
            session_path=session,
            processed_data_root=processed_data_root,
            make_processed_data_directory=create_processed_directories,
        )

        if animal_id == "":
            animal_id = session_data.animal_id
        elif animal_id != session_data.animal_id:
            # Raises an error if sessions from multiple animals are passed as part of the same multi-day dataset
            message = (
                f"Unable to specialize the multi-day sl-suite2p configuration file for the target set of Sun lab "
                f"sessions, as the input set of sessions comes from at least two different animals: {animal_id} and "
                f"{session_data.animal_id}. Multi-day tracking requires all sessions to be acquired from the same "
                f"animal."
            )
            console.error(message=message, error=ValueError)

        supported_systems = ("mesoscope-vr",)
        if session_data.acquisition_system not in supported_systems:
            # Raises an error if the session uses an unsupported acquisition system.
            message = (
                f"Unable to specialize the multi-day sl-suite2p configuration file for the target set of Sun lab "
                f"sessions, as the {session.name} session was acquired using an unsupported acquisition system "
                f"{session_data.acquisition_system}. Currently, only the following acquisition systems are "
                f"supported: {', '.join(supported_systems)}."
            )
            console.error(message=message, error=ValueError)

        # If the session uses a supported acquisition system, resolves and adds the path to that session's
        # suite2p-processed data folder as the input to the multi-day pipeline
        session_inputs.append(str(session_data.processed_data.mesoscope_data_path))

    # Loads the configuration file into memory
    config: MultiDayS2PConfiguration = MultiDayS2PConfiguration.from_yaml(file_path=input_path)  # type: ignore

    # Specializes the config to work with the target data
    config.main.progress_bars = progress_bars
    config.main.parallel_workers = workers
    config.io.multiday_save_path = str(output_path)
    config.io.multiday_save_folder = animal_id  # Uses animal ID as the output folder name
    config.io.session_folders = session_inputs

    # Creates a new tracker file for this runtime. A separate tracker that those provided by the SessionData instance is
    # needed due to access permission nuances of the Sun lab processing servers.
    tracker_path = output_path.joinpath(animal_id, "multi_day_suite2p_tracker.yaml")
    ensure_directory_exists(tracker_path)

    # Starts the runtime.
    tracker = ProcessingTracker(file_path=tracker_path)
    tracker.start()
    try:
        # Converts the specialized configuration file into an 'ops' dictionary for the runtime.
        ops = config.to_ops()

        # Generates the ops.npy file for the runtime, using the 'ops' loaded above.
        ops_path = resolve_multiday_ops(ops=ops, db={})

        # Loads the resolved ops file to access the runtime configuration parameters below.
        final_ops = np.load(ops_path, allow_pickle=True).item()

        # Same idea as in the single-day pipeline: If both flags are set to the same value, this is interpreted as
        # a request to run the entire multi-day pipeline.
        if discover == extract:
            run_s2p_multiday(ops_path=ops_path)
            return

        if discover:  # Step 1
            discover_multiday_cells(ops_path=ops_path)

        if extract:  # Step 2
            # Same idea as with single-day planes, either processes all sessions sequentially or only the target session
            if target != "-1":
                session_id = target
                extract_multiday_fluorescence(ops_path=ops_path, session_id=session_id)
            else:
                for session in final_ops["session_ids"]:
                    extract_multiday_fluorescence(ops_path=ops_path, session_id=session)
    finally:
        # If the code reaches this section while the tracker indicates that the processing is still running,
        # this means that the processing runtime encountered an error. Configures the tracker to indicate that this
        # runtime finished with an error to prevent deadlocking future runtime calls.
        if tracker.is_running:
            tracker.error()


def _parse_db(data_string: str) -> dict[str, Any]:
    """This service function parses the value passed to the --overrides (-o) argument of the run_pipeline function as a
    Python dictionary.

    Args:
        data_string: A string that contains the data to be parsed.

    Returns:
        The parsed data as a dictionary compatible with the 'db' and 'ops' input arguments to the resolve_ops()
        or resolve_multiday_ops functions.

    Raises:
        ValueError: If the input data_string cannot be parsed as a Python dictionary.
    """

    # If the user provided no overrides, returns an empty 'db' dictionary.
    if data_string == "{}":
        return {}

    try:
        # Parses the string as a Python literal
        parsed = ast.literal_eval(data_string)

        # Ensures the parsed result is a dictionary. If not, propagates the error to be evaluated by the
        # 'try' block
        if not isinstance(parsed, dict):
            raise ValueError()

        # Otherwise, returns the parsed dictionary
        return parsed
    except (SyntaxError, ValueError):
        message = (
            f"Unable to parse the input 'overrides' argument as a python dictionary. Make sure the value of the "
            f"--overrides (-o) argument is formatted like a python dictionary, "
            f"e.g.: '{{'key1': value1, 'key2': 'value2'}}'"
        )
        console.error(message=message, error=ValueError)

        # Fallback to appease mypy, should not be reachable.
        raise ValueError(message)
