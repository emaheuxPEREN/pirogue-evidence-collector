import hashlib
import os
import glob
import mimetypes
import json
from datetime import datetime, timezone
from pathlib import Path


class MetadataExporter:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.metadata = {}
        self.tz = datetime.now(timezone.utc).astimezone().tzinfo

    def resolve_timestamp(self, timestamp: float):
        return datetime.fromtimestamp(timestamp, self.tz).isoformat()

    def add_extra_metadata(self, metadata: dict):
        self.metadata.update(metadata)

    def get_file_checksums(self):
        md5_hash = hashlib.md5()
        sha1_hash = hashlib.sha1()
        sha256_hash = hashlib.sha256()
        sha512_hash = hashlib.sha512()
        with open(self.input_file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
                sha1_hash.update(chunk)
                sha256_hash.update(chunk)
                sha512_hash.update(chunk)
        return {
            'md5': md5_hash.hexdigest(),
            'sha1': sha1_hash.hexdigest(),
            'sha256': sha256_hash.hexdigest(),
            'sha512': sha512_hash.hexdigest()
        }

    def extract(self):
        self.metadata = {
            'filename': Path(self.input_file).name,
            'size': os.path.getsize(self.input_file),
            'extraction_timestamp': datetime.now(self.tz).timestamp(),
            'extraction_date': datetime.now(self.tz).isoformat(),
            'resolved_type': mimetypes.guess_type(self.input_file)[0] or 'application/octet-stream'
        }
        self.metadata.update(self.get_file_checksums())

    def export(self):
        if os.path.exists(self.input_file + '.metadata.json'):
            with open(self.input_file + '.metadata.json') as f:
                existing_metadata = json.load(f)
            self.metadata.update(existing_metadata)
        with open(self.input_file + '.metadata.json', 'w') as f:
            json.dump(self.metadata, f)


class BatchExporter:
    def __init__(self, input_folder: str, extra_metadata: dict = None):
        self.input_folder = input_folder
        self.extra_metadata = extra_metadata

    def export(self):
        for f in glob.glob(self.input_folder + '/*', recursive=False):
            if not os.path.isfile(f):
                continue
            if f.endswith('.metadata.json'):
                continue
            me = MetadataExporter(f)
            me.extract()
            if self.extra_metadata:
                me.add_extra_metadata(self.extra_metadata)
            me.export()


if __name__ == '__main__':
    import glob
    for f in glob.glob('/pirogue_utils/drop_server/*'):
        if not os.path.isfile(f):
            continue
        if f.endswith('.metadata.json'):
            continue
        me = MetadataExporter(f)
        me.extract()
        me.export()
        print(me.metadata)
    # me = MetadataExporter('/Users/esther/Code/pts/pirogue-file-drop/pirogue_file_drop/IMG_1921.png')
    # me.extract()
    # print(me.metadata)

