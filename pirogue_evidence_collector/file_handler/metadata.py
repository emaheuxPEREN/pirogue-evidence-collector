import hashlib
import os
import mimetypes
import json
from datetime import datetime, timezone
from pathlib import Path


class MetadataExporter:
    def __init__(self, input_file: Path):
        self.input_file: Path = input_file
        self.metadata: dict = {}
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
        with self.input_file.open('rb') as _f:
            for chunk in iter(lambda: _f.read(4096), b''):
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
            'filename': self.input_file.name,
            'size': os.path.getsize(self.input_file),
            'extraction_timestamp': datetime.now(self.tz).timestamp(),
            'extraction_date': datetime.now(self.tz).isoformat(),
            'resolved_type': mimetypes.guess_type(self.input_file)[0] or 'application/octet-stream'
        }
        self.metadata.update(self.get_file_checksums())

    def export(self):
        if os.path.exists(self.input_file.name + '.metadata.json'):
            with open(self.input_file.name + '.metadata.json') as _f:
                existing_metadata = json.load(_f)
            self.metadata.update(existing_metadata)
        with open(self.input_file.name + '.metadata.json', 'w') as _f:
            json.dump(self.metadata, _f)


class BatchExporter:
    def __init__(self, input_folder: Path, extra_metadata: dict = None):
        self.input_folder: Path = input_folder
        self.extra_metadata: dict = extra_metadata

    def export(self):
        for input_file in self.input_folder.glob('*'):
            if not input_file.is_file():
                continue
            if input_file.name.endswith('.metadata.json'):
                continue
            exporter = MetadataExporter(input_file)
            exporter.extract()
            if self.extra_metadata:
                exporter.add_extra_metadata(self.extra_metadata)
            exporter.export()


if __name__ == '__main__':
    folder_path = Path('/pirogue_utils/drop_server')
    for f in folder_path.glob('*'):
        if not f.is_file():
            continue
        if f.name.endswith('.metadata.json'):
            continue
        me = MetadataExporter(f)
        me.extract()
        me.export()
        print(me.metadata)
    # me = MetadataExporter('/Users/esther/Code/pts/pirogue-file-drop/pirogue_file_drop/IMG_1921.png')
    # me.extract()
    # print(me.metadata)
