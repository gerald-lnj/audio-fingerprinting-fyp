"""
Creates ultrasound based on string seed
"""

import os
import hashlib
import wave
import base64
from pydub import AudioSegment

CWD = os.getcwd()


def ultrasound_generator(seed):
    """
    Creates ultrasound based on string seed.
    Base64-encodes the seed to use as filename.
    Returns the filenmae as string.
    """

    hash_object = hashlib.sha512(seed.encode())
    hex_dig = hash_object.hexdigest()

    infiles = []
    # TODO:
    # Currently, produces files that are 2.5s long
    # need to change to create files that are 10s long
    for i in range(1, len(hex_dig)):
        infiles.append("{}/source_audio/{}.wav".format(CWD, hex_dig[i]))
    ultrasound_filename = base64.urlsafe_b64encode(seed.encode("utf-8")).decode("utf-8")
    outfile = "{}/output_audio/{}.wav".format(CWD, ultrasound_filename)

    data = []
    for infile in infiles:
        _w = wave.open(infile, "rb")
        data.append([_w.getparams(), _w.readframes(_w.getnframes())])
        _w.close()

    output = wave.open(outfile, "wb")
    output.setparams(data[0][0])
    for _, frames in data:
        output.writeframes(frames)
    output.close()

    return ultrasound_filename


def audio_extractor(extracted_audio_filepath, seed, start, end):
    print(extracted_audio_filepath)
    audio_filename = base64.urlsafe_b64encode(seed.encode("utf-8")).decode("utf-8")
    output_filepath = "{}/output_audio/{}.wav".format(CWD, audio_filename)

    new_audio = AudioSegment.from_wav(extracted_audio_filepath)
    new_audio = new_audio[start * 1000 : end * 1000]
    new_audio.export(output_filepath, format="wav")

    return audio_filename
