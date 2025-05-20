# audio2face_api

**audio2face_api** is a Python package providing an easy-to-use interface to the Headless Mode API of NVIDIA's Audio2Face. It supports two operational modes : **Direct** and **Stream**.

## Features

- Headless control of Audio2Face via HTTP/gRPC APIs
- Export facial blendshapes directly to files
- Stream audio in real-time to Audio2Face with LiveLink support
- Emotion control via global settings or keyframe detection
- JSON export of generated frame data

---

## Installation

```bash
pip install git+https://github.com/oussama-sil/audio2face_api.git
```

## Usage

### 1. Direct Mode

In **Direct Mode** , the audio is processed as a whole, and the resulting blendshapes are exported as JSON files.

#### Example

```python
from audio2face_api import Audio2FaceDirect

a2f = Audio2FaceDirect(
    api_url=API_URL,
    scene_path=scene_path,
    fps=FPS,
    use_keyframes=False,
    use_global_emotion=True,
    global_emotion={"joy": 0.9, "sadness": 0.05},
)

a2f.init_A2F()

# Disable detection of emotion on audio change
a2f.a2e.set_auto_emotion_detect(auto_detect=False)

# Set Global Emotion
a2f.a2e.set_gloabl_emotion(joy=0.9, sadness=0.05)

# Set the audio root path
a2f.set_audio_root_path(dir_path="./assets")

# Export blendshapes
a2f.export_blendshapes(
    audio_name="canada.wav",
    output_dir="./output",
    output_name="canada"
)
```

### 2. Stream Mode

In **Stream Mode** , audio is streamed chunk-by-chunk to Audio2Face, enabling real-time playback and optional capture of generated frames using the LiveLink plugin.

#### Example

```python
from audio2face_api import Audio2FaceStream
import soundfile
import json

a2f = Audio2FaceStream(
    grpc_url=gRPC_URL,
    chunk_size=CHUNCK_SIZE,
    block_until_playback_is_finished=False,
    use_livelink=True,  # Set to true to receive generated frames
    api_url=API_URL,
    scene_path=scene_path,
    fps=FPS,
    use_keyframes=False,
    use_global_emotion=True,
    global_emotion={"joy": 0.9, "sadness": 0.1},
)

a2f.init_A2F()

# Load audio file
data, samplerate = soundfile.read(audio_fpath, dtype="float32")

# Stream and retrieve frames
frames = a2f.stream_audio(data, samplerate)

# Save frames to file
with open("./output/canada_stream.json", "w") as json_file:
    json.dump(frames, json_file, indent=4)

```

## Emotion Control

You can customize the emotional expression of generated faces using:

### Global Emotion

```python
a2f.a2e.set_gloabl_emotion(joy=0.95, amazement=0.05)

```

### Keyframe-Based Emotion Detection

Enable or disable automatic emotion detection from audio:

```python
a2f.a2e.set_auto_emotion_detect(auto_detect=False)

```

## License

MIT License

## Acknowledgements

Some portions of the code in this package are adapted from [SocAIty/py_audio2face](https://github.com/SocAIty/py_audio2face) repository. Many thanks to their contributors for making it publicly available.

## Contributing

Contributions are very welcome! Feel free to open issues, suggest improvements, or submit pull requests to enhance this package.
