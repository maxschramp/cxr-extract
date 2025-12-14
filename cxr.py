#!/usr/bin/env python3
"""CXR file representation module."""

import os
import re
from pathlib import Path
from typing import List, Optional

try:
    import OpenEXR
except ImportError:
    OpenEXR = None


class CXRFile:
    """Represents a CXR file with its metadata."""
    
    def __init__(self, filename: str, directory_path: str, frame_number: int, sequence_name: str, elements: Optional[List[str]] = None):
        self.filename = filename
        self.directory_path = directory_path
        self.frame_number = frame_number
        self.sequence_name = sequence_name
        self.elements = elements if elements is not None else self._read_elements()
    
    @property
    def full_path(self) -> str:
        return os.path.join(self.directory_path, self.filename)
    
    def _read_elements(self) -> List[str]:
        """Read and parse corona elements from EXR header."""
        if not OpenEXR:
            return []
        
        try:
            header = OpenEXR.InputFile(self.full_path).header()
            if 'corona.elements' not in header:
                return []
            
            elements = header['corona.elements']
            elements_str = elements.decode('utf-8') if isinstance(elements, bytes) else elements
            return self._parse_corona_elements(elements_str)
        except Exception:
            return []
    
    @staticmethod
    def _parse_corona_elements(elements_string: str) -> List[str]:
        """Parse corona.elements string and filter out specific types."""
        excluded_types = ['SamplingFocus', 'VisibleDiffuse', 'VisibleNormals', 'Hybrid']
        elements = ['BEAUTY', 'Alpha']  # Always include these
        
        parts = elements_string.split('", "')
        
        for part in parts:
            part = part.strip('"').strip()
            if not part:
                continue
            
            components = part.split('|')
            if len(components) >= 3:
                name = components[0].strip()
                element_type = components[2].strip()
                
                if element_type not in excluded_types and name not in elements:
                    elements.append(name)
        
        return elements
    
    @classmethod
    def from_path(cls, file_path: str) -> 'CXRFile':
        """Create a CXRFile instance from a file path."""
        path = Path(file_path)
        match = re.match(r'(.+)\.(\d{4})\.\w+$', path.name)
        
        if not match:
            raise ValueError(f"Filename '{path.name}' doesn't match pattern (name.####.ext)")
        
        return cls(
            filename=path.name,
            directory_path=str(path.parent.absolute()),
            frame_number=int(match.group(2)),
            sequence_name=match.group(1),
            elements=None
        )
    
    def __repr__(self) -> str:
        return f"CXRFile({self.filename}, frame={self.frame_number}, elements={len(self.elements)})"
    
    def __str__(self) -> str:
        return f"{self.sequence_name}.{self.frame_number:04d}"
