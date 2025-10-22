import reflex as rx
from app.state import State
from app.states.audio_state import AudioState
from app.states.export_state import ExportState
from app.components.visualizer import visualization_preview, viz_controls


def file_info_item(icon: str, label: str, value: rx.Var[str | None]) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-5 w-5 text-gray-500"),
        rx.el.div(
            rx.el.p(label, class_name="text-sm font-medium text-gray-600"),
            rx.el.p(
                rx.cond(value, value, "N/A"),
                class_name="text-sm text-gray-800 font-semibold",
            ),
            class_name="flex-1",
        ),
        class_name="flex items-center gap-4 p-3 bg-gray-50 rounded-lg",
    )


def metadata_display() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Video Metadata", class_name="text-lg font-semibold text-gray-800 mb-4"
        ),
        rx.el.div(
            file_info_item("file-text", "Filename", State.video_metadata["filename"]),
            file_info_item("database", "Size", State.video_metadata["size"]),
            file_info_item("clock", "Duration", State.video_metadata["duration"]),
            file_info_item(
                "maximize", "Resolution", State.video_metadata["resolution"]
            ),
            file_info_item(
                "volume-2", "Audio Info", State.video_metadata["audio_info"]
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
        ),
        class_name="w-full",
    )


def video_player() -> rx.Component:
    return rx.el.div(
        rx.video(
            src=rx.get_upload_url(State.video_file_name),
            playing=True,
            controls=True,
            width="100%",
            height="auto",
            class_name="rounded-lg overflow-hidden shadow-md",
        ),
        class_name="w-full aspect-video bg-black rounded-lg",
    )


def control_panel() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            "Process Video",
            rx.icon("circle_play", class_name="ml-2 h-5 w-5"),
            class_name="px-5 py-3 bg-[#6200EA] text-white rounded-md font-semibold text-sm flex items-center shadow-sm hover:shadow-lg transition-shadow duration-300",
            on_click=AudioState.process_audio(State.video_file_name),
            is_loading=AudioState.is_processing_audio,
            disabled=AudioState.is_processing_audio | ExportState.is_exporting,
        ),
        rx.el.button(
            "Export Video",
            rx.icon("download", class_name="ml-2 h-5 w-5"),
            class_name="px-5 py-3 bg-green-600 text-white rounded-md font-semibold text-sm flex items-center shadow-sm hover:shadow-lg transition-shadow duration-300",
            on_click=ExportState.toggle_export_modal,
            disabled=AudioState.is_processing_audio
            | ExportState.is_exporting
            | (AudioState.waveform_data.length() == 0),
        ),
        rx.el.button(
            "Clear Video",
            rx.icon("trash-2", class_name="ml-2 h-5 w-5"),
            class_name="px-5 py-3 bg-gray-200 text-gray-800 rounded-md font-semibold text-sm flex items-center shadow-sm hover:shadow-lg transition-shadow duration-300",
            on_click=[State.clear_video, AudioState.clear_visualizations],
        ),
        class_name="flex items-center gap-4 mt-6",
    )


def upload_placeholder() -> rx.Component:
    return rx.upload.root(
        rx.el.div(
            rx.icon("cloud_upload", class_name="h-12 w-12 text-[#6200EA] mx-auto"),
            rx.el.h3(
                "Click to upload or drag and drop",
                class_name="mt-4 text-md font-semibold text-gray-700",
            ),
            rx.el.p(
                "Supports: MP4, AVI, MOV, MKV, WEBM",
                class_name="text-xs text-gray-500 mt-1",
            ),
            class_name="text-center",
        ),
        id="upload-main",
        border="2px dashed #D1C4E9",
        padding="2rem",
        class_name="w-full h-full flex items-center justify-center bg-white rounded-lg hover:bg-violet-50 transition-colors duration-300 cursor-pointer",
        on_drop=State.handle_upload(rx.upload_files(upload_id="upload-main")),
    )


def processing_view() -> rx.Component:
    return rx.el.div(
        rx.el.progress(
            value=State.upload_progress,
            max=100,
            class_name="w-full h-2 rounded-full [&::-webkit-progress-bar]:bg-gray-200 [&::-webkit-progress-value]:bg-[#6200EA] [&::-moz-progress-bar]:bg-[#6200EA]",
        ),
        rx.el.p(
            State.processing_message,
            class_name="text-center text-sm font-medium text-gray-600 mt-4",
        ),
        class_name="flex flex-col items-center justify-center w-full p-8",
    )


def error_view() -> rx.Component:
    return rx.el.div(
        rx.icon("flag_triangle_right", class_name="h-12 w-12 text-red-500 mx-auto"),
        rx.el.h3("Upload Failed", class_name="mt-4 text-md font-semibold text-red-700"),
        rx.el.p(
            State.video_metadata["error"],
            class_name="text-xs text-gray-600 mt-1 max-w-sm text-center",
        ),
        rx.el.button(
            "Try Again",
            on_click=[State.clear_video, AudioState.clear_visualizations],
            class_name="mt-6 px-4 py-2 bg-red-500 text-white text-sm font-semibold rounded-md shadow-sm hover:bg-red-600",
        ),
        class_name="text-center flex flex-col items-center justify-center p-8 bg-red-50 rounded-lg",
    )


def export_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(rx.el.div(class_name="hidden")),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                "Export Settings", class_name="text-lg font-semibold"
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Format", class_name="text-sm font-medium text-gray-600 mb-2"
                    ),
                    rx.el.div(
                        rx.el.button(
                            "MP4",
                            on_click=lambda: ExportState.set_export_format("mp4"),
                            class_name=rx.cond(
                                ExportState.export_format == "mp4",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        rx.el.button(
                            "MOV",
                            on_click=lambda: ExportState.set_export_format("mov"),
                            class_name=rx.cond(
                                ExportState.export_format == "mov",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        rx.el.button(
                            "AVI",
                            on_click=lambda: ExportState.set_export_format("avi"),
                            class_name=rx.cond(
                                ExportState.export_format == "avi",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        class_name="flex gap-2",
                    ),
                ),
                rx.el.div(
                    rx.el.p(
                        "Quality", class_name="text-sm font-medium text-gray-600 mb-2"
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Low",
                            on_click=lambda: ExportState.set_export_quality("low"),
                            class_name=rx.cond(
                                ExportState.export_quality == "low",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        rx.el.button(
                            "Medium",
                            on_click=lambda: ExportState.set_export_quality("medium"),
                            class_name=rx.cond(
                                ExportState.export_quality == "medium",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        rx.el.button(
                            "High",
                            on_click=lambda: ExportState.set_export_quality("high"),
                            class_name=rx.cond(
                                ExportState.export_quality == "high",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        class_name="flex gap-2",
                    ),
                ),
                rx.el.div(
                    rx.el.p(
                        "Resolution",
                        class_name="text-sm font-medium text-gray-600 mb-2",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "480p",
                            on_click=lambda: ExportState.set_export_resolution("480p"),
                            class_name=rx.cond(
                                ExportState.export_resolution == "480p",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        rx.el.button(
                            "720p",
                            on_click=lambda: ExportState.set_export_resolution("720p"),
                            class_name=rx.cond(
                                ExportState.export_resolution == "720p",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        rx.el.button(
                            "1080p",
                            on_click=lambda: ExportState.set_export_resolution("1080p"),
                            class_name=rx.cond(
                                ExportState.export_resolution == "1080p",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        rx.el.button(
                            "Source",
                            on_click=lambda: ExportState.set_export_resolution(
                                "source"
                            ),
                            class_name=rx.cond(
                                ExportState.export_resolution == "source",
                                "bg-[#6200EA] text-white",
                                "bg-gray-200 text-gray-800",
                            )
                            + " px-3 py-1 text-sm rounded-md",
                        ),
                        class_name="flex gap-2 flex-wrap",
                    ),
                ),
                class_name="grid grid-cols-1 gap-4 mt-4",
            ),
            rx.el.div(
                rx.cond(
                    ExportState.is_exporting,
                    rx.el.div(
                        rx.el.progress(
                            value=ExportState.export_progress,
                            max=100,
                            class_name="w-full h-2 rounded-full [&::-webkit-progress-bar]:bg-gray-200 [&::-webkit-progress-value]:bg-[#6200EA] [&::-moz-progress-bar]:bg-[#6200EA]",
                        ),
                        rx.el.p(
                            ExportState.export_message,
                            class_name="text-sm text-gray-600 mt-2 text-center",
                        ),
                        rx.el.button(
                            "Cancel",
                            on_click=ExportState.cancel_export,
                            class_name="w-full mt-2 px-4 py-2 bg-red-500 text-white text-sm font-semibold rounded-md shadow-sm hover:bg-red-600",
                        ),
                        class_name="w-full",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Start Export",
                            on_click=[ExportState.start_export(State.video_file_name)],
                            class_name="w-full px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-md shadow-sm hover:bg-green-700",
                        ),
                        class_name="w-full",
                    ),
                ),
                class_name="mt-6 flex justify-end gap-4",
            ),
            rx.radix.primitives.dialog.close(
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    variant="soft",
                    color_scheme="gray",
                    class_name="absolute top-2 right-2 rounded-full",
                )
            ),
            style={"width": "450px"},
        ),
        open=ExportState.show_export_modal,
        on_open_change=ExportState.set_show_export_modal,
    )


def export_preview() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Exported Video", class_name="text-lg font-semibold text-gray-800 mb-4"
        ),
        rx.video(
            src=rx.get_upload_url(ExportState.exported_video_url),
            playing=False,
            controls=True,
            width="100%",
            height="auto",
            class_name="rounded-lg overflow-hidden shadow-md",
        ),
        rx.el.a(
            "Download Video",
            href=rx.get_upload_url(ExportState.exported_video_url),
            download=True,
            class_name="mt-4 inline-block px-5 py-3 bg-green-600 text-white rounded-md font-semibold text-sm text-center w-full hover:bg-green-700 transition-colors",
        ),
        class_name="w-full mt-8 p-6 bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow duration-300 border border-gray-100",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.icon("film", class_name="h-8 w-8 text-[#6200EA]"),
                rx.el.h1(
                    "Audio Visualizer", class_name="text-2xl font-bold text-gray-800"
                ),
                class_name="flex items-center gap-3 p-4 border-b border-gray-200",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.match(
                            State.is_uploading,
                            (True, processing_view()),
                            (
                                False,
                                rx.cond(
                                    State.show_processing_error,
                                    error_view(),
                                    rx.cond(
                                        State.video_metadata,
                                        video_player(),
                                        upload_placeholder(),
                                    ),
                                ),
                            ),
                        ),
                        class_name="w-full aspect-video flex items-center justify-center bg-gray-100 rounded-lg shadow-inner",
                    ),
                    rx.cond(
                        State.video_metadata & ~State.show_processing_error,
                        rx.el.div(
                            metadata_display(),
                            control_panel(),
                            viz_controls(),
                            class_name="mt-8 p-6 bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow duration-300 border border-gray-100",
                        ),
                        None,
                    ),
                    rx.cond(
                        State.video_metadata & ~State.show_processing_error,
                        visualization_preview(),
                        None,
                    ),
                    export_modal(),
                    rx.cond(
                        ExportState.exported_video_url != "", export_preview(), None
                    ),
                    class_name="flex-1 min-w-0",
                ),
                class_name="p-4 md:p-8 flex flex-col gap-8",
            ),
            class_name="w-full max-w-4xl mx-auto bg-white/80 backdrop-blur-sm shadow-xl rounded-xl overflow-hidden my-8 border border-gray-200",
        ),
        class_name="font-['JetBrains_Mono'] bg-gray-50 min-h-screen flex items-center justify-center",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)