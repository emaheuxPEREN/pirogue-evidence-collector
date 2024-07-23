import argparse
import logging

from rich.console import Console
from rich.logging import RichHandler

LOG_FORMAT = '[%(name)s] %(message)s'
logging.basicConfig(level='INFO', format=LOG_FORMAT, handlers=[
    RichHandler(show_path=False, log_time_format='%X')])
console = Console()


def __install_frida():
    from pirogue_evidence_collector.android.device import AndroidDevice
    device = AndroidDevice()
    device.install_latest_frida_server()


def __start_frida():
    from pirogue_evidence_collector.android.device import AndroidDevice
    device = AndroidDevice()
    device.start_frida_server()


def __stop_frida():
    from pirogue_evidence_collector.android.device import AndroidDevice
    device = AndroidDevice()
    device.stop_frida_server()


def main():
    arg_parser = argparse.ArgumentParser(prog='pirogue-android', description='PiRogue Android utils')
    arg_parser.add_argument(
        'action',
        type=str,
        help='Interact with Android device connected to the PiRogue',
        nargs='?',
        choices=['install-frida', 'start-frida', 'stop-frida'])

    args = arg_parser.parse_args()

    android_route = {
        'install-frida': __install_frida,
        'start-frida': __start_frida,
        'stop-frida': __stop_frida,
    }
    android_route.get(args.action, __install_frida)()


if __name__ == '__main__':
    main()
