#!/usr/bin/env python
"""
Command-line interface for zacro
"""

import argparse
import os
import sys

from .zacro import xacro_to_file
from .zacro import xacro_to_string


def main():
    """Main entry point for zacro command-line tool"""
    parser = argparse.ArgumentParser(
        description='Fast Rust implementation of xacro (XML macro language)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zacro robot.xacro                    # Process to stdout
  zacro robot.xacro -o robot.urdf      # Process to file
  zacro robot.xacro --format           # Format output with indentation
  zacro robot.xacro --remove-first-joint  # Remove first joints (modular robots)
  zacro robot.xacro --format --remove-first-joint -o robot.urdf  # All options
        """
    )

    parser.add_argument('input_file',
                        help='Input xacro file to process')
    parser.add_argument('-o', '--output',
                        help='Output file (default: stdout)')
    parser.add_argument('--format', action='store_true',
                        help='Format output with proper indentation')
    parser.add_argument('--remove-first-joint', action='store_true',
                        help='Remove first joint from each macro expansion (for modular robots)')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                        help='Verbosity level (default: 1)')
    # Import __version__ here to ensure dynamic version loading
    from . import __version__
    parser.add_argument('--version', action='version', version=f'zacro {__version__}')

    # Add parameter mapping support
    parser.add_argument('-p', '--param', action='append', metavar='KEY:=VALUE',
                        help='Set parameter values (can be used multiple times)')

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)

    # Parse parameter mappings
    mappings = {}
    if args.param:
        for param in args.param:
            if ':=' not in param:
                print(f"Error: Invalid parameter format '{param}'. Use KEY:=VALUE", file=sys.stderr)
                sys.exit(1)
            key, value = param.split(':=', 1)
            mappings[key.strip()] = value.strip()

    mappings = mappings if mappings else None

    try:
        if args.output:
            # Process to file
            xacro_to_file(
                args.input_file,
                args.output,
                mappings=mappings,
                verbosity=args.verbosity,
                format_output=args.format,
                remove_first_joint=args.remove_first_joint
            )
            if args.verbosity > 0:
                print(f"Successfully processed '{args.input_file}' -> '{args.output}'", file=sys.stderr)
        else:
            # Process to stdout
            result = xacro_to_string(
                args.input_file,
                mappings=mappings,
                verbosity=args.verbosity,
                format_output=args.format,
                remove_first_joint=args.remove_first_joint
            )
            print(result)

    except Exception as e:
        print(f"Error processing '{args.input_file}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
