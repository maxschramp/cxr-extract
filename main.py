#!/usr/bin/env python3
"""Corona CXR Extractor"""

import sys
import os
import subprocess
import argparse
import logging
from pathlib import Path
from collections import defaultdict
from typing import List, Dict

try:
    import inquirer
    from tqdm import tqdm
except ImportError as e:
    print(f"Error: {e.name} package not found. Install with: pip install inquirer tqdm")
    sys.exit(1)

from cxr import CXRFile
from filesystem import collect_cxr_files


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Corona CXR Extractor")
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--ciepath', default=r"C:\Program Files\Chaos\Corona\Corona Renderer for 3ds Max\Image Editor\CoronaImageCmd.exe", help='Path to CoronaImageCmd.exe')
    parser.add_argument('--prefix', default='', help='Prefix for output folder name')
    parser.add_argument('--format', choices=['exr', 'jpg'], default='exr', help='Output format (default: exr)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    return parser.parse_args()


def group_by_sequence(cxr_files: List[CXRFile]) -> Dict[str, List[CXRFile]]:
    """Group CXR files by sequence name."""
    sequences = defaultdict(list)
    for cxr_file in cxr_files:
        sequences[cxr_file.sequence_name].append(cxr_file)
    return {name: sorted(files, key=lambda x: x.frame_number) for name, files in sequences.items()}


def select_files_to_process(cxr_files: List[CXRFile]) -> List[CXRFile]:
    """Interactive selection of CXR files to process."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if len(cxr_files) == 1:
        return cxr_files
    
    sequences = group_by_sequence(cxr_files)
    
    # Multiple sequences
    if len(sequences) > 1:
        answers = inquirer.prompt([inquirer.Checkbox('sequences', message='Select sequences to process', choices=sorted(sequences.keys()))])
        if not answers or not answers['sequences']:
            logging.error("No sequences selected")
            sys.exit(0)
        return [f for seq in answers['sequences'] for f in sequences[seq]]
    
    # Single sequence
    seq_files = list(sequences.values())[0]
    mode = inquirer.prompt([inquirer.List('mode', message='Process entire sequence or individual frames?', choices=['Entire Sequence', 'Individual Frames'])])
    
    if not mode or mode['mode'] == 'Entire Sequence':
        return seq_files
    
    # Individual frames
    frame_choices = [f"{f.sequence_name}.{f.frame_number:04d}" for f in seq_files]
    answers = inquirer.prompt([inquirer.Checkbox('frames', message='Select frames to process', choices=frame_choices)])
    
    if not answers or not answers['frames']:
        logging.error("No frames selected")
        sys.exit(0)
    
    return [f for f in seq_files if f"{f.sequence_name}.{f.frame_number:04d}" in answers['frames']]


def select_elements_to_extract(sequences: Dict[str, List[CXRFile]]) -> Dict[str, List[str]]:
    """Interactive selection of elements to extract for each sequence."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    sequence_elements = {}
    
    for seq_name, files in sequences.items():
        # Get unique elements from first file in sequence (all should have same elements)
        available_elements = files[0].elements
        
        # Add 'All' option at the beginning
        choices = ['All'] + available_elements
        
        answers = inquirer.prompt([inquirer.Checkbox('elements', message=f'Select elements to extract for sequence "{seq_name}"', choices=choices)])
        
        if not answers or not answers['elements']:
            logging.warning(f"No elements selected for {seq_name}, skipping")
            continue
        
        # If 'All' is selected, use special marker
        if 'All' in answers['elements']:
            sequence_elements[seq_name] = ['*']
        else:
            sequence_elements[seq_name] = answers['elements']
    
    return sequence_elements

    if not files:
        return False
def extract_sequence_elements(files: List[CXRFile], elements_to_extract: List[str], ciepath: str, prefix: str = '', file_format: str = 'exr', overwrite: bool = False):
    """Extract elements from all files in a sequence using a single CoronaImageCmd.exe call per element."""
    if not files:
        return False
    
    # Get output directory and sequence info from first file
    output_dir = Path(files[0].directory_path)
    seq_name = files[0].sequence_name
    
    # Create sequence subfolder with optional prefix
    folder_name = f"{prefix}_{seq_name}" if prefix else seq_name
    sequence_dir = output_dir / folder_name
    sequence_dir.mkdir(exist_ok=True)
    
    # Handle 'All' option
    if elements_to_extract == ['*']:
        cmd = [ciepath, "--batch", "-e", "*"]
        files_to_process = []
        
        for cxr_file in files:
            output_path = sequence_dir / f"{seq_name}_ALL.{cxr_file.frame_number:04d}.{file_format}"
            
            if not overwrite and output_path.exists() and output_path.stat().st_size > 0:
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
            logging.error(f"✗ CoronaImageCmd.exe not found at: {ciepath}")
            return False
    else:
        # Extract each element for all files in sequence with one command per element
        for element in elements_to_extract:
            cmd = [ciepath, "--batch", "-e", element]
            files_to_process = []
            
            for cxr_file in files:
                output_path = sequence_dir / f"{seq_name}_{element}.{cxr_file.frame_number:04d}.{file_format}"
                
                if not overwrite and output_path.exists() and output_path.stat().st_size > 0:
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
            except FileNotFoundError:
                logging.error(f"✗ CoronaImageCmd.exe not found at: {ciepath}")
                return False
    
    return True


def main():
    """Main function."""
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(levelname)s: %(message)s')
    
    logging.info(f"Processing input: {args.input}")
    
    cxr_files = collect_cxr_files(args.input)
    
    if not cxr_files:
        logging.error("No CXR files found")
        sys.exit(1)
    
    selected_files = select_files_to_process(cxr_files)
    
    # Group selected files by sequence for element selection
    sequences = group_by_sequence(selected_files)
    sequence_elements = select_elements_to_extract(sequences)
    
    if not sequence_elements:
        logging.error("No elements selected for any sequence")
        sys.exit(1)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    logging.info(f"Processing {len(selected_files)} file(s) across {len(sequences)} sequence(s)")
    
    # Process each sequence
    for seq_name, files in sequences.items():
        elements_to_extract = sequence_elements.get(seq_name)
        
        if not elements_to_extract:
            logging.warning(f"Skipping sequence {seq_name}: no elements selected")
            continue
        
        # Show progress with tqdm
        desc = f"{seq_name} - {'All elements' if elements_to_extract == ['*'] else f'{len(elements_to_extract)} element(s)'}"
        
        with tqdm(total=len(files), desc=desc, unit="frame") as pbar:
            success = extract_sequence_elements(files, elements_to_extract, args.ciepath, prefix=args.prefix, file_format=args.format, overwrite=args.overwrite)
            if success:
                pbar.update(len(files))
            else:
                pbar.write(f"✗ Failed to extract sequence {seq_name}")
    
    logging.info("✓ Extraction complete")


if __name__ == "__main__":
    main()