from audio2face_api.A2F import Audio2FaceDirect
import os
import logging

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


def test_direct_api():

    # ? Default Scene
    scene_path = os.path.abspath("./assets/mark_solved.usd")

    # ? Default API URL
    API_URL = "http://localhost:8011"

    FPS = 30

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

    # Example
    a2f.export_blendshapes(
        audio_name="canada.wav", output_dir="./output", output_name="canada"
    )


test_direct_api()
