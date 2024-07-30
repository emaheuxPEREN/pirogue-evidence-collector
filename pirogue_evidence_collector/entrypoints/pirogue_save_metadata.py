from pathlib import Path

from pirogue_evidence_collector.file_handler.metadata import BatchExporter


def main():
    be = BatchExporter(Path('/pirogue_utils/drop_server'))
    be.export()

