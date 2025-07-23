import logging
import lzma

import requests


FRIDA_SERVER_LATEST_RELEASE_URL = 'https://api.github.com/repos/frida/frida/releases/latest'
FRIDA_SERVER_RELEASE_BY_TAG_URL = 'https://api.github.com/repos/frida/frida/releases/tags/{TAG}'
log = logging.getLogger(__name__)


class FridaServer:
    @staticmethod
    def download_frida_server(arch: str, output_file: str, platform: str, client_version: str):
        if not arch:
            log.error(f'Unable to determine device ABI, please install Frida server manually at {output_file}')
            return
        resp = requests.get(FRIDA_SERVER_RELEASE_BY_TAG_URL.format(TAG=client_version))
        try:
            resp.raise_for_status()
            release = resp.json()
            assert release.get('tag_name') == client_version
            for asset in release['assets']:
                asset_name = asset['name']
                if 'server' in asset_name and f'{platform}-{arch}.xz' in asset_name:
                    log.info(f'Downloading {asset["browser_download_url"]}...')
                    xz_file = requests.get(asset['browser_download_url'])
                    xz_file.raise_for_status()
                    log.info(f'Extracting {asset_name}...')
                    server_binary = lzma.decompress(xz_file.content)
                    log.info(f'Writing {asset_name} to {output_file}...')
                    with open(output_file, mode='wb') as out:
                        out.write(server_binary)
                        out.flush()
                    return
            raise FileNotFoundError((arch, platform, client_version))
        except Exception as e:
            log.error(
                f'Unable to find frida-server version {client_version} in GitHub releases. '
                'Please install it by hand at /data/local/tmp/frydaxx-server and make it executable using chmod +x.'
            )
            raise Exception(f'Unable to find frida-server version {client_version} in GitHub releases.') from e
