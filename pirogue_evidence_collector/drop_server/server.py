import gc
import os
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread

from flask import *
from werkzeug.serving import BaseWSGIServer
from werkzeug.utils import secure_filename
import logging


def create_server(secret_token, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)
    app = Flask(__name__)
    app.logger.setLevel(logging.ERROR)
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    def __check_token(token):
        return str(token) == secret_token

    @app.route('/<token>/')
    def main(token: str):
        if not __check_token(token):
            return ''
        return render_template('index.html', secret_token=secret_token)

    @app.route('/<token>/done')
    def done(token: str):
        if not __check_token(token):
            return ''
        return render_template('done.html', secret_token=secret_token)

    @app.route('/<token>/shutdown', methods=['GET'])
    def shutdown(token: str):
        for obj in gc.get_objects():
            try:
                if isinstance(obj, BaseWSGIServer):
                    obj.shutdown()
                    return "bye"
            except:
                pass
        return "failed"

    @app.route('/<token>/upload', methods=['POST'])
    def upload(token: str):
        if not __check_token(token):
            return ''
        tz = datetime.now(timezone.utc).astimezone().tzinfo
        if request.method == 'POST':
            metadata = json.loads(request.values.get('metadata'))
            files = request.files.getlist('file')
            for file in files:
                file_metadata = metadata.get(file.filename, {})
                filename = secure_filename(file.filename)
                filepath = os.path.join(output_folder, filename)
                file.save(filepath)
                logging.info(f'File saved: {filepath}')
                if file_metadata:
                    file_metadata['modification_date'] = datetime.fromtimestamp(
                        file_metadata.get('modification_timestamp'), tz).isoformat()
                with open(filepath + '.metadata.json', 'w') as f:
                    json.dump(file_metadata, f)
        return redirect(url_for('done', token=token, **request.args))

    return app, shutdown


class DropServer:
    def __init__(self, output_folder, *, host: str = '0.0.0.0', port: int = 8080, debug=False):
        self.secret_token = secrets.token_urlsafe(6)
        self.app, self.shutdown_fnc = create_server(self.secret_token, output_folder)
        self.host = host
        self.port = port
        self.debug = debug
        self.server_thread = Thread(target=self._start_server)
        self.url = f'http://{host}:{port}/{self.secret_token}/'

    def _start_server(self):
        self.app.run(debug=self.debug, host=self.host, port=self.port)

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.shutdown_fnc()
        self.server_thread.join()

