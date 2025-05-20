import time
from audio2face_api.A2F import Audio2FaceStream
import os
import logging
import soundfile
import numpy as np
import json

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


def test_stream_api():

    # ? Default Scene
    scene_path = os.path.abspath("./assets/mark_solved_streaming.usd")

    # ? Default API URL
    API_URL = "http://localhost:8011"
    gRPC_URL = "localhost:50051"

    FPS = 30
    CHUNCK_SIZE = 4000

    a2f = Audio2FaceStream(
        grpc_url=gRPC_URL,
        chunk_size=CHUNCK_SIZE,
        block_until_playback_is_finished=False,
        use_livelink=True,  # Set to true to receive the generated frames from Aufio2Face
        api_url=API_URL,
        scene_path=scene_path,
        fps=FPS,
        use_keyframes=False,
        use_global_emotion=True,
        global_emotion={"joy": 0.9, "sadness": 0.1},
    )

    try:
        a2f.init_A2F()

        audio_fpath = "./assets/canada.wav"

        data, samplerate = soundfile.read(audio_fpath, dtype="float32")

        # Only Mono audio is supported
        if len(data.shape) > 1:
            data = np.average(data, axis=1)

        print(
            f"Audio length: {len(data) / samplerate} seconds , {len(data)} timestamps"
        )

        a2f.a2e.set_auto_emotion_detect(auto_detect=False)
        a2f.a2e.set_gloabl_emotion(joy=0.95, amazement=0.05)

        while True:
            # SImulate async call
            time.sleep(1)  # Wait for new audio data
            frames = a2f.stream_audio(data, samplerate)
            # save frames to a json file
            with open("./output/canada_stream.json", "w") as json_file:
                json.dump(frames, json_file, indent=4)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: Stopping the stream...")
        #! Important: Stop the stream before exiting the script
        a2f.end_a2f_connection()


test_stream_api()
