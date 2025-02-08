import numpy as np
import matplotlib.pyplot as plt
import librosa
import sounddevice as sd
import threading
import time
#from testingprototype import readserial
from proton import get_gps_data


#For windows, you have to configurte your audio backend, this line will list everything, select WASAPI since it has the least latency
sd.default.device = sd.query_devices(kind='output')['name'] 
sd.default.latency = 'low'  
sd.default.dtype = 'float32'  

print(sd.query_hostapis())  # List available backends
output_device_index = 8  # Replace with your correct WASAPI device index
#sd.default.hostapi = 2 

print("Program has started!")
y,sr = librosa.load("C:\\Users\\sreer\\Desktop\\tracks\\ats.mp3",sr=48000) #sample rate supported by wasapi(for my system)

print("File loaded!")
print("Shape of file: ", y.shape)

duration = y.shape[0] / sr
print("Duration: ", duration, " seconds"," Sample Rate:",sr)

print("Performing stft...")
S_full, phase = librosa.magphase(librosa.stft(y))


S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(2, sr=sr)))

S_filter = np.minimum(S_full, S_filter)

margin_i, margin_v = 2, 10
power = 2

mask_i = librosa.util.softmask(S_filter,
                               margin_i * (S_full - S_filter),
                               power=power)

mask_v = librosa.util.softmask(S_full - S_filter,
                               margin_v * S_filter,
                               power=power)

S_foreground = mask_v * S_full
S_background = mask_i * S_full


y_foreground = librosa.istft(S_foreground * phase)
y_background = librosa.istft(S_background * phase)

istftharmony = y_foreground
istftperkuzz = y_background
print("vocal and bg ISTFT done!")

# Set up playback parameters
playback_position = 0
sample1rate = sr
#play = sig
voc = istftharmony   #original
har = istftperkuzz

#voc = sig
#har = sig

tog = 0
switchevent = False
switchreq = False
fade_progress = get_gps_data()#readserial("COM4",115200)
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
       fade_progress = get_gps_data()

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
    
