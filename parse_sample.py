import wave
import struct
import math
from array import array

NOISE_TRESHOLD = 500
CLOSENESS_THRESHOLD = 5

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

def tenUSecTosamples(x, rate):
    return x*rate/1000/100

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


############ generate pi wave file, instead of arduino codes!
def get_basic_wave(f, all_pairs, index_pairs, frequencey=38000):
    framerate = 44100
    wave_list = []
    for i in index_pairs:
        on,off = all_pairs[i]
        on = tenUSecTosamples(on, framerate)
        off = tenUSecTosamples(off, framerate)
        wave_list += sine_wave(on, frequencey/2, framerate) + [0]*off

    wav_file = wave.open(f, "wb")
    nchannels = 2
    sampwidth = 2
    nframes = len(wave_list)*2
    comptype = "NONE"
    compname = "not compressed"

    wav_file.setparams((nchannels, sampwidth, framerate, nframes,
        comptype, compname))

    for s in wave_list:
        # write the audio frames to file
        s = s*((2**15)-1)
        wav_file.writeframes(struct.pack('h', s))
        wav_file.writeframes(struct.pack('h', -s))

    wav_file.close()


def sine_wave(count, frequency=440.0, framerate=44100, amplitude=0.8):
    if amplitude > 1.0:
        amplitude = 1.0
    if amplitude < 0.0:
        amplitude = 0.0
    return [float(amplitude) * math.sin(2.0*math.pi*float(frequency)*(float(i)/float(framerate))) for i in range(count)]

############################################




def main():
    import argparse   # only supported on python 2.7, rest of this script may be used with python 2.6
    parser = argparse.ArgumentParser(description='RC Parsing tool')

    parser.add_argument('--parsefile', dest="wavfile", type=argparse.FileType('rb'), help='Raw signal wave file to parse. leave empty to record live')
    parser.add_argument('--plot',dest="plot", action='store_true', help='Plot the normalized signal - good for debugging. If doesn\'t match with original signal, change threshholds.')
    parser.add_argument('--frequency',dest="freq", type=int, default=38000, help='Create the configuration at a location. does nothing else.')
    parser.add_argument('--outfile',dest="outfile", type=argparse.FileType('wb'), help='Create the configuration at a location. does nothing else.')

    args = parser.parse_args()

    if args.wavfile:
        rate, s = getSamples(args.wavfile)
    else:
        print "Recording now"
        data = record(2)
        print "Done recording"
        rate, s = RATE, array('h', data)

    # convert the samples for a weird wave, to 1 when there is PWM and 0 when there isn't.
    # also trims the signal
    new_s = normalizeSamples(s)

    if args.plot:
        import matplotlib.pyplot as plt
        # new s = 1 when there is pwm. 0 otherwise
        plt.plot(new_s)
        plt.show()

    # convert to streches (pairs of (on samples, off samples)
    streches = convertSamplesToStreches(new_s)
    # convert the streches from size of samples to size of 10 uSecs
    streches = [samplesTo10USec(x, rate) for x in streches]

    # merge similar pairs
    pairs = getNormalizedPairs(streches)
    # encode
    allPairs = list(set(pairs))
    indexPairs = [allPairs.index(x) for x in pairs]

    print (args.freq,allPairs, indexPairs)

    if args.outfile:
        get_basic_wave(args.outfile, allPairs, indexPairs, args.freq)


if __name__ == "__main__":
    main()
