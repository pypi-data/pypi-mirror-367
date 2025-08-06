from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from remotivelabs.broker._generated import recordingsession_api_pb2 as recordingsession__api__pb2
from remotivelabs.broker.client import BrokerClient

_logger = logging.getLogger(__name__)


def sha256(path: Path) -> str:
    with open(path, "rb") as f:
        b = f.read()
    return hashlib.sha256(b).hexdigest()


class FileType(Enum):
    FILE_TYPE_UNKNOWN = 0
    FILE_TYPE_FOLDER = 1
    FILE_TYPE_VIDEO = 2
    FILE_TYPE_AUDIO = 3
    FILE_TYPE_IMAGE = 4
    FILE_TYPE_RECORDING = 5
    FILE_TYPE_RECORDING_SESSION = 6
    FILE_TYPE_RECORDING_MAPPING = 7
    FILE_TYPE_PLATFORM = 8
    FILE_TYPE_INSTANCE = 9
    FILE_TYPE_SIGNAL_DATABASE = 10


@dataclass
class RecordingFile:
    path: str
    type: FileType
    created_time: int
    modified_time: int
    size: int

    @classmethod
    def from_grpc(cls, file: recordingsession__api__pb2.File) -> RecordingFile:
        return cls(
            path=file.path,
            type=FileType(file.type),
            created_time=file.createdTime,
            modified_time=file.modifiedTime,
            size=file.size,
        )


class AsyncBrokerRecordingSessionClient(BrokerClient):
    """
    TODO: We probably dont want to inherit from BrokerClient, but rather use composition to hide functionality not relevant for recording
    session operations. However, this will do for now.
    """

    async def __aenter__(self) -> AsyncBrokerRecordingSessionClient:
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await super().__aexit__(exc_type, exc_value, traceback)

    async def list_recording_files(self, path: str | None = None) -> list[RecordingFile]:
        """
        List recording files in a directory.

        Args:
            path: Optional path to the subdirectory containing the recording files.
        """
        res = await self._recording_session_service.ListRecordingFiles(recordingsession__api__pb2.FileListingRequest(path=path))
        return [RecordingFile.from_grpc(file) for file in res.files]
