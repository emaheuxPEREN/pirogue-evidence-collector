import argparse
import threading

import frida

from pirogue_evidence_collector.frida.capture_manager import CaptureManager


def on_spawned(spawn):
    print('on_spawned:', spawn)
    FridaApplication.pending.append(spawn)
    FridaApplication.event.set()


def on_message(capture_manager, spawn, message, script):
    # Pass options to friTap hooks
    if message['payload'] == 'experimental':
        script.post({'type': 'experimental', 'payload': False})
        return
    if message['payload'] == 'defaultFD':
        script.post({'type': 'defaultFD', 'payload': False})
        return
    if message['payload'] == 'anti':
        script.post({'type': 'antiroot', 'payload': False})
        return

    # Received data from the Frida hooks
    if message['type'] == 'send':
        data = message.get('payload')
        # Specific handling for friTap data
        if data and data.get('contentType', '') == 'keylog':
            data['dump'] = 'sslkeylog.txt'
            data['type'] = 'sslkeylog'
            data['data'] = data.get('keylog')
        if data:
            capture_manager.capture_data(data)


class FridaApplication:
    pending = []
    sessions = []
    scripts = []
    event = threading.Event()

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--capture-command',
            help=(
                'Specify directly a capture command instead of building it from interface. '
                'Useful for remote capture over SSH. Example:\n'
                'ssh root@openwrt "tcpdump -U -n -w - -i wlan0 \'host PHONE_IP\'"'
            )
        )
        parser.add_argument('-o', '--output', help='The output directory')
        parser.add_argument('-i', '--iface', help='The network interface to capture', default=None)
        parser.add_argument('--disable-screenrecord', action='store_false', help='Use to disable screen recording')
        self.options = parser.parse_args()
        self._device = None

        self.capture_manager = CaptureManager(self.options.output, self.options.iface, self.options.disable_screenrecord)

    def save_data(self):
        self.capture_manager.stop_capture()

    def run(self):
        self.capture_manager.start_capture(capture_cmd=self.options.capture_command)

        self._device = frida.get_usb_device()
        self._device.on('spawn-added', on_spawned)
        self._device.enable_spawn_gating()
        FridaApplication.event = threading.Event()

        print('Enabled spawn gating')
        print('Pending:', self._device.enumerate_pending_spawn())
        for spawn in self._device.enumerate_pending_spawn():
            print('Resuming:', spawn)
            self._device.resume(spawn.pid)
        while True:
            while len(FridaApplication.pending) == 0:
                print('Waiting for data')
                FridaApplication.event.wait()
                FridaApplication.event.clear()
            spawn = FridaApplication.pending.pop()
            if spawn.identifier:
                print('Instrumenting:', spawn)
                session = self._device.attach(spawn.pid)
                script = session.create_script(self.capture_manager.get_agent_script())
                script.on('message', lambda message, data: on_message(self.capture_manager, spawn, message, script))
                script.load()
                api = script.exports
                api.socket_trace(spawn.pid, spawn.identifier)
                api.log_ssl_keys()
                try:
                    api.log_aes_info(spawn.pid, spawn.identifier)
                except Exception:
                    pass
                api.log_ad_ids()
                api.no_root()
                hook_definitions, success = self.capture_manager.get_dynamic_hooks_definitions()
                if success:
                    api.inject_dynamic_hooks(spawn.pid, spawn.identifier, hook_definitions)
                FridaApplication.sessions.append(session)
                FridaApplication.scripts.append(script)
            else:
                print('Not instrumenting:', spawn)
            self._device.resume(spawn.pid)
            print('Processed:', spawn)
