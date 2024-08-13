import argparse
import logging
import pathlib

from rich.logging import RichHandler

from pirogue_evidence_collector.utils.rfc3161 import FolderTimestamper, FileTimestamper

LOG_FORMAT = '%(message)s'
logging.basicConfig(level='INFO', format=LOG_FORMAT, handlers=[
    RichHandler(show_path=False, log_time_format='%X')])


def main():
    arg_parser = argparse.ArgumentParser(
        prog='pirogue-timestamp',
        description='Add a trusted timestamp to all the files contained in a folder'
    )
    arg_parser.add_argument(
        '-p',
        '--path',
        help='Path of the folder containing the files to be timestamped',
        required=True,
        type=pathlib.Path
    )
    arg_parser.add_argument(
        '-c',
        '--combine',
        help='Combine all the files in the folder into a single file of hashes and time stamp it instead of time '
             'stamping each file individually',
        default=False,
        required=False,
        type=bool
    )

    args = arg_parser.parse_args()
    target_path = args.path

    if target_path.is_dir():
        logging.info(f'Timestamping the files contained in {target_path}')
        bt = FolderTimestamper(target_path)
        bt.timestamp_all(args.combine)
    elif target_path.is_file():
        logging.info(f'Timestamping the file {target_path}')
        ft = FileTimestamper(target_path)
        ft.timestamp()

