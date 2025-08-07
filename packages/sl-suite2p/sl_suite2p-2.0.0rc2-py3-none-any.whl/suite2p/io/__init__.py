"""This package provides tools to import, convert, and save multi-plane imaging data. Specifically, it includes
functions used to prepare compatible TIFF, and Thorlabs RAW data for the Suite2p single-day processing pipeline by
converting it to the BinaryFile format used by the library. It also exposes functions for saving the processed data in
both NumPy and MATLAB-compatible formats."""

from .raw import raw_to_binary
from .save import combined, save_matlab, compute_dydx
from .tiff import save_tiff, tiff_to_binary, mesoscan_to_binary, generate_tiff_filename
from .binary import BinaryFile, BinaryFileCombined

__all__ = [
    "raw_to_binary",
    "combined",
    "save_matlab",
    "compute_dydx",
    "save_tiff",
    "tiff_to_binary",
    "mesoscan_to_binary",
    "generate_tiff_filename",
    "BinaryFile",
    "BinaryFileCombined",
]
