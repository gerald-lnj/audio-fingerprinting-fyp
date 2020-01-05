
"""
Creates ultrasound based on string seed
"""

import os
import hashlib
import wave

def noise_generator(seed):
    """
    Creates ultrasound based on string seed
    """
    cwd = os.getcwd()
    hash_object = hashlib.sha512(seed.encode())
    hex_dig = hash_object.hexdigest()

    infiles = []

    for i in range(1, len(hex_dig)):
        infiles.append('{}/source_audio/{}.wav'.format(cwd, hex_dig[i]))

    outfile = '{}/output_audio/{}.wav'.format(cwd, seed)

    data = []
    for infile in infiles:
        _w = wave.open(infile, 'rb')
        data.append([_w.getparams(), _w.readframes(_w.getnframes())])
        _w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for _, frames in data:
        output.writeframes(frames)
    output.close()