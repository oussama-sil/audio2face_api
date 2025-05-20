DEFAULT_A2E_INSTANCE = "/World/audio2face/CoreFullface"

# ? For streaming
DEFAULT_AUDIO_STREAM_PLAYER_INSTANCE = "/World/audio2face/PlayerStreaming"
DEFAULT_AUDIO_STREAM_GRPC_PORT = 50051


"""
The settings for the audio2emotion generation
Available settings:
    "a2f_instance": "/World/audio2face/CoreFullface",                   * Necessary, default to be /World/audio2face/CoreFullface
    "a2e_window_size": 1.4,                 Emotion Detection Range     Sets the size, in seconds, of an audio chunk used to predict a single emotion_auto_detect per keyframe.
    "a2e_stride": 1,                        Keyframe Interval           Sets the number of seconds between adjacent automated keyframes.
    "a2e_emotion_strength": 0.5,            Emotion Strength            Sets the strength of the generated emotions relative to the neutral emotion_auto_detect.
    "a2e_smoothing_kernel_radius": 0,       * WTF?!
    "a2e_smoothing_exp": 0,                 Smoothing(Exp)              Sets the number of neighboring keyframes used for emotion_auto_detect smoothing.
    "a2e_max_emotions": 5,                  Max Emotions                Sets a hard limit on the quantity of emotions that Audio2Emotion will engage at one time. (Emotions are prioritized by their strength.)
    "a2e_contrast": 1,                      Emotion Contrast            Controls the emotion_auto_detect spread - pushing higher and lower values.
    "preferred_emotion": [                  Preferred Emotion           Sets a single emotion_auto_detect as the base emotion_auto_detect for the character animation. The preferred emotion_auto_detect is taken from the current settings in the Emotion widget and is mixed with generated emotions throughout the animation. (is not set indicates whether or not you’ve set a preferred emotion_auto_detect.)
    0
    ],
    "a2e_preferred_emotion_strength": 0,    Strength                    Sets the strength of the preferred emotion_auto_detect. This determines how present this animation will be in the final animation.
    "a2e_streaming_smoothing": 0,           * Only for clients
    "a2e_streaming_update_period": 0,
    "a2e_streaming_transition_time": 0
"""

A2E_DEFAULT_SETTINGS = {
    "a2f_instance": DEFAULT_A2E_INSTANCE,
    "a2e_window_size": 2.0,
    "a2e_stride": 1,
    "a2e_emotion_strength": 0.5,
    "a2e_smoothing_exp": 0.0,
    "a2e_max_emotions": 5,
    "a2e_contrast": 1.0,
    "preferred_emotion": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    "a2e_preferred_emotion_strength": 0.5,
}
