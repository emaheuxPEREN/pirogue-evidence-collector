import argparse
import logging
import pathlib

from rich.logging import RichHandler

from pirogue_evidence_collector.utils.rfc3161 import FolderTimestamper

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

    args = arg_parser.parse_args()
    folder_path = args.path

    logging.info(f'Timestamping files in {folder_path}')
    bt = FolderTimestamper(folder_path)
    bt.timestamp_all()
