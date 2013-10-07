import wave
import struct
from array import array

NOISE_TRESHOLD = 500
CLOSENESS_THRESHOLD = 5

import matplotlib.pyplot as plt

def getSamples(f):
    wf = wave.open(f)

    sampleSize = wf.getsampwidth()

    if wf.getnchannels() != 1 or sampleSize != 2:
        raise Exception("Bad wave file.")
    samples = []


    sample = wf.readframes(1)
    while sample:
        n = struct.unpack("h",sample)[0]
        samples.append(n)
        sample = wf.readframes(1)
    return wf.getframerate(),samples



# this function assumes that we used a sound card to sample, and that the PWM wave will appear continuous due to the low sample rate
def normalizeSamples(s):
    maxS = max(s)
    minS = min(s)

    # check if the pwm is registered as negative or positive peak
    c = lambda x: x > 0
    if abs(minS) > abs(maxS):
        c = lambda x: x <0

    # abs(x) > 5000 = ignore noise
    # c = check for signal
    new_s =  [1 if (abs(x) > NOISE_TRESHOLD ) and c(x) else 0 for x in s]

    # remove leading zeros
    while new_s[0] == 0:
        del new_s[0]
    return new_s

# counts the number of samples, and writes the script of counts.
# e.g [0,0,0,1,1,1,0,1,11,0] -> [3,1,1,1,2,1]
def convertSamplesToStreches(normalizedSamples):
    streches = []
    cur = normalizedSamples[0]
    counter = 1
    for i in normalizedSamples[1:]:
        if i == cur:
            counter += 1
        else:
            streches.append(counter)
            cur = i
            counter = 1
    streches.append(counter)
    return streches

def samplesTo10USec(x, rate):
   return (x*1000*100/rate)


def getCloseMatch(value, data):
    for v in data:
        if abs(v-value) < 5:
            return v

    data.add(value)
    return value

# return pairs, which insignificat differences are removed.
def getNormalizedPairs(streches):
    # normalize
    on_st = streches[::2]
    off_st = streches[1::2]

    # the last off value doesn't really mean anything...
    off_st[-1] = 0

    on_values = set()
    off_values = set()

    pairs = []

    for on,off in zip(on_st, off_st):
        on = getCloseMatch(on, on_values)
        off = getCloseMatch(off, off_values)
        pairs.append((on, off))
    return pairs


chunk = 1024
CHANNELS = 1
RATE = 44100

def record(seconds):
    import pyaudio
    FORMAT = pyaudio.paInt16
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)
    data = ""
    for i in range(0, 44100 / chunk * seconds):
        data += stream.read(chunk)
    return data

# rate, s = getSamples("code.wav")
print "Recording now"
data = record(2)
print "Done recording"
rate, s = RATE, array('h', data)
new_s = normalizeSamples(s)

# new s = 1 when there is pwm. 0 otherwise
# plt.plot(new_s)
# plt.show()

streches = convertSamplesToStreches(new_s)
streches = [samplesTo10USec(x, rate) for x in streches]

pairs = getNormalizedPairs(streches)
allPairs = list(set(pairs))
indexPairs = [allPairs.index(x) for x in pairs]
print (38000,allPairs, indexPairs)
print pairs