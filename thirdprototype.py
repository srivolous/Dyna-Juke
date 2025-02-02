import numpy as np
import matplotlib.pyplot as plt
import librosa
import sounddevice as sd
import threading
import time
from testingprototype import readserial
import torch
import torchlibrosa as tl


sd.default.device = sd.query_devices(kind='output')['name']  # Use the default output device
sd.default.latency = 'low'  # Reduce latency
sd.default.dtype = 'float32'  # Ensure correct format

print(sd.query_hostapis())  # List available backends
output_device_index = 8  # Replace with your correct WASAPI device index
#sd.default.hostapi = 2 

print("Program has started!")
sig, srone = librosa.load("C:\\Users\\sreer\\Desktop\\tracks\\ats.mp3",sr=48000)
#sig2,srtwo = librosa.load("C:\\Users\\sreer\\Desktop\\tracks\\ats.mp3",sr=None)
print("File loaded!")
print("Shape of file: ", sig.shape)

duration = sig.shape[0] / srone
print("Duration: ", duration, " seconds"," Sample Rate:",srone)

print("Performing stft...")
stftsig = librosa.stft(sig)

print("STFT done.")

mag, phse = librosa.magphase(stftsig)
print("Magnitude and phase done!")

# Decompose the audio into harmony and percussion
harmony, perkuzz = librosa.decompose.hpss(mag)
print("Harmony and percussion decomposed!")

# Inverse STFT for both harmony and percussion
istftharmony = librosa.istft(harmony * phse)
istftperkuzz = librosa.istft(perkuzz * phse)
print("Harmony and percussion ISTFT done!")

# Set up playback parameters
playback_position = 0
sample1rate = srone
play = sig
voc = istftharmony   #original
har = istftperkuzz

voc = sig
har = sig

tog = 0
switchevent = False
switchreq = False
fade_progress = readserial("/dev/ttyUSB0",115200)
#overhaul = readserial("/dev/ttyUSB0",115200)
#if(overhaul == 1):
#    fade_progress = 1.0
#else:
#    fade_progress = 0.0
fade_duration = 0.2
serialoutputlain = 0
fade_progress = 0

def toggle_audio():
    global fade_progress;
    while True:
       fade_progress = readserial("/dev/ttyUSB0",115200)

toggle_thread = threading.Thread(target=toggle_audio,daemon = True)
toggle_thread.start()


# Callback function for audio streaming
def callback(outdata, frames, time, status):
    global playback_position,tog,fade_progress,switchreq,switchevent
    #fade_progression = True
    print("frames: ",frames)
    frames = 1024
    mzic1 = voc[playback_position:playback_position + frames]  # Get the audio slice for plaback
    mzic2 = har[playback_position:playback_position + frames]
    print(f"fadeprogress(Unified) : {fade_progress}, Sample rate : {sample1rate}")
    mzic =(1-fade_progress)*mzic1 + fade_progress*mzic2
    # Ensure the length of mzic is a multiple of 64 for reshaping(code is useless due to the track being restricted to a single channel)
   # if len(mzic) % 64 != 0:
    #    print("is this code working?")
     #   padding_size = 64 - (len(mzic) % 64)
      #  mzic = np.pad(mzic, (0, padding_size), mode="constant")
    # put one more frame in the data
    framesone = len(mzic)
    #mzic = mzic[:framesone].reshape(-1,1)                          COMMENT
    mzic = np.column_stack((mzic, mzic))
   # print("Final shape after reshape: ", mzic.shape)
    # If there are fewer samples than expected, pad with zeros
    if mzic.shape[0] < frames:
        outdata[:mzic.shape[0]] = mzic
        outdata[mzic.shape[0]:].fill(0)
        raise sd.CallbackStop
    # Assign the reshaped data to the output buffer
    outdata[:] = mzic
    playback_position += frames

# Play the audio
try:
    with sd.OutputStream(samplerate=sample1rate, blocksize=1024,channels =2,  callback=callback,latency = 'low',device = output_device_index): #wasnone
        print("Playing Process Begin!, samplerate = ",sample1rate)
        sd.sleep(int(duration * 1000))
        #sd.wait()
except KeyboardInterrupt:
    print("prog exited")
    
