"""Command-line interface for CXR Extract."""

import sys
import argparse
import logging
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from . import __version__
from .filesystem import collect_cxr_files
from .ui import select_files_to_process, select_elements_to_extract, group_by_sequence, clear_screen
from .extractor import ElementExtractor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract render elements from Corona CXR files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cxr-extract scene.0001.cxr
  cxr-extract /path/to/renders/
  cxr-extract scene.cxr --prefix extracted --format jpg
        """
    )
    parser.add_argument('input', help='Input CXR file or directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--ciepath', 
                       default=r"C:\Program Files\Chaos\Corona\Corona Renderer for 3ds Max\Image Editor\CoronaImageCmd.exe",
                       help='Path to CoronaImageCmd.exe')
    parser.add_argument('--prefix', default='', help='Prefix for output folder name')
    parser.add_argument('--format', choices=['exr', 'jpg'], default='exr', 
                       help='Output format (default: exr)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    logging.info(f"CXR Extract v{__version__}")
    logging.info(f"Processing input: {args.input}")
    
    # Collect CXR files
    cxr_files = collect_cxr_files(args.input)
    if not cxr_files:
        logging.error("No CXR files found")
        sys.exit(1)
    
    # Interactive file selection
    selected_files = select_files_to_process(cxr_files)
    sequences = group_by_sequence(selected_files)
    
    # Interactive element selection
    sequence_elements = select_elements_to_extract(sequences)
    if not sequence_elements:
        logging.error("No elements selected for any sequence")
        sys.exit(1)
    
    clear_screen()
    
    # Initialize extractor
    extractor = ElementExtractor(args.ciepath, args.format, args.overwrite)
    
    # Calculate total work
    total_sequences = len(sequence_elements)
    logging.info(f"Processing {len(selected_files)} file(s) across {total_sequences} sequence(s)")
    
    # Process sequences
    if tqdm:
        seq_iterator = tqdm(sequences.items(), desc="Extracting sequences", unit="seq")
    else:
        seq_iterator = sequences.items()
    
    for seq_name, files in seq_iterator:
        elements = sequence_elements.get(seq_name)
        if not elements:
            continue
        
        output_dir = Path(files[0].directory_path)
        success = extractor.extract_sequence(files, elements, output_dir, args.prefix)
        
        if not success:
            logging.error(f"Failed to extract sequence '{seq_name}'")
    
    logging.info("✓ Extraction complete!")


if __name__ == "__main__":
    main()
