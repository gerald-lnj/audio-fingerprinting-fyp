import cmath
import math
import numpy as np

CHUNK_SIZE = 1024

# # Range : {~300 (unused), 300-440, 440-880, 880-1760, 1760-3400, 3400~}
# # for audible frequency range
# RANGE = [7, 10, 20, 40, 80, 512]

# Range : {20k, 20.1k, 20.2k, 20.3k})
# for ultrasound frequency range
RANGE = [463, 465, 467, 469, 512]

FILTER_WINDOW_SIZE = 40


def analyse(audio):
    """
    returns 2d int array of peaks
    """
    # if wav file is 2 channels
    if len(audio.shape) == 2:
        # take one channel only
        # left_channel = audio[:, 0]
        # right_channel = audio[:, 1]
        audio = audio[:, 0]

    # returns 2d array of complex numbers
    spectrum = fft(audio)
    # returns 2d array of peaks
    peak = find_peak(spectrum)
    return peak


def fft(audio):
    """
    takes in numpy 1d array
    """
    total_size = audio.shape[0]

    amount_possible = total_size // CHUNK_SIZE

    # When turning into frequency domain we'll need complex numbers:
    # Complex[][] results = new Complex[amount_possible][];
    # a list that is to hold lists of complex num, of len amount_possible
    results = []

    # For all the chunks:
    for times in range(amount_possible):
        complex_temp = np.zeros((CHUNK_SIZE), dtype=np.complex)
        for i, _ in enumerate(complex_temp):
            # Put the time domain data into a complex number with imaginary part as 0:
            complex_temp[i] = complex(audio[times * CHUNK_SIZE + i])
        complex_final = hann_window(complex_temp)
        # perform FFT unitary forward transform on complex_final, and append to results
        results.append(np.fft.fft(complex_final, norm="ortho"))

    return results


def find_peak(spectrum):
    """
    takes in 2d array spectrum, and returns peaks
    """
    peak = [[0 for i in range(len(RANGE))] for j in range(len(spectrum))]
    highscores = [[0 for i in range(len(RANGE))] for j in range(len(spectrum))]
    band = 0
    for i, _ in enumerate(spectrum):
        for freq in range(1, CHUNK_SIZE // 2):
            mag = abs(spectrum[i][freq])
            if freq > RANGE[band]:
                band += 1
            if mag > highscores[i][band]:
                highscores[i][band] = mag
                peak[i][band] = freq
    peak_filtered = []

    total_mag = [0 for i in range(((len(peak) - 1) // FILTER_WINDOW_SIZE) + 1)]
    mean_mag = [0 for i in range(((len(peak) - 1) // FILTER_WINDOW_SIZE) + 1)]
    index = 0
    rest_count = 0
    while (index + 1) * FILTER_WINDOW_SIZE <= len(peak):
        for j in range(
            index * FILTER_WINDOW_SIZE, index * FILTER_WINDOW_SIZE + FILTER_WINDOW_SIZE
        ):
            for k, _ in enumerate(peak[j]):
                total_mag[index] += abs(spectrum[j][peak[j][k]])
        index += 1
    for i in range(index * FILTER_WINDOW_SIZE, len(peak)):
        for j in range(len(peak[i])):
            total_mag[index] += abs(spectrum[i][peak[i][j]])
            rest_count += 1
    for i in range(len(mean_mag) - 1):
        mean_mag[i] = total_mag[i] / (FILTER_WINDOW_SIZE * len(peak[0]))
    mean_mag[-1] = total_mag[-1] / rest_count
    for i, _ in enumerate(peak):
        for j, _ in enumerate(peak[i]):
            freq = peak[i][j]
            amp = abs(spectrum[i][freq])
            if peak[i][j] != 0 and amp >= mean_mag[i // FILTER_WINDOW_SIZE]:
                temp = [i, freq, int(amp)]
                peak_filtered.append(temp)
    return peak_filtered


def hann_window(recorded_data):
    """
    reduce unnecessarily performed frequency part of each and every frequency
    formula
    expects numpy array of type complex
    """

    _m = recorded_data.shape[0]
    hann = np.hanning(_m)
    new_recorded_data = np.multiply(recorded_data, hann)

    return new_recorded_data
