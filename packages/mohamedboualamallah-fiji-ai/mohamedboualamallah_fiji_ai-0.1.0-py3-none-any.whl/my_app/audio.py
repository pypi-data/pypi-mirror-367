from scipy.io.wavfile import write
import sounddevice as sd
import numpy as np
import webrtcvad
import queue
import os
from gradio_client import Client, handle_file
sample_rate = 16000
frame_duration = 30  # ms
frame_size = int(sample_rate * frame_duration / 1000)
vad = webrtcvad.Vad(2)  # 0-3 (3 = most aggressive)
silence_limit = 1.5  # seconds

audio_queue = queue.Queue()
frames = []

def callback(indata, frames_count, time_info, status):
    audio_queue.put(bytes(indata))

def record_until_silence(filename="command.wav"):
    global frames
    frames = []  # Clear previous frames to start fresh

    if os.path.exists(filename):
         os.remove(filename)

    print("🎤 Speak now...")

    with sd.RawInputStream(samplerate=sample_rate, blocksize=frame_size,
                           dtype='int16', channels=1, callback=callback):
        num_silent = 0
        silence_frames = int(silence_limit * 1000 / frame_duration)
        try:
            while True:
                frame = audio_queue.get()
                is_speech = vad.is_speech(frame, sample_rate)
                frames.append(frame)

                if not is_speech:
                    num_silent += 1
                else:
                    num_silent = 0

                if num_silent > silence_frames:
                    break

        except KeyboardInterrupt:
            print("\n⛔️ Interrupted manually.")

    audio_bytes = b''.join(frames)
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
    write(filename, sample_rate, audio_np)
    print(f"✅ Recording saved as {filename}")
    return audio_np, sample_rate

def texttospeech(text):

    client = Client("NihalGazi/Text-To-Speech-Unlimited")
    result = client.predict(
            prompt=text,
            voice="coral",
            emotion="Expressive, Friendly, Conversational.",
            use_random_seed=True,
            specific_seed=12345,
            api_name="/text_to_speech_app"
    )
    return result[0]
    