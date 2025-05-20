import logging
from audio2face_api.http_client import HttpClient
from abc import ABC, abstractmethod


class Audio2Emotion(ABC):
    """Class to Handle Audio2Emotion (A2E) API requests and responses."""

    def __init__(
        self,
        a2e_settings: dict = None,
        http_client: HttpClient = None,
    ):
        self.a2e_settings = a2e_settings
        self.http_client = http_client

    def detect_emotion_keys(self):
        """
        Detects emotions in the audio file.
        :return: response from the server.
        """
        res = self.http_client.post("A2F/A2E/GenerateKeys", payload=self.a2e_settings)
        logging.debug(f"Audio2Emotion: Emotion detection result: {res}")
        if res.get("status") == "OK":
            logging.info("Audio2Emotion: Emotion detection completed successfully.")
        else:
            logging.error("Audio2Emotion: Failed to detect emotions.")
        return res

    def get_emotion_keys(self):
        """
        Get the detected emotions Key Frames.
        """
        payload = {
            "a2f_instance": self.a2e_settings["a2f_instance"],
            "as_timestamps": True,
        }
        res = self.http_client.post("A2F/A2E/GetKeyData", payload=payload)
        logging.debug(f"Audio2Emotion: Get emotion keys result: {res}")
        if res.get("status") == "OK":
            logging.info("Audio2Emotion: Emotion keys retrieved successfully.")
        else:
            logging.error("Audio2Emotion: Failed to retrieve emotion keys.")

        return res

    def set_gloabl_emotion(
        self,
        amazement: float | None = 0.0,
        anger: float | None = 0.0,
        cheekiness: float | None = 0.0,
        disgust: float | None = 0.0,
        fear: float | None = 0.0,
        grief: float | None = 0.0,
        joy: float | None = 0.0,
        outofbreath: float | None = 0.0,
        pain: float | None = 0.0,
        sadness: float | None = 0.0,
        update_settings: bool = True,
    ):
        """
        Set the global emotion for the character.
        """
        emotion_strength = {}
        emotion_strength["Amazement"] = amazement if amazement is not None else 0.0
        emotion_strength["Anger"] = anger if anger is not None else 0.0
        emotion_strength["Cheekiness"] = cheekiness if cheekiness is not None else 0.0
        emotion_strength["Disgust"] = disgust if disgust is not None else 0.0
        emotion_strength["Fear"] = fear if fear is not None else 0.0
        emotion_strength["Grief"] = grief if grief is not None else 0.0
        emotion_strength["Joy"] = joy if joy is not None else 0.0
        emotion_strength["Outofbreath"] = (
            outofbreath if outofbreath is not None else 0.0
        )
        emotion_strength["Pain"] = pain if pain is not None else 0.0
        emotion_strength["Sadness"] = sadness if sadness is not None else 0.0

        if update_settings:
            self._update_emotion_settings(
                {"preferred_emotion": list(emotion_strength.values())}
            )

        payload = {
            "a2f_instance": self.a2e_settings["a2f_instance"],
            "emotion": list(emotion_strength.values()),
        }
        res = self.http_client.post("A2F/A2E/SetEmotion", payload=payload)
        logging.debug(f"Audio2Emotion: Set global emotion result: {res}")
        if res.get("status") == "OK":
            logging.info("Audio2Emotion: Global emotion set successfully.")
        else:
            logging.error("Audio2Emotion: Failed to set global emotion.")
        return res

    def _update_emotion_settings(self, settings: dict = None):
        """
        Update the emotion settings.
        :param settings: Dictionary of settings to update.
        """
        for key, value in settings.items():
            self.a2e_settings[key] = value

    @abstractmethod
    def set_auto_emotion_detect(self, auto_detect: bool = True):
        """
        Set the auto emotion detection mode.
        :param auto_detect: Boolean to enable or disable auto emotion detection.
        """
        pass


class Audio2EmotionStream(Audio2Emotion):
    def set_auto_emotion_detect(self, auto_detect: bool = True):
        """
        Set the auto emotion detection mode on streaming mode.
        """
        payload = {
            "a2f_instance": self.a2e_settings["a2f_instance"],
            "enable": auto_detect,
        }
        res = self.http_client.post("/A2F/A2E/EnableStreaming", payload=payload)
        logging.debug(f"Audio2EmotionStream: Set auto emotion detection result: {res}")
        if res.get("status") == "OK":
            logging.info(
                "Audio2EmotionStream: Auto emotion detection mode set successfully."
            )
        else:
            logging.error(
                "Audio2EmotionStream: Failed to set auto emotion detection mode."
            )

        return res


class Audio2EmotionDirect(Audio2Emotion):
    def set_auto_emotion_detect(self, auto_detect: bool = True):
        """
        Set the auto emotion detection mode on audio change.
        """
        payload = {
            "a2f_instance": self.a2e_settings["a2f_instance"],
            "enable": auto_detect,
        }
        res = self.http_client.post(
            "/A2F/A2E/EnableAutoGenerateOnTrackChange", payload=payload
        )
        logging.debug(f"Audio2EmotionDirect: Set auto emotion detection result: {res}")
        if res.get("status") == "OK":
            logging.info(
                "Audio2EmotionDirect: Auto emotion detection mode set successfully."
            )
        else:
            logging.error(
                "Audio2EmotionDirect: Failed to set auto emotion detection mode."
            )

        return res
