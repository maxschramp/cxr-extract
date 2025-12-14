"""Filesystem operations for CXR files."""

from pathlib import Path
from typing import List
import logging
from cxr import CXRFile


def collect_cxr_files(input_path: str) -> List[CXRFile]:
    """Collect CXR files from input path (file or directory)."""
    path = Path(input_path)
    
    if not path.exists():
        logging.error(f"Path does not exist: {input_path}")
        return []
    
    if path.is_file():
        if path.suffix.lower() != '.cxr':
            logging.warning(f"Input file is not a .cxr file: {path.name}")
            return []
        try:
            return [CXRFile.from_path(str(path))]
        except ValueError as e:
            logging.error(f"Error parsing {path.name}: {e}")
            return []
    
    # Directory - search recursively
    logging.info(f"Scanning directory: {path}")
    cxr_files = []
    for cxr_path in path.rglob('*.cxr'):
        try:
            cxr_files.append(CXRFile.from_path(str(cxr_path)))
        except ValueError as e:
            logging.error(f"Error parsing {cxr_path.name}: {e}")
    
    logging.info(f"Found {len(cxr_files)} CXR file(s)")
    return cxr_files
