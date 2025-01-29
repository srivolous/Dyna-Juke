import numpy as np
import matplotlib.pyplot as plt
import librosa
import sounddevice as sd
import threading
import time
from testingprototype import readserial

print("Program has started!")
sig, srone = librosa.load("/home/arthur/Desktop/vimstuff/ats.mp3", sr=None)
sig2,srtwo = librosa.load("/home/arthur/Desktop/vimstuff/mgx.mp3",sr=None)
print("File loaded!")
print("Shape of file: ", sig.shape)

duration = sig.shape[0] / srone
print("Duration: ", duration, " seconds"," Sample Rate:" , srone)

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
#voc = librosa.effects.time_stretch(sig,rate = 0.1)
#har = sig
har = istftperkuzz
#plt.plot(voc)
#plt.show()
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
    mzic1 = voc[playback_position:playback_position + frames]  # Get the audio slice for plaback
    mzic2 = har[playback_position:playback_position + frames]


    print(f"fadeprogress(Unified) : {fade_progress}")
    mzic =(1-fade_progress)*mzic1 + fade_progress*mzic2

        
    #mzic output
    #print("mzic initial shape: ", mzic.shape)

    # Ensure the length of mzic is a multiple of 64 for reshaping(code is useless due to the track being restricted to a single channel)
    if len(mzic) % 64 != 0:
        print("is this code working?")
        padding_size = 64 - (len(mzic) % 64)
        mzic = np.pad(mzic, (0, padding_size), mode="constant")

    # put one more frame in the data
    framesone = len(mzic)
    mzic = mzic[:framesone].reshape(-1,1)
   # print("Final shape after reshape: ", mzic.shape)

    # If there are fewer samples than expected, pad with zeros
    if mzic.shape[0] < frames:
        outdata[:mzic.shape[0]] = mzic
        outdata[mzic.shape[0]:].fill(0)
        raise sd.CallbackStop

    mzic1 = mzic1[playback_position:playback_position + frames]  # Get the audio slice for playback
    mzic2 = mzic2[playback_position:playback_position + frames]
    # Assign the reshaped data to the output buffer
    outdata[:] = mzic
    playback_position += frames

# Play the audio
with sd.OutputStream(samplerate=sample1rate, blocksize=None,channels =1,  callback=callback):
    print("Playing Process Begin!")
    sd.sleep(int(duration * 1000))
    #sd.wait()
    
