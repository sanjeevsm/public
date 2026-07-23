#!/usr/bin/env python3
"""
Murex CTT Command Line Tool
Standalone CLI for extracting and creating Murex Configuration Transfer Tool files.

Usage:
    python murex_ctt.py extract --zip <file> [--output <dir>]
    python murex_ctt.py create  --folder <dir> [--output <file>]
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Make dashboard_api importable from scripts/
_script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_script_dir.parent / 'dashboard_api'))

try:
    from services.murex_ctt import MurexCTTService
except ImportError as e:
    print(f"Error: Could not import MurexCTTService — {e}", file=sys.stderr)
    print("Make sure you are running this with the venv Python:", file=sys.stderr)
    print("  Windows : dashboard_api\\.venv\\Scripts\\python.exe scripts\\murex_ctt.py ...", file=sys.stderr)
    print("  macOS/Linux: dashboard_api/.venv/bin/python scripts/murex_ctt.py ...", file=sys.stderr)
    sys.exit(1)


# ── helpers ───────────────────────────────────────────────────────────────────

def _fmt_size(n: int) -> str:
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return f"{n:.1f} {unit}" if unit != 'B' else f"{n} B"
        n /= 1024
    return f"{n:.1f} TB"


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_extract(args):
    zip_path = Path(args.zip).resolve()

    if not zip_path.exists():
        print(f"Error: file not found: {zip_path}", file=sys.stderr)
        sys.exit(1)
    if zip_path.suffix.lower() != '.zip':
        print(f"Error: file must have a .zip extension: {zip_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output).resolve() if args.output else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting : {zip_path}")
    print(f"Output dir : {output_dir}")
    print()

    service = MurexCTTService(workspace_dir=str(output_dir))
    results = service.extract_ctt(zip_path, output_dir)

    if results['success']:
        extracted_folder = output_dir / zip_path.stem
        print(f"  Files extracted   : {len(results['extracted_files'])}")
        print(f"  Nested zips found : {len(results['nested_zips'])}")
        print(f"  Output folder     : {extracted_folder}")
        if results['errors']:
            print(f"  Warnings          : {len(results['errors'])}")
            for w in results['errors']:
                print(f"    - {w}")
        print()
        print("Done.")
    else:
        print("Extraction failed:", file=sys.stderr)
        for err in results['errors']:
            print(f"  {err}", file=sys.stderr)
        sys.exit(1)


def cmd_create(args):
    folder = Path(args.folder).resolve()

    if not folder.exists():
        print(f"Error: folder not found: {folder}", file=sys.stderr)
        sys.exit(1)
    if not folder.is_dir():
        print(f"Error: not a directory: {folder}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_zip = Path(args.output).resolve()
        if not output_zip.suffix:
            output_zip = output_zip.with_suffix('.zip')
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_zip = Path.cwd() / f"{folder.name}_{timestamp}.zip"

    output_zip.parent.mkdir(parents=True, exist_ok=True)

    print(f"Source folder : {folder}")
    print(f"Output zip    : {output_zip}")
    print()

    service = MurexCTTService()
    results = service.create_ctt(folder, output_zip)

    if results['success']:
        size = output_zip.stat().st_size
        print(f"  Files zipped        : {len(results['zipped_files'])}")
        print(f"  Nested zips created : {len(results['nested_zips'])}")
        print(f"  Output file         : {output_zip}")
        print(f"  Size                : {_fmt_size(size)}")
        if results['errors']:
            print(f"  Warnings            : {len(results['errors'])}")
            for w in results['errors']:
                print(f"    - {w}")
        print()
        print("Done.")
    else:
        print("Creation failed:", file=sys.stderr)
        for err in results['errors']:
            print(f"  {err}", file=sys.stderr)
        sys.exit(1)


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog='murex_ctt',
        description='Murex Configuration Transfer Tool (CTT) — Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract a CTT zip to the current directory
  python murex_ctt.py extract --zip DM_CTT.zip

  # Extract to a specific output folder
  python murex_ctt.py extract --zip DM_CTT.zip --output ~/ctt/extracted

  # Create a CTT zip from a folder (auto-named with timestamp)
  python murex_ctt.py create --folder DM_CTT

  # Create a CTT zip with a specific output path
  python murex_ctt.py create --folder ~/ctt/DM_CTT --output ~/ctt/output/DM_CTT.zip
        """
    )
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    sub = parser.add_subparsers(dest='command', metavar='<command>')
    sub.required = True

    # extract
    ep = sub.add_parser(
        'extract',
        help='Extract a CTT zip file into folder structure',
        description=(
            'Extract a Murex CTT zip file. '
            'Nested zips are automatically detected and extracted recursively, '
            'preserving the original folder hierarchy.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python murex_ctt.py extract --zip DM_CTT.zip
  python murex_ctt.py extract -z DM_CTT.zip -o ~/ctt/extracted
  python murex_ctt.py extract --zip /path/to/DM_CTT.zip --output ~/ctt/extracted
        """
    )
    ep.add_argument('--zip',    '-z', required=True, metavar='<file>',
                    help='Path to the CTT .zip file to extract')
    ep.add_argument('--output', '-o', metavar='<dir>',
                    help='Destination directory (default: current working directory)')
    ep.set_defaults(func=cmd_extract)

    # create
    cp = sub.add_parser(
        'create',
        help='Create a CTT zip from a folder structure',
        description=(
            'Create a Murex CTT zip from a folder. '
            'Each subdirectory is converted to a nested zip, '
            'mirroring the structure expected by Murex CTT.'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python murex_ctt.py create --folder DM_CTT
  python murex_ctt.py create -f DM_CTT -o DM_CTT_release.zip
  python murex_ctt.py create --folder ~/ctt/DM_CTT --output ~/releases/DM_CTT.zip
        """
    )
    cp.add_argument('--folder', '-f', required=True, metavar='<dir>',
                    help='Source folder to package into a CTT zip')
    cp.add_argument('--output', '-o', metavar='<file>',
                    help='Output zip file path (default: <folder>_YYYYMMDD_HHMMSS.zip in current dir)')
    cp.set_defaults(func=cmd_create)

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    args.func(args)


if __name__ == '__main__':
    main()
