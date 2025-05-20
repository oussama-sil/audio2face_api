import os
import time
from audio2face_api.A2E_CONFIG import A2E_DEFAULT_SETTINGS
from audio2face_api.A2F_CONFIG import (
    DEFAULT_PLAYER_INSTANCE,
    DEFAULT_SOLVER_INSTANCE,
    DEFAULT_STREAM_LIVELINK,
)
from audio2face_api.http_client import HttpClient
from audio2face_api.A2E import Audio2Emotion, Audio2EmotionDirect, Audio2EmotionStream
import logging
from abc import ABC, abstractmethod

import logging
from typing import override

from audio2face_api.A2E_CONFIG import DEFAULT_AUDIO_STREAM_PLAYER_INSTANCE
from audio2face_api.A2F_CONFIG import (
    DEFAULT_STREAM_LIVELINK,
    LIVELINK_DEFAULT_SETTINGS,
    LIVELINK_LISTENING_INTERFACE,
    LIVELINK_LISTENING_PORT,
    PATH_PING_AUDIO,
)
from audio2face_api.Buffer import Buffer
from audio2face_api.LiveLink import LiveLinkListener
import audio2face_api.grpc.audio2face_pb2 as audio2face_pb2
import audio2face_api.grpc.audio2face_pb2_grpc as audio2face_pb2_grpc
import grpc
import numpy as np
import soundfile


class Audio2Face(ABC):
    def __init__(
        self,
        api_url: str = "http://localhost:8011",
        scene_path: str = None,
        a2e_settings: dict = A2E_DEFAULT_SETTINGS,
        fps: int = 30,
        use_keyframes: bool = False,
        use_global_emotion: bool = False,
        global_emotion: dict = None,
    ):

        # API : Audio2Face Server
        self.is_api_running = False
        self.api_url = api_url

        # Client to handle requests with the server
        self.http_client = HttpClient(api_url)

        if not os.path.isabs(scene_path):
            scene_path = os.path.abspath(scene_path)
        self.scene_path = scene_path
        self.scene_loaded = None

        # Emotion Detection Handler
        self.use_keyframes = use_keyframes
        self.use_global_emotion = use_global_emotion
        self.global_emotion = global_emotion
        self.a2e_settings = a2e_settings
        self.fps = fps

    def init_A2F(self):
        """
        Initializes the A2F API by checking if A2F is running and loading the scene.
        """
        # Check if the API is running and load the scene
        if self.get_api_status():
            payload = {"file_name": self.scene_path}
            res = self.http_client.post("A2F/USD/Load", payload)
            # Load the scene
            self.scene_loaded = res.get("status") == "OK"
            if self.scene_loaded:
                logging.info(
                    f"Audio2Face: Scene {self.scene_path} loaded successfully."
                )
            else:
                logging.error("Audio2Face: Failed to load the scene.")
        else:
            raise ConnectionError(
                "Audio2Face: API is not running. Please check the server status."
            )

    def get_api_status(self):
        """
        Check if the API is running
        """
        return self.http_client.get("status") == "OK"


class Audio2FaceDirect(Audio2Face):

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.audio_root_path = None

        # A2E
        self.a2e = Audio2EmotionDirect(
            a2e_settings=self.a2e_settings,
            http_client=self.http_client,
        )

    def set_audio_root_path(self, dir_path: str = None):
        """
        Set the root path for audio files.
        :param dir_path: The directory path to set as the audio root path.
        """
        # Getting the abs path
        if not os.path.isabs(dir_path):
            dir_path = os.path.abspath(dir_path)

        # Check if the directory exists otherwise create it
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logging.info(f"Audio2FaceDirect: Audio root path {dir_path} created.")

        payload = {"a2f_player": DEFAULT_PLAYER_INSTANCE, "dir_path": dir_path}
        res = self.http_client.post("A2F/Player/SetRootPath", payload)
        logging.debug(f"Audio2FaceDirect: {res}")
        if res.get("status") == "OK":
            self.audio_root_path = dir_path
            logging.info(f"Audio2FaceDirect: Audio root path set to {dir_path}.")
        else:
            logging.error("Audio2FaceDirect: Failed to set audio root path.")
        return res

    def _set_audio(self, audio_name: str = None):
        """
        Set the audio file to be used by A2F player.
        :param audio_name: The name of the audio file.
        :return: JSON response from the server.
        """
        # Check if the audio file exists in root folder
        audio_path = os.path.join(self.audio_root_path, audio_name)
        if not os.path.exists(audio_path):
            raise FileNotFoundError(
                f"Audio2FaceDirect: Audio file {audio_name} not found in {self.audio_root_path}."
            )

        # Check if the audio file is a valid format
        valid_formats = [".wav"]
        if not any(audio_name.endswith(ext) for ext in valid_formats):
            raise ValueError(
                f"Audio2FaceDirect: Invalid audio format. Supported formats are: {', '.join(valid_formats)}."
            )

        # Set the audio file
        payload = {
            "a2f_player": DEFAULT_PLAYER_INSTANCE,
            "file_name": audio_name,
            "time_range": [0, -1],
        }

        res = self.http_client.post("A2F/Player/SetTrack", payload=payload)
        logging.debug(f"Audio2FaceDirect: {res}")
        if res.get("status") == "OK":
            logging.info(f"Audio2FaceDirect: Audio file {audio_name} set successfully.")
        else:
            logging.error("Audio2FaceDirect: Failed to set audio file.")
        return res

    def _export_blendshapes(
        self,
        output_dir: str = None,
        output_name: str = None,
    ):
        """Export Blendshapes to the given directory.
        :param output_dir: The directory to export the blendshapes to.
        :param output_name: The name of the output file.
        :return: JSON response from the server.
        """

        # Check if the output directory exists otherwise create it
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Audio2FaceDirect: Output directory {output_dir} created.")

        # Get Absolute path if not already abs path
        if not os.path.isabs(output_dir):
            output_dir = os.path.abspath(output_dir)

        payload = {
            "solver_node": DEFAULT_SOLVER_INSTANCE,
            "export_directory": output_dir,
            "file_name": output_name,
            "format": "json",
            "batch": False,
            "fps": self.fps,
        }

        res = self.http_client.post("A2F/Exporter/ExportBlendshapes", payload=payload)
        logging.debug(f"Audio2FaceDirect: {res}")
        if res.get("status") == "OK":
            logging.info(
                f"Audio2FaceDirect: Blendshapes exported successfully to {output_dir}."
            )
        else:
            logging.error("Audio2FaceDirect: Failed to export blendshapes.")
        return res

    def export_blendshapes(
        self,
        audio_name: str = None,
        output_dir: str = None,
        output_name: str = None,
    ):
        """Export Blendshapes from the audio file."""

        start_time = time.time()
        # Set the audio file
        self._set_audio(audio_name)

        if self.use_global_emotion:
            # Set Global Emotion
            self.a2e.set_gloabl_emotion(**self.global_emotion)

        # Emotion Detection
        if self.use_keyframes:
            self.a2e.detect_emotion_keys()

        # Blendshapes Export
        self._export_blendshapes(output_dir=output_dir, output_name=output_name)
        end_time = time.time()
        logging.info(
            f"Audio2FaceDirect: Inference completed in {end_time - start_time:.2f} seconds."
        )


class Audio2FaceStream(Audio2Face):

    def __init__(
        self,
        grpc_url,
        chunk_size,
        block_until_playback_is_finished,
        use_livelink,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # gRPC URL
        self.grpc_url = grpc_url

        # Audio Stream params
        self.chunk_size = chunk_size

        # self.sleep_between_chunks = sleep_between_chunks
        self.block_until_playback_is_finished = block_until_playback_is_finished

        # Use LiveLink to receive the generated frames
        self.use_livelink = use_livelink
        self.livelink_listener = None
        self.frames_buffer = None

        # A2E
        self.a2e = Audio2EmotionStream(
            a2e_settings=self.a2e_settings,
            http_client=self.http_client,
        )

    @override
    def init_A2F(self):
        super().init_A2F()

        # Stream an init audio
        data, samplerate = soundfile.read(PATH_PING_AUDIO, dtype="float32")
        self._push_audio_stream(data, samplerate)

        # Starting Livelink Stream to receive frames
        if self.use_livelink:
            logging.info("Audio2FaceStream: Starting LiveLink Stream...")
            # A buffer for frames
            self.frames_buffer = Buffer()
            # Creates a listener to receive the frames
            self.livelink_listener = LiveLinkListener(
                ip=LIVELINK_LISTENING_INTERFACE,
                port=LIVELINK_LISTENING_PORT,
                buffer=self.frames_buffer,
            )
            self.livelink_listener.start()
            # Enable livelink pluging on A2F
            time.sleep(1)  # Wait for the livelink listener to start
            self.enable_stream_livelink(True)

        if self.use_global_emotion:
            # Set Global Emotion
            self.a2e.set_gloabl_emotion(**self.global_emotion)

    def stream_audio(self, audio_data, sample_rate):
        if self.use_livelink:
            logging.info("Audio2FaceStream: Flushing frames buffer...")
            self.frames_buffer.flush()
        audio_length = len(audio_data) / sample_rate  # length in seconds
        self._push_audio_stream(audio_data, sample_rate)
        # retrieve the frames from the buffer
        frames = None
        if self.use_livelink:
            # Sleep to wait until all the frames are received
            time.sleep(audio_length + 1)
            frames = self.frames_buffer.flush()
        return frames

    def _push_audio_stream(self, audio_data, sample_rate):
        """
        This function pushes audio chunks sequentially via PushAudioStreamRequest()
        See grpc folder for details about grpc
        """
        with grpc.insecure_channel(self.grpc_url) as channel:
            logging.debug("Audio2FaceStream: Created gRPC Channel")
            stub = audio2face_pb2_grpc.Audio2FaceStub(channel)

            def make_generator():
                start_marker = audio2face_pb2.PushAudioRequestStart(
                    samplerate=sample_rate,
                    instance_name=DEFAULT_AUDIO_STREAM_PLAYER_INSTANCE,
                    block_until_playback_is_finished=self.block_until_playback_is_finished,
                )
                yield audio2face_pb2.PushAudioStreamRequest(start_marker=start_marker)
                for i in range(len(audio_data) // self.chunk_size + 1):
                    # time.sleep(self.sleep_between_chunks)
                    chunk = audio_data[
                        i * self.chunk_size : i * self.chunk_size + self.chunk_size
                    ]
                    yield audio2face_pb2.PushAudioStreamRequest(
                        audio_data=chunk.astype(np.float32).tobytes()
                    )

            request_generator = make_generator()
            logging.info("Audio2FaceStream: Streaming Audio Data to A2F Instance")
            response = stub.PushAudioStream(request_generator)

            if response.success:
                logging.info("Audio2FaceStream: Audio Streamed Successfully")
            else:
                logging.error(f"Audio2FaceStream: ERROR: {response.message}")
        logging.debug("Audio2FaceStream: Closed gRPC Channel")

    def enable_stream_livelink(self, enable: bool = True):

        payload = {"node_path": DEFAULT_STREAM_LIVELINK, "value": enable}
        res = self.http_client.post(
            "A2F/Exporter/ActivateStreamLivelink", payload=payload
        )
        logging.debug(f"Audio2FaceStream: {res}")
        if res.get("status") == "OK":
            logging.info("Audio2FaceStream: Stream Livelink activated successfully.")
        else:
            logging.error("Audio2FaceStream: Failed to activate Stream Livelink.")
        return res

    def set_livelink_settings(
        self, livelink_settings: dict = LIVELINK_DEFAULT_SETTINGS
    ):
        payload = {"node_path": DEFAULT_STREAM_LIVELINK, "values": livelink_settings}
        res = self.http_client.post(
            "/A2F/Exporter/SetStreamLivelinkSettings", payload=payload
        )
        logging.debug(f"Audio2FaceStream: {res}")
        if res.get("status") == "OK":
            logging.info("Audio2FaceStream: Stream Livelink settings set successfully.")
        else:
            logging.error("Audio2FaceStream: Failed to set Stream Livelink settings.")

    def get_livelink_settings(self):

        # Get the status of LiveLink
        payload = {
            "node_path": DEFAULT_STREAM_LIVELINK,
        }
        res = self.http_client.post(
            "/A2F/Exporter/IsStreamLivelinkConnected", payload=payload
        )
        logging.debug(f"Audio2FaceStream: {res}")
        if res.get("status") == "OK":
            if res.get("result"):
                logging.info("Audio2FaceStream: Stream Livelink is connected.")
            else:
                logging.warning("Audio2FaceStream: Stream Livelink is not connected.")
        else:
            logging.error("Audio2FaceStream: Failed to connect Stream Livelink.")
        state = res.get("result")

        # Get Livelink settings
        payload = {
            "node_path": DEFAULT_STREAM_LIVELINK,
        }
        res = self.http_client.post(
            "/A2F/Exporter/GetStreamLivelinkSettings", payload=payload
        )
        logging.debug(f"Audio2FaceStream: {res}")
        if res.get("status") == "OK":
            logging.info("Audio2FaceStream: Stream Livelink settings retrieved.")
        else:
            logging.error(
                "Audio2FaceStream: Failed to retrieve Stream Livelink settings."
            )
        settings = res.get("result")
        settings["connected"] = state
        return settings

    def end_a2f_connection(self):
        if self.use_livelink:
            self.enable_stream_livelink(False)  # To close the socket
            self.livelink_listener.stop()
            self.livelink_listener.join()
            self.frames_buffer.flush()
            logging.info("Audio2FaceStream: Closed gRPC Channel and stopped listener.")
