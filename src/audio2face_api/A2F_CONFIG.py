import os

# Easy to use for relative paths a cross the project
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_DIR = os.path.join(ROOT_DIR, "../output")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

APP_DATA_DIR = os.getenv("LOCALAPPDATA")

DEFAULT_PLAYER_INSTANCE = "/World/audio2face/Player"
DEFAULT_SOLVER_INSTANCE = "/World/audio2face/BlendshapeSolve"


# For
DEFAULT_AUDIO_STREAM_PLAYER_INSTANCE = "/World/audio2face/PlayerStreaming"
DEFAULT_AUDIO_STREAM_GRPC_PORT = 50051
PATH_PING_AUDIO = "./assets/ping.mp3"

# For LiveLink Streaming
DEFAULT_STREAM_LIVELINK = "/World/audio2face/StreamLivelink"
LIVELINK_LISTENING_INTERFACE = "localhost"
LIVELINK_LISTENING_PORT = 12030
LIVELINK_AUDIO_PORT = 12031

LIVELINK_DEFAULT_SETTINGS = {
    "audio_port": LIVELINK_AUDIO_PORT,
    "enable_audio_stream": False,
    "enable_gaze": True,
    "enable_idle_face": False,
    "enable_idle_head": True,
    "idle_face_multiplier": 1,
    "idle_head_multiplier": 1,
    "idle_motion_fps": 30,
    "livelink_host": LIVELINK_LISTENING_INTERFACE,
    "livelink_port": LIVELINK_LISTENING_PORT,
    "livelink_subject": "Audio2Face",
}
