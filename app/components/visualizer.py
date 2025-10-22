import reflex as rx
from app.states.audio_state import AudioState


def waveform_chart() -> rx.Component:
    return rx.recharts.area_chart(
        rx.recharts.area(
            data_key="amplitude",
            type_="natural",
            stroke=AudioState.visualization_color,
            fill=AudioState.visualization_color,
            fill_opacity=0.3,
            dot=False,
        ),
        rx.recharts.x_axis(data_key="time", hide=True),
        rx.recharts.y_axis(domain=[-1, 1], hide=True),
        data=AudioState.waveform_data,
        height=120,
        width="100%",
    )


def spectrum_chart() -> rx.Component:
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="magnitude", fill=AudioState.visualization_color, background=False
        ),
        rx.recharts.x_axis(data_key="frequency", hide=True),
        rx.recharts.y_axis(domain=[0, 1], hide=True),
        data=AudioState.spectrum_data,
        height=120,
        width="100%",
        bar_gap=2,
    )


def visualization_preview() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Visualization Preview",
            class_name="text-lg font-semibold text-gray-800 mb-4",
        ),
        rx.cond(
            AudioState.is_processing_audio,
            rx.el.div(
                rx.spinner(class_name="text-[#6200EA]"),
                rx.el.p(
                    AudioState.processing_audio_message,
                    class_name="text-sm text-gray-600 ml-4",
                ),
                class_name="flex items-center justify-center h-32",
            ),
            rx.cond(
                AudioState.waveform_data,
                rx.el.div(
                    rx.match(
                        AudioState.visualization_type,
                        ("waveform", waveform_chart()),
                        ("spectrum", spectrum_chart()),
                        (
                            "both",
                            rx.el.div(
                                waveform_chart(),
                                spectrum_chart(),
                                class_name="flex flex-col gap-4",
                            ),
                        ),
                    ),
                    class_name="p-4 bg-gray-50 rounded-lg",
                ),
                rx.el.div(
                    rx.el.p(
                        "Process video to see visualization.",
                        class_name="text-sm text-gray-500",
                    ),
                    class_name="flex items-center justify-center h-32 bg-gray-50 rounded-lg",
                ),
            ),
        ),
        class_name="w-full mt-8 p-6 bg-white rounded-lg shadow-sm hover:shadow-lg transition-shadow duration-300 border border-gray-100",
    )


def viz_controls() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p("Style", class_name="text-sm font-medium text-gray-600 mb-2"),
            rx.el.div(
                rx.el.button(
                    "Waveform",
                    on_click=lambda: AudioState.set_visualization_type("waveform"),
                    class_name=rx.cond(
                        AudioState.visualization_type == "waveform",
                        "bg-[#6200EA] text-white",
                        "bg-gray-200 text-gray-800",
                    )
                    + " px-3 py-1 text-sm rounded-md",
                ),
                rx.el.button(
                    "Spectrum",
                    on_click=lambda: AudioState.set_visualization_type("spectrum"),
                    class_name=rx.cond(
                        AudioState.visualization_type == "spectrum",
                        "bg-[#6200EA] text-white",
                        "bg-gray-200 text-gray-800",
                    )
                    + " px-3 py-1 text-sm rounded-md",
                ),
                rx.el.button(
                    "Both",
                    on_click=lambda: AudioState.set_visualization_type("both"),
                    class_name=rx.cond(
                        AudioState.visualization_type == "both",
                        "bg-[#6200EA] text-white",
                        "bg-gray-200 text-gray-800",
                    )
                    + " px-3 py-1 text-sm rounded-md",
                ),
                class_name="flex gap-2",
            ),
        ),
        rx.el.div(
            rx.el.p("Color", class_name="text-sm font-medium text-gray-600 mb-2"),
            rx.el.input(
                type="color",
                on_change=AudioState.set_visualization_color,
                class_name="w-10 h-10 rounded-md p-1",
                default_value=AudioState.visualization_color,
            ),
        ),
        rx.el.div(
            rx.el.p("Position", class_name="text-sm font-medium text-gray-600 mb-2"),
            rx.el.div(
                rx.el.button(
                    "Bottom",
                    on_click=lambda: AudioState.set_visualization_position("bottom"),
                    class_name=rx.cond(
                        AudioState.visualization_position == "bottom",
                        "bg-[#6200EA] text-white",
                        "bg-gray-200 text-gray-800",
                    )
                    + " px-3 py-1 text-sm rounded-md",
                ),
                rx.el.button(
                    "Top",
                    on_click=lambda: AudioState.set_visualization_position("top"),
                    class_name=rx.cond(
                        AudioState.visualization_position == "top",
                        "bg-[#6200EA] text-white",
                        "bg-gray-200 text-gray-800",
                    )
                    + " px-3 py-1 text-sm rounded-md",
                ),
                rx.el.button(
                    "Overlay",
                    on_click=lambda: AudioState.set_visualization_position("overlay"),
                    class_name=rx.cond(
                        AudioState.visualization_position == "overlay",
                        "bg-[#6200EA] text-white",
                        "bg-gray-200 text-gray-800",
                    )
                    + " px-3 py-1 text-sm rounded-md",
                ),
                class_name="flex gap-2",
            ),
        ),
        class_name="grid grid-cols-3 gap-4 mt-6",
    )