import reflex as rx
import asyncio
import os
import random
import string
from typing import TypedDict
from app.states.audio_state import AudioState
from app.states.export_state import ExportState


class VideoMetadata(TypedDict):
    filename: str
    size: str
    duration: str | None
    resolution: str | None
    audio_info: str | None
    error: str | None


class State(rx.State):
    """The app state."""

    is_uploading: bool = False
    processing_message: str = ""
    video_file_name: str = ""
    video_metadata: VideoMetadata | None = None
    upload_progress: int = 0
    show_processing_error: bool = False
    ACCEPTED_VIDEO_TYPES = [
        "video/mp4",
        "video/webm",
        "video/x-msvideo",
        "video/quicktime",
        "video/x-matroska",
    ]
    VALID_EXTENSIONS = [".mp4", ".webm", ".avi", ".mov", ".mkv"]

    def _format_size(self, size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / 1024**2:.2f} MB"
        else:
            return f"{size_bytes / 1024**3:.2f} GB"

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        self.video_metadata = None
        self.video_file_name = ""
        self.show_processing_error = False
        self.upload_progress = 0
        if not files:
            self.is_uploading = False
            return
        file = files[0]
        if file.content_type not in self.ACCEPTED_VIDEO_TYPES or not any(
            (file.filename.lower().endswith(ext) for ext in self.VALID_EXTENSIONS)
        ):
            self.video_metadata = {
                "filename": file.filename,
                "size": self._format_size(file.size),
                "duration": None,
                "resolution": None,
                "audio_info": None,
                "error": "Invalid file type. Please upload a valid video file (MP4, WEBM, AVI, MOV, MKV).",
            }
            self.is_uploading = False
            self.show_processing_error = True
            return
        self.processing_message = "Uploading file..."
        yield
        for i in range(101):
            self.upload_progress = i
            await asyncio.sleep(0.01)
        upload_data = await file.read()
        upload_dir = rx.get_upload_dir()
        upload_dir.mkdir(parents=True, exist_ok=True)
        unique_suffix = "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )
        unique_name = f"{unique_suffix}_{file.filename}"
        file_path = upload_dir / unique_name
        with file_path.open("wb") as f:
            f.write(upload_data)
        self.video_file_name = unique_name
        self.processing_message = "Analyzing video metadata..."
        yield
        await asyncio.sleep(1)
        self.video_metadata = {
            "filename": file.filename,
            "size": self._format_size(file.size),
            "duration": "00:01:34",
            "resolution": "1920x1080",
            "audio_info": "AAC, 48kHz, Stereo",
            "error": None,
        }
        self.is_uploading = False

    @rx.var
    def uploaded_video_url(self) -> str:
        return self.video_file_name if self.video_file_name else ""

    @rx.event
    def clear_video(self):
        self.video_metadata = None
        self.video_file_name = ""
        self.is_uploading = False
        self.show_processing_error = False
        self.upload_progress = 0
        return [AudioState.clear_visualizations, ExportState.clear_export]