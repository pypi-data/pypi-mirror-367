
#!/usr/bin/env python3
"""
Command Line Interface for Quantum File System
"""

import argparse
import sys
import os
from .converter import QuantumConverter

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Quantum File System - Convert between JSON and QJSON formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  quantum-fs input.json -k "mykey123" --to-qjson -o output.qjson
  quantum-fs encrypted.qjson -k "mykey123" --to-json -o decrypted.json
        """
    )
    
    parser.add_argument('input_file', help='Input file path (JSON or QJSON)')
    parser.add_argument('-k', '--key', required=True, help='Authentication key for encryption/decryption')
    parser.add_argument('-o', '--output', required=True, help='Output file path')
    
    # Conversion type (mutually exclusive)
    conversion_group = parser.add_mutually_exclusive_group(required=True)
    conversion_group.add_argument('--to-qjson', action='store_true', help='Convert JSON to QJSON')
    conversion_group.add_argument('--to-json', action='store_true', help='Convert QJSON to JSON')
    
    parser.add_argument('--version', action='version', version='Quantum File System 0.1.0')
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Initialize converter with the provided key
        converter = QuantumConverter(args.key)
        
        if args.to_qjson:
            # Convert JSON to QJSON
            print(f"Converting {args.input_file} to QJSON format...")
            converter.json_to_qjson(args.input_file, args.output)
            print(f"✓ Successfully created {args.output}")
            
        elif args.to_json:
            # Convert QJSON to JSON
            print(f"Converting {args.input_file} to JSON format...")
            converter.qjson_to_json(args.input_file, args.output)
            print(f"✓ Successfully created {args.output}")
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
