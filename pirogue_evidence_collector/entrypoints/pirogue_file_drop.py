import argparse
import time

import netifaces
import logging

from rich.logging import RichHandler
from pirogue_admin_client import PirogueAdminClientAdapter
from pirogue_evidence_collector.drop_server.server import DropServer
from pirogue_evidence_collector.utils.qrcode_generator import QRCodeGenerator

LOG_FORMAT = '%(message)s'
logging.basicConfig(level='INFO', format=LOG_FORMAT, handlers=[
    RichHandler(show_path=False, log_time_format='%X')])


def main():
    admin_client = PirogueAdminClientAdapter()
    isolated_iface_address: str = admin_client.get_configuration().get('ISOLATED_ADDRESS')
    arg_parser = argparse.ArgumentParser(
        prog='pirogue-file-drop',
        description='Start a file drop server to collect files from a mobile device',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    arg_parser.add_argument('-i', '--iface', dest='iface', required=False, default=None,
                            help='Specify the network interface to listen on')
    arg_parser.add_argument('-p', '--port', dest='port', required=False, default=8080,
                            help='Specify the port to listen on')
    arg_parser.add_argument('-o', '--output', required=True,
                            help='The output directory')
    args = arg_parser.parse_args()

    if args.iface:
        isolated_iface_address = netifaces.ifaddresses(args.iface)[netifaces.AF_INET][0]['addr']
    url = f'http://{isolated_iface_address}:{args.port}'

    # Open port on the isolated network
    isolated_network_port: int = args.port
    try:
        # Make sure the port is already closed
        admin_client.close_isolated_port(isolated_network_port)
    except Exception: pass
    admin_client.open_isolated_port(isolated_network_port)

    # Launch the web server
    server = DropServer(args.output, host=isolated_iface_address, port=isolated_network_port)
    server.start()
    time.sleep(0.1)
    qg = QRCodeGenerator(url)
    logging.info(f'Flash the QR code on the mobile device or browse {url}')
    qg.generate()
    input('\nPress Enter to stop the server\n')
    server.stop()

    # Close the port
    admin_client.close_isolated_port(args.port)
