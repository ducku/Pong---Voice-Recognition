import parselmouth
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from multiprocessing import Process, Pipe
from threading import Thread

sd.default.samplerate = 48000
sd.default.channels = 1

def record(duration: int) -> None:
    recording = sd.rec(duration * sd.default.samplerate)
    sd.wait()
    write("w.wav", sd.default.samplerate, recording)

def recording_to_amplitude() -> float:
    sound = parselmouth.Sound("w.wav")
    amplitude = sound.to_intensity(minimum_pitch=100.0, time_step=None, subtract_mean=True)
    amplitude_vals = amplitude.selected_array['frequency']
    average = np.nanmean(amplitude_vals)
    return average

def recording_to_pitch() -> float:
    sound = parselmouth.Sound("w.wav")
    pitch = sound.to_pitch(pitch_ceiling=999999, pitch_floor=3)
    pitch_vals = pitch.selected_array['frequency']
    average = np.nanmean(pitch_vals)
    return average

def record_and_return_pitch(duration: int) -> float:
    record(duration)
    return recording_to_pitch()


def _continues_detect(pipe: Pipe, duration: int) -> None:
    while True:
        pitch = record_and_return_pitch(duration)
        pipe.send(pitch)

def continues_detect() -> Pipe:
    p_r, p_w = Pipe(duplex=False)
    Thread(target=_continues_detect, args=(p_w, 1)).start()
    return p_r


def continues_detect_and_print():
    p_r = continues_detect()
    while True:
        pitch = p_r.recv()
        print(pitch)

def main():
    continues_detect_and_print()

if __name__ == "__main__":
    main()