"""Filesystem operations for CXR file collection."""

from pathlib import Path
from typing import List
import logging

from .core import CXRFile


def collect_cxr_files(input_path: str) -> List[CXRFile]:
    """
    Collect CXR files from input path (file or directory).
    
    Args:
        input_path: Path to a CXR file or directory containing CXR files
        
    Returns:
        List of CXRFile objects found
    """
    path = Path(input_path)
    
    if not path.exists():
        logging.error(f"Path does not exist: {input_path}")
        return []
    
    if path.is_file():
        return _process_single_file(path)
    
    return _process_directory(path)


def _process_single_file(path: Path) -> List[CXRFile]:
    """Process a single CXR file."""
    if path.suffix.lower() != '.cxr':
        logging.warning(f"Input file is not a .cxr file: {path.name}")
        return []
    
    try:
        return [CXRFile.from_path(str(path))]
    except ValueError as e:
        logging.error(f"Error parsing {path.name}: {e}")
        return []


def _process_directory(path: Path) -> List[CXRFile]:
    """Process all CXR files in a directory recursively."""
    logging.info(f"Scanning directory: {path}")
    cxr_files = []
    
    for cxr_path in path.rglob('*.cxr'):
        try:
            cxr_files.append(CXRFile.from_path(str(cxr_path)))
        except ValueError as e:
            logging.error(f"Error parsing {cxr_path.name}: {e}")
    
    logging.info(f"Found {len(cxr_files)} CXR file(s)")
    return cxr_files
