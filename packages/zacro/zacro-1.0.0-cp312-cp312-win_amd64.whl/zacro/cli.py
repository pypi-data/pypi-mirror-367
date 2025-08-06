#!/usr/bin/env python
"""
Command-line interface for zacro
"""

import argparse
import os
import sys

# All validation is now handled by Rust implementation
from .tree import print_urdf_tree
from .zacro import xacro_to_file
from .zacro import xacro_to_string


def main():
    """Main entry point for zacro command-line tool"""
    parser = argparse.ArgumentParser(
        description='Fast Rust implementation of xacro (XML macro language)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  zacro robot.xacro                    # Process to stdout (formatted and validated by default)
  zacro robot.xacro -o robot.urdf      # Process to file (formatted and validated by default)
  zacro robot.xacro --tree             # Show link tree structure
  zacro robot.xacro --no-format        # Disable formatting output
  zacro robot.xacro --remove-first-joint  # Remove first joints (modular robots)
  zacro robot.xacro --no-validate --remove-first-joint -o robot.urdf  # All options
        """
    )

    parser.add_argument('input_file',
                        help='Input xacro file to process')
    parser.add_argument('-o', '--output',
                        help='Output file (default: stdout)')
    parser.add_argument('--no-format', action='store_true',
                        help='Disable formatting output (formatting is enabled by default)')
    parser.add_argument('--remove-first-joint', action='store_true',
                        help='Remove first joint from each macro expansion (for modular robots)')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                        help='Verbosity level (default: 1)')
    parser.add_argument('--no-validate', action='store_true', default=False,
                        help='Disable URDF validation (validation is enabled by default)')
    parser.add_argument('--no-validation-verbose', action='store_true', default=False,
                        help='Suppress validation output details')
    parser.add_argument('--tree', action='store_true', default=False,
                        help='Show URDF link tree structure instead of XML output')
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
    validation_verbose = not args.no_validation_verbose
    validate = not args.no_validate  # Validation is enabled by default
    format_output = not args.no_format  # Format output is enabled by default

    try:
        if args.tree:
            # Show tree structure instead of XML
            result = xacro_to_string(
                args.input_file,
                mappings=mappings,
                verbosity=args.verbosity,
                format_output=format_output,
                remove_first_joint=args.remove_first_joint,
                validate_urdf=validate,
                validation_verbose=validation_verbose
            )
            # Generate and print tree
            tree_output = print_urdf_tree(result)
            print(tree_output)
        elif validate:
            # Use Rust-based validation
            if args.output:
                # Process to file with validation
                result = xacro_to_string(
                    args.input_file,
                    mappings=mappings,
                    verbosity=args.verbosity,
                    format_output=format_output,
                    remove_first_joint=args.remove_first_joint,
                    validate_urdf=True,
                    validation_verbose=validation_verbose
                )
                # Write result to file
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                if args.verbosity > 0:
                    print(f"Successfully processed and validated '{args.input_file}' -> '{args.output}'",
                          file=sys.stderr)
            else:
                # Process to stdout with validation
                result = xacro_to_string(
                    args.input_file,
                    mappings=mappings,
                    verbosity=args.verbosity,
                    format_output=format_output,
                    remove_first_joint=args.remove_first_joint,
                    validate_urdf=True,
                    validation_verbose=validation_verbose
                )
                print(result)
        else:
            # Process without validation
            if args.output:
                # Process to file
                xacro_to_file(
                    args.input_file,
                    args.output,
                    mappings=mappings,
                    verbosity=args.verbosity,
                    format_output=format_output,
                    remove_first_joint=args.remove_first_joint,
                    validate_urdf=False
                )
                if args.verbosity > 0:
                    print(f"Successfully processed '{args.input_file}' -> '{args.output}'", file=sys.stderr)
            else:
                # Process to stdout
                result = xacro_to_string(
                    args.input_file,
                    mappings=mappings,
                    verbosity=args.verbosity,
                    format_output=format_output,
                    remove_first_joint=args.remove_first_joint,
                    validate_urdf=False
                )
                print(result)

    except Exception as e:
        # Check if it's a validation error from Rust
        error_msg = str(e)
        if "URDF validation failed" in error_msg or "validation error" in error_msg.lower():
            print(f"URDF validation failed for '{args.input_file}':", file=sys.stderr)
            print(error_msg, file=sys.stderr)
            sys.exit(2)  # Different exit code for validation errors
        else:
            print(f"Error processing '{args.input_file}': {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
