import gc
import os
import json
from datetime import datetime, timezone

from flask import *
from werkzeug.serving import BaseWSGIServer
from werkzeug.utils import secure_filename
import logging
from rich.logging import RichHandler


logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)]
)


def create_server(output_folder):
    app = Flask(__name__)
    app.logger.setLevel(logging.ERROR)

    @app.route('/')
    def main():
        return render_template('index.html')

    @app.route('/done')
    def done():
        return render_template('done.html')

    @app.route('/shutdown', methods=['GET'])
    def shutdown():
        for obj in gc.get_objects():
            try:
                if isinstance(obj, BaseWSGIServer):
                    obj.shutdown()
                    return "bye"
            except:
                pass
        return "failed"

    @app.route('/upload', methods=['POST'])
    def upload():
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
        return redirect(url_for('done'))

    return app


class DropServer:
    def __init__(self, output_folder, port=8080):
        self.app = create_server(output_folder)
        self.port = port

    def start(self, debug=False):
        logging.info('Starting server...')
        self.app.run(debug=debug, host='0.0.0.0', port=self.port)


if __name__ == '__main__':
    server = DropServer('/Users/esther/Downloads')
    server.start(debug=True)
    logging.info('Server stopped.')
