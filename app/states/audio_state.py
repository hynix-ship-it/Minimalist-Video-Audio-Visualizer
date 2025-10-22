import reflex as rx
import numpy as np
import ffmpeg
import asyncio
import logging
from typing import TypedDict, Literal
from scipy.fft import fft
from app.states.export_state import ExportState


class WaveformPoint(TypedDict):
    time: float
    amplitude: float


class SpectrumPoint(TypedDict):
    frequency: float
    magnitude: float


VisualizationType = Literal["waveform", "spectrum", "both"]
VisualizationPosition = Literal["bottom", "top", "overlay"]


class AudioState(rx.State):
    waveform_data: list[WaveformPoint] = []
    spectrum_data: list[SpectrumPoint] = []
    is_processing_audio: bool = False
    processing_audio_message: str = ""
    visualization_type: VisualizationType = "waveform"
    visualization_color: str = "#6200EA"
    visualization_position: VisualizationPosition = "bottom"

    @rx.event(background=True)
    async def process_audio(self, video_file_name: str):
        async with self:
            if not video_file_name:
                return
            self.is_processing_audio = True
            self.processing_audio_message = "Extracting audio from video..."
        upload_dir = rx.get_upload_dir()
        video_path = upload_dir / video_file_name
        audio_path = upload_dir / f"{video_file_name}.wav"
        try:
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream.audio, audio_path, ac=1, ar="44100", format="wav"
            )
            ffmpeg.run(
                stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
            )
        except ffmpeg.Error as e:
            logging.exception(f"FFmpeg error: {e.stderr.decode()}")
            async with self:
                self.is_processing_audio = False
                self.processing_audio_message = "Failed to extract audio."
            return
        except FileNotFoundError as e:
            logging.exception(
                "FFmpeg not found. Please ensure it is installed and in the system's PATH."
            )
            async with self:
                self.is_processing_audio = False
                self.processing_audio_message = "FFmpeg not found."
            return
        async with self:
            self.processing_audio_message = "Generating waveform..."
        from scipy.io import wavfile

        sample_rate, audio_samples = wavfile.read(audio_path)
        if audio_samples.dtype == np.int16:
            audio_samples = audio_samples.astype(np.float32) / 32767.0
        num_points = 200
        step = len(audio_samples) // num_points
        downsampled = audio_samples[::step][:num_points]
        if np.max(np.abs(downsampled)) > 0:
            downsampled = downsampled / np.max(np.abs(downsampled))
        time_points = np.linspace(0, len(audio_samples) / sample_rate, num_points)
        waveform = [
            {"time": t, "amplitude": a} for t, a in zip(time_points, downsampled)
        ]
        async with self:
            self.waveform_data = waveform
            self.processing_audio_message = "Generating spectrum..."
        await asyncio.sleep(0.5)
        num_bins = 64
        fft_size = 2048
        if len(audio_samples) > fft_size:
            chunk = audio_samples[:fft_size]
        else:
            chunk = audio_samples
        fft_result = fft(chunk)
        n = len(chunk)
        magnitude = np.abs(fft_result[: n // 2])
        freqs = np.fft.fftfreq(n, 1 / sample_rate)[: n // 2]
        bin_edges = np.logspace(np.log10(20), np.log10(sample_rate / 2), num_bins + 1)
        bin_magnitudes = []
        for i in range(num_bins):
            mask = (freqs >= bin_edges[i]) & (freqs < bin_edges[i + 1])
            if np.any(mask):
                bin_magnitudes.append(np.mean(magnitude[mask]))
            else:
                bin_magnitudes.append(0)
        bin_magnitudes = np.array(bin_magnitudes)
        if np.max(bin_magnitudes) > 0:
            bin_magnitudes = bin_magnitudes / np.max(bin_magnitudes)
        spectrum = [
            {"frequency": f, "magnitude": m}
            for f, m in zip(bin_edges[:-1], bin_magnitudes)
        ]
        async with self:
            self.spectrum_data = spectrum
            self.is_processing_audio = False

    @rx.event
    def set_visualization_type(self, viz_type: VisualizationType):
        self.visualization_type = viz_type

    @rx.event
    def set_visualization_color(self, color: str):
        self.visualization_color = color

    @rx.event
    def set_visualization_position(self, position: VisualizationPosition):
        self.visualization_position = position

    @rx.event
    def clear_visualizations(self):
        self.waveform_data = []
        self.spectrum_data = []
        self.is_processing_audio = False
        return ExportState.clear_export