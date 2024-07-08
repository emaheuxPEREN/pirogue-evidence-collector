import os
import enum
import glob
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

    def download_ca(self, output_dir):
        output_file_path = os.path.join(output_dir, self.value['ca_name'])
        if os.path.exists(output_file_path):
            return output_file_path
        response = requests.get(self.value['ca_url'], allow_redirects=True)
        if response.status_code == 200:
            with open(output_file_path, 'wb') as f:
                f.write(response.content)
        return output_file_path

    def download_tsa(self, output_dir):
        output_file_path = os.path.join(output_dir, self.value['tsa_name'])
        if os.path.exists(output_file_path):
            return output_file_path
        response = requests.get(self.value['tsa_url'], allow_redirects=True)
        if response.status_code == 200:
            with open(output_file_path, 'wb') as f:
                f.write(response.content)
        return output_file_path


class BatchFileTimestamper:
    def __init__(self, input_folder, use_openssl=True, server: TimestampServer = TimestampServer.FREETSA):
        self.input_folder = input_folder
        self.use_openssl = use_openssl or force_use_openssl
        self.server = server
        self.readme_content = ''

    @staticmethod
    def _extension_to_ignore(filename):
        for ext in ['.tsq', '.tsr', '.metadata.json', 'crt', 'pem', 'md']:
            if filename.endswith(ext):
                return True
        return False

    def timestamp_all(self):
        with open(os.path.join(self.input_folder, 'README.md'), 'w') as readme_file:
            server_home_url = self.server.value['home_url']
            readme_file.write('# Timestamp verification instructions\n')
            readme_file.write(f'The following files have been timestamped by {server_home_url}.\n\n')
            for f in glob.glob(self.input_folder + '/*', recursive=False):
                if not os.path.isfile(f):
                    continue
                if BatchFileTimestamper._extension_to_ignore(f):
                    continue
                ft = FileTimestamper(f, use_openssl=self.use_openssl, server=self.server)
                ft.timestamp()
                readme_file.write(f'## For file `{f}`\n')
                readme_file.write(f'```\n{ft.verification_commands()}\n```\n\n')


class FileTimestamper:
    def __init__(self, file_path, use_openssl=True, server: TimestampServer = TimestampServer.FREETSA):
        self.file_path = file_path
        self.use_openssl = use_openssl or force_use_openssl
        self.output_dir = os.path.dirname(file_path)
        self.output_tsr = file_path + '.tsr'
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
        # openssl ts -query -data file.png -no_nonce -sha512 -cert -out file.tsq
        return f'openssl ts -query -data {self.file_path} -no_nonce -sha512 -cert -out {self.file_path}.tsq'

    def _send_openssl_ts_request(self):
        headers = {'Content-Type': 'application/timestamp-query'}
        with open(f'{self.file_path}.tsq', 'rb') as f:
            data = f.read()
        response = requests.post(self.server.value['base_url'], headers=headers, data=data)
        if response.status_code == 200:
            with open(f'{self.file_path}.tsr', 'wb') as f:
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
# View the timestamp request
openssl ts -query -in {self.file_path}.tsq -text
# View the timestamp reply
openssl ts -reply -in {self.file_path}.tsr -text
# Verify the timestamp
openssl ts -verify -in {self.file_path}.tsr -queryfile {self.file_path}.tsq -CAfile {self.ca} -untrusted {self.tsa}
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


if __name__ == '__main__':
    # f = FileTimestamper('/Users/esther/Downloads/android-chrome-512x512.png')
    # f.timestamp()
    # print(f.verification_commands())
    bt = BatchFileTimestamper('/Users/esther/Downloads')
    bt.timestamp_all()
