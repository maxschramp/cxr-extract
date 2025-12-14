"""User interface components for interactive selection."""

import os
import sys
import logging
from collections import defaultdict
from typing import List, Dict

try:
    import inquirer
except ImportError:
    inquirer = None

from .core import CXRFile


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def group_by_sequence(cxr_files: List[CXRFile]) -> Dict[str, List[CXRFile]]:
    """Group CXR files by sequence name and sort by frame number."""
    sequences = defaultdict(list)
    for cxr_file in cxr_files:
        sequences[cxr_file.sequence_name].append(cxr_file)
    return {name: sorted(files, key=lambda x: x.frame_number) for name, files in sequences.items()}


def select_files_to_process(cxr_files: List[CXRFile]) -> List[CXRFile]:
    """Interactive selection of CXR files to process."""
    if not inquirer:
        logging.error("inquirer package not available")
        return cxr_files
    
    clear_screen()
    
    if len(cxr_files) == 1:
        return cxr_files
    
    sequences = group_by_sequence(cxr_files)
    
    # Multiple sequences
    if len(sequences) > 1:
        return _select_sequences(sequences)
    
    # Single sequence
    return _select_frames(list(sequences.values())[0])


def _select_sequences(sequences: Dict[str, List[CXRFile]]) -> List[CXRFile]:
    """Select which sequences to process."""
    answers = inquirer.prompt([
        inquirer.Checkbox('sequences', 
                         message='Select sequences to process', 
                         choices=sorted(sequences.keys()))
    ])
    
    if not answers or not answers['sequences']:
        logging.error("No sequences selected")
        sys.exit(0)
    
    return [f for seq in answers['sequences'] for f in sequences[seq]]


def _select_frames(seq_files: List[CXRFile]) -> List[CXRFile]:
    """Select entire sequence or individual frames."""
    mode = inquirer.prompt([
        inquirer.List('mode', 
                     message='Process entire sequence or individual frames?', 
                     choices=['Entire Sequence', 'Individual Frames'])
    ])
    
    if not mode or mode['mode'] == 'Entire Sequence':
        return seq_files
    
    # Individual frame selection
    frame_choices = [f"{f.sequence_name}.{f.frame_number:04d}" for f in seq_files]
    answers = inquirer.prompt([
        inquirer.Checkbox('frames', 
                         message='Select frames to process', 
                         choices=frame_choices)
    ])
    
    if not answers or not answers['frames']:
        logging.error("No frames selected")
        sys.exit(0)
    
    return [f for f in seq_files if f"{f.sequence_name}.{f.frame_number:04d}" in answers['frames']]


def select_elements_to_extract(sequences: Dict[str, List[CXRFile]]) -> Dict[str, List[str]]:
    """Interactive selection of elements to extract for each sequence."""
    if not inquirer:
        logging.error("inquirer package not available")
        return {}
    
    clear_screen()
    sequence_elements = {}
    
    for seq_name, files in sequences.items():
        available_elements = files[0].elements
        choices = ['All'] + available_elements
        
        answers = inquirer.prompt([
            inquirer.Checkbox('elements', 
                            message=f'Select elements to extract for sequence "{seq_name}"', 
                            choices=choices)
        ])
        
        if not answers or not answers['elements']:
            logging.warning(f"No elements selected for {seq_name}, skipping")
            continue
        
        # Use wildcard for 'All' option
        sequence_elements[seq_name] = ['*'] if 'All' in answers['elements'] else answers['elements']
    
    return sequence_elements
