import reflex as rx
from typing import Literal, TypedDict
import asyncio

ExportFormat = Literal["mp4", "mov", "avi"]
ExportQuality = Literal["low", "medium", "high"]
ExportResolution = Literal["480p", "720p", "1080p", "source"]


class ExportState(rx.State):
    show_export_modal: bool = False
    export_format: ExportFormat = "mp4"
    export_quality: ExportQuality = "medium"
    export_resolution: ExportResolution = "source"
    is_exporting: bool = False
    export_progress: int = 0
    export_message: str = ""
    exported_video_url: str = ""
    cancel_export_flag: bool = False

    @rx.event
    def toggle_export_modal(self):
        self.show_export_modal = not self.show_export_modal

    @rx.event
    def set_export_format(self, format: ExportFormat):
        self.export_format = format

    @rx.event
    def set_export_quality(self, quality: ExportQuality):
        self.export_quality = quality

    @rx.event
    def set_export_resolution(self, resolution: ExportResolution):
        self.export_resolution = resolution

    @rx.event
    def cancel_export(self):
        self.cancel_export_flag = True

    @rx.event(background=True)
    async def start_export(self, video_file_name: str):
        async with self:
            self.is_exporting = True
            self.export_progress = 0
            self.exported_video_url = ""
            self.cancel_export_flag = False
            self.export_message = "Preparing to export..."
        for i in range(101):
            async with self:
                if self.cancel_export_flag:
                    self.is_exporting = False
                    self.export_message = "Export cancelled."
                    self.export_progress = 0
                    return
                self.export_progress = i
                self.export_message = f"Exporting... {i}%"
                if i == 50:
                    self.export_message = "Applying visualizations..."
            await asyncio.sleep(0.1)
        async with self:
            self.is_exporting = False
            self.export_message = "Export complete!"
            self.exported_video_url = video_file_name

    @rx.event
    def clear_export(self):
        self.exported_video_url = ""
        self.is_exporting = False
        self.export_progress = 0
        self.export_message = ""