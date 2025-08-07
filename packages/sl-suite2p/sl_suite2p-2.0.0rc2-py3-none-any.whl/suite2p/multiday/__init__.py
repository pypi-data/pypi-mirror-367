"""This package provides the algorithms and tools for carrying out the multi-day suite2p processing pipeline. This
pipeline tracks the cells across multiple single-day-registered sessions and extracts their fluorescence data across
sessions. It is an extension of the single-day suite2p pipeline and uses some tools and assets from the single-day code.
This pipeline was adapted from the original implementation to improve its runtime efficiency and integrate it with the
single-day suite2p pipeline and source code.
Original implementation can be found here: https://github.com/sprustonlab/multiday-suite2p-public/tree/main
"""

from .io import import_sessions, export_masks_and_images
from .gui import show_images_with_masks
from .utils import extract_unique_components
from .process import extract_session_traces
from .transform import (
    register_sessions,
    generate_template_masks,
    backward_transform_masks,
)
from .dataclasses import Session, MultiDayData

__all__ = [
    "show_images_with_masks",
    "import_sessions",
    "export_masks_and_images",
    "extract_unique_components",
    "extract_session_traces",
    "register_sessions",
    "generate_template_masks",
    "backward_transform_masks",
    "MultiDayData",
    "Session",
]
