#!/usr/bin/env python3
"""
DS Save Converter - Universal Nintendo DS Save File Converter

A smart utility to convert DS save files between different formats and sizes.
Automatically detects whether to expand (for TWiLight Menu++) or trim (for flashcarts).
"""

import sys
import os
import argparse
from pathlib import Path

__version__ = "1.0.0"
__author__ = "DS Save Converter Team"
__description__ = "Universal Nintendo DS Save File Converter"

def find_actual_data_end(filename):
    """
    Find the position after the last non-zero byte.
    Scans from the end of file backwards until it finds a non-zero byte.
    
    Args:
        filename (str): Path to the save file
        
    Returns:
        int: Position after the last meaningful byte
    """
    with open(filename, 'rb') as f:
        data = f.read()
    
    # Start from the end, find first non-zero byte
    for i in range(len(data) - 1, -1, -1):
        if data[i] != 0:
            return i + 1  # Return position after the last meaningful byte
    
    return 0  # File is all zeros

def smart_trim_size(actual_data_end):
    """
    Round up to the nearest standard DS save size if we're close.
    This handles cases where legitimate save data ends with zeros.
    
    Standard DS save sizes: 64KB, 128KB, 256KB, 512KB
    If actual data is within 5% of a standard size, round up to that size.
    
    Args:
        actual_data_end (int): Actual end position of non-zero data
        
    Returns:
        int: Smart-trimmed size (rounded up if close to standard size)
    """
    standard_sizes = [64*1024, 128*1024, 256*1024, 512*1024]
    
    for size in standard_sizes:
        # If we're within 5% of a standard size, use that size
        if actual_data_end > size * 0.95 and actual_data_end <= size:
            return size
    
    # Otherwise use the natural size
    return actual_data_end

def convert_save(input_file, output_file=None, target_size_kb=None, verbose=True):
    """
    Convert DS save file between different formats/sizes.
    
    Args:
        input_file (str): Input save file path
        output_file (str, optional): Output save file path
        target_size_kb (int, optional): Target size in KB
        verbose (bool): Print detailed information
        
    Returns:
        str: Path to the converted file
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if output_file is None:
        output_file = input_path.with_name(f"{input_path.stem}_converted{input_path.suffix}")
    
    file_size = input_path.stat().st_size
    actual_data_end = find_actual_data_end(input_file)
    trailing_zeros = file_size - actual_data_end
    
    # Auto-detect mode based on file size
    if target_size_kb is None:
        if file_size < 512 * 1024:  # Less than 512KB
            # Expansion mode - expand to 512KB
            final_size = 512 * 1024
            mode = "expansion"
            if verbose:
                print(f"Auto-detected: EXPANSION mode ({file_size//1024}KB -> 512KB)")
        else:
            # Trimming mode - use smart trim size
            final_size = smart_trim_size(actual_data_end)
            mode = "trimming"
            if verbose:
                smart_size_kb = final_size // 1024
                natural_size_kb = actual_data_end // 1024
                if final_size != actual_data_end:
                    print(f"Auto-detected: SMART TRIMMING mode (rounded {natural_size_kb}KB -> {smart_size_kb}KB)")
                else:
                    print(f"Auto-detected: TRIMMING mode (removing {trailing_zeros} trailing zeros)")
    else:
        # Manual mode
        final_size = target_size_kb * 1024
        mode = "manual"
        if verbose:
            print(f"Manual mode: forcing {target_size_kb}KB")
    
    # Perform the conversion
    with open(input_file, 'rb') as src, open(output_file, 'wb') as dst:
        if final_size <= file_size:
            # Truncate
            data = src.read(final_size)
        else:
            # Expand with zeros
            data = src.read()
            data += b'\x00' * (final_size - len(data))
        
        dst.write(data)
    
    if verbose:
        print(f"Input file size: {file_size} bytes ({file_size//1024}KB)")
        print(f"Actual data ends at: {actual_data_end} bytes")
        if final_size != actual_data_end:
            print(f"Smart rounded to: {final_size} bytes ({final_size//1024}KB)")
        print(f"Trailing zeros: {trailing_zeros} bytes")
        print(f"Output size: {final_size} bytes ({final_size//1024}KB)")
        print(f"Mode: {mode}")
        print(f"Saved: {output_file}")
    
    return str(output_file)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Universal Nintendo DS Save File Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s game.sav                    # Auto-detect conversion mode
  %(prog)s game.sav converted.sav      # Auto-detect with custom output
  %(prog)s game.sav converted.sav 128  # Force 128KB output
  %(prog)s -q game.sav                 # Quiet mode (minimal output)

Auto-detection modes:
  < 512KB file → Expands to 512KB (for TWiLight Menu++)
  = 512KB file → Trims trailing zeros (for R4/flashcarts)
        """
    )
    
    parser.add_argument('input_file', help='Input save file')
    parser.add_argument('output_file', nargs='?', help='Output save file (optional)')
    parser.add_argument('target_size', nargs='?', type=int, 
                       help='Target size in KB (optional)')
    parser.add_argument('-q', '--quiet', action='store_true', 
                       help='Quiet mode (minimal output)')
    parser.add_argument('-v', '--version', action='version', 
                       version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    try:
        output_path = convert_save(
            args.input_file, 
            args.output_file, 
            args.target_size,
            verbose=not args.quiet
        )
        
        if args.quiet:
            print(output_path)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
