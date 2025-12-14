"""Extraction logic for CXR render elements."""

import subprocess
import logging
from pathlib import Path
from typing import List

from .core import CXRFile


class ElementExtractor:
    """Handles extraction of render elements from CXR files."""
    
    def __init__(self, cie_path: str, output_format: str = 'exr', overwrite: bool = False):
        self.cie_path = cie_path
        self.output_format = output_format
        self.overwrite = overwrite
    
    def extract_sequence(self, files: List[CXRFile], elements: List[str], 
                        output_dir: Path, prefix: str = '') -> bool:
        """Extract elements from all files in a sequence."""
        if not files:
            return False
        
        seq_name = files[0].sequence_name
        folder_name = f"{prefix}_{seq_name}" if prefix else seq_name
        sequence_dir = output_dir / folder_name
        sequence_dir.mkdir(exist_ok=True)
        
        # Handle 'All' option
        if elements == ['*']:
            return self._extract_all_elements(files, sequence_dir, seq_name)
        
        # Extract specific elements
        return self._extract_specific_elements(files, elements, sequence_dir, seq_name)
    
    def _extract_all_elements(self, files: List[CXRFile], output_dir: Path, 
                             seq_name: str) -> bool:
        """Extract all elements using wildcard."""
        cmd = [self.cie_path, "--batch", "-e", "*"]
        files_to_process = []
        
        for cxr_file in files:
            output_path = output_dir / f"{seq_name}_ALL.{cxr_file.frame_number:04d}.{self.output_format}"
            
            if not self.overwrite and output_path.exists() and output_path.stat().st_size > 0:
                logging.debug(f"Skipping existing file: {output_path.name}")
                continue
            
            cmd.extend([cxr_file.full_path, str(output_path)])
            files_to_process.append(cxr_file)
        
        if not files_to_process:
            logging.info(f"All files already exist for {seq_name} (all elements), skipping")
            return True
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"✗ Failed to extract all elements: {e.stderr}")
            return False
        except FileNotFoundError:
            logging.error(f"✗ CoronaImageCmd.exe not found at: {self.cie_path}")
            return False
    
    def _extract_specific_elements(self, files: List[CXRFile], elements: List[str],
                                   output_dir: Path, seq_name: str) -> bool:
        """Extract specific named elements."""
        for element in elements:
            cmd = [self.cie_path, "--batch", "-e", element]
            files_to_process = []
            
            for cxr_file in files:
                output_path = output_dir / f"{seq_name}_{element}.{cxr_file.frame_number:04d}.{self.output_format}"
                
                if not self.overwrite and output_path.exists() and output_path.stat().st_size > 0:
                    logging.debug(f"Skipping existing file: {output_path.name}")
                    continue
                
                cmd.extend([cxr_file.full_path, str(output_path)])
                files_to_process.append(cxr_file)
            
            if not files_to_process:
                logging.info(f"All files already exist for {seq_name} - {element}, skipping")
                continue
            
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"✗ Failed to extract {element}: {e.stderr}")
                return False
            except FileNotFoundError:
                logging.error(f"✗ CoronaImageCmd.exe not found at: {self.cie_path}")
                return False
        
        return True
