import argparse
import time

import netifaces
import logging

from rich.logging import RichHandler
from pirogue_evidence_collector.drop_server.server import DropServer
from pirogue_evidence_collector.utils.qrcode_generator import QRCodeGenerator

LOG_FORMAT = '%(message)s'
logging.basicConfig(level='INFO', format=LOG_FORMAT, handlers=[
    RichHandler(show_path=False, log_time_format='%X')])


def main():
    arg_parser = argparse.ArgumentParser(
        prog='pirogue-file-drop',
        description='Start a file drop server to collect files from a mobile device',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    arg_parser.add_argument('-i', '--iface', dest='iface', required=True,
                            help='Specify the network interface to listen on')
    arg_parser.add_argument('-p', '--port', dest='port', required=False, default=8080,
                            help='Specify the port to listen on')
    arg_parser.add_argument('-o', '--output', required=True,
                            help='The output directory')
    args = arg_parser.parse_args()

    if args.iface not in netifaces.interfaces():
        raise ValueError(f'Interface {args.iface} not found')

    ip = netifaces.ifaddresses(args.iface)[netifaces.AF_INET][0]['addr']
    url = f'http://{ip}:{args.port}'
    server = DropServer(args.output, '0.0.0.0', args.port)
    server.start()
    time.sleep(0.1)
    qg = QRCodeGenerator(url)
    logging.info(f'Flash the QR code on the mobile device or browse {url}')
    qg.generate()
    input('\nPress Enter to stop the server\n')
    server.stop()
