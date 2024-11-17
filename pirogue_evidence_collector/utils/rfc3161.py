import hashlib
import os
import enum
from pathlib import Path

from pirogue_colander_connector.collectors.ignore import ColanderIgnoreFile
from pyasn1.codec.der import encoder
import requests


try:
    import rfc3161ng
    force_use_openssl = False
except ImportError:
    force_use_openssl = True
import subprocess


class TimestampServer(enum.Enum):
    FREETSA = {
        'home_url': 'https://freetsa.org/index_en.php',
        'base_url': 'https://freetsa.org/tsr',
        'ca_url': 'https://freetsa.org/files/cacert.pem',
        'ca_name': 'freetsa.org_cacert.pem',
        'tsa_url': 'https://freetsa.org/files/tsa.crt',
        'tsa_name': 'freetsa.org_tsa.crt'
    }
    KAKWALAB = {
        'home_url': 'https://uts-server.kakwalab.ovh/',
        'base_url': 'https://uts-server.kakwalab.ovh/',
        'ca_url': 'https://uts-server.kakwalab.ovh/ca.pem',
        'ca_name': 'kakwalab.ovh_ca.pem',
        'tsa_url': 'https://uts-server.kakwalab.ovh/tsa_cert.pem',
        'tsa_name': 'kakwalab.ovh_tsa_cert.pem'
    }

    def download_ca(self, output_dir: Path):
        output_file_path = output_dir / self.value['ca_name']
        if output_file_path.exists():
            return output_file_path
        response = requests.get(self.value['ca_url'], allow_redirects=True)
        if response.status_code == 200:
            with output_file_path.open('wb') as f:
                f.write(response.content)
        return output_file_path

    def download_tsa(self, output_dir: Path):
        output_file_path = output_dir / self.value['tsa_name']
        if output_file_path.exists():
            return output_file_path
        response = requests.get(self.value['tsa_url'], allow_redirects=True)
        if response.status_code == 200:
            with output_file_path.open('wb') as f:
                f.write(response.content)
        return output_file_path


class Timestamper:
    def __init__(self, input_path: Path):
        self.input_path = Path(input_path)
        self.colander_ignore = ColanderIgnoreFile(self.input_path)
        for p in ['*.tsq', '*.tsr', '*.metadata.json', '*.crt', '*.pem', '*.md']:
            self.colander_ignore.add_ignored_pattern(p)
        self.colander_ignore.save_ignore_file()


class FolderTimestamper(Timestamper):
    def __init__(self, input_path, use_openssl=True, server: TimestampServer = TimestampServer.FREETSA):
        super().__init__(input_path)
        self.use_openssl = use_openssl or force_use_openssl
        self.server = server

    def _ignore_file(self, filename):
        if filename.startswith('.'):
            return True
        return self.colander_ignore.is_ignored(Path(filename))

    def _combine_timestamp(self):
        hashes = []
        # Compute the hash of the files contained in the folder
        for file in self.input_path.glob('*'):
            if not file.is_file():
                continue
            if self._ignore_file(file.name):
                continue
            sha512_hash = hashlib.sha512()
            with file.open('rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha512_hash.update(chunk)
            hashes.append((file, sha512_hash.hexdigest()))

        # Write the hashes to a file
        with open(os.path.join(self.input_path, 'hashes.txt'), 'w') as hashes_file:
            for file, hash in hashes:
                hashes_file.write(f'{file.name} {hash}\n')

        # Timestamp the hashes file
        ft = FileTimestamper(hashes_file.name, use_openssl=self.use_openssl, server=self.server)
        ft.timestamp()

        # Write the verification instructions to a README file
        with open(os.path.join(self.input_path, 'README.md'), 'w') as readme_file:
            server_home_url = self.server.value['home_url']
            readme_file.write('# Timestamp verification instructions\n')
            readme_file.write(
                f"The file `hashes.txt` contains the hashes of the files in this folder. "
                f"It has been timestamped by {server_home_url}.\n\n")
            readme_file.write('## Verification commands\n')
            readme_file.write(f'{ft.verification_commands()}\n')

    def timestamp_all(self, combine=False):
        if combine:
            self._combine_timestamp()
        else:
            for file in self.input_path.glob('*'):
                if not file.is_file():
                    continue
                if self._ignore_file(file.name):
                    continue
                ft = FileTimestamper(file, use_openssl=self.use_openssl, server=self.server)
                ft.timestamp()


class FileTimestamper(Timestamper):
    def __init__(self, input_path: Path, use_openssl=True,
                 server: TimestampServer = TimestampServer.FREETSA):
        super().__init__(input_path)
        self.file_path = Path(input_path)
        self.use_openssl = use_openssl or force_use_openssl
        self.output_dir = Path(os.path.dirname(input_path))
        self.output_tsr = self.output_dir / (self.file_path.name + '.tsr')
        self.output_tsq = self.output_dir / (self.file_path.name + '.tsq')
        self.server = server
        self.ca, self.tsa = self.get_remote_certificates()
        self.timestamper = None
        if not self.use_openssl:
            self._prepare_timestamper()

    def _prepare_timestamper(self):
        self.timestamper = rfc3161ng.RemoteTimestamper(
            self.server.value['base_url'],
            hashname='sha512'
        )

    def _openssl_ts_request_command(self):
        return f'openssl ts -query -data {self.file_path} -no_nonce -sha512 -cert -out {self.output_tsq}'

    def _send_openssl_ts_request(self):
        headers = {'Content-Type': 'application/timestamp-query'}
        with self.output_tsq.open('rb') as f:
            data = f.read()
        response = requests.post(self.server.value['base_url'], headers=headers, data=data)
        if response.status_code == 200:
            with self.output_tsr.open('wb') as f:
                f.write(response.content)
        else:
            raise Exception('Unable to send the timestamp request to the server.')

    def get_remote_certificates(self):
        return (
            self.server.download_ca(self.output_dir),
            self.server.download_tsa(self.output_dir)
        )

    def verification_commands(self):
        if not self.use_openssl:
            cmd = f'openssl ts -verify -data {self.file_path} -in {self.file_path}.tsr -queryfile {self.file_path}.tsq -CAfile {self.ca} -untrusted {self.tsa}'
        else:
            cmd = f'''
View the timestamp request  
```openssl ts -query -in {self.output_tsq.name} -text```\n
View the timestamp reply  
```openssl ts -reply -in {self.output_tsr.name} -text```\n
Verify the timestamp  
```openssl ts -verify -in {self.output_tsr.name} -queryfile {self.output_tsq.name} -CAfile {self.ca.name} -untrusted {self.tsa.name}```\n
            '''
        return cmd

    def timestamp(self):
        if self.use_openssl:
            cmd = self._openssl_ts_request_command()
            subprocess.check_call(cmd, shell=True)
            self._send_openssl_ts_request()
        else:
            with open(self.file_path, 'rb') as f:
                tsr = self.timestamper(f.read(), return_tsr=True)
            with open(f'{self.file_path}.tsr', 'wb') as f:
                f.write(encoder.encode(tsr))
