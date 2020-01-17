
"""
Creates ultrasound based on string seed
"""

import os
import hashlib
import wave
import base64

def noise_generator(seed):
    """
    Creates ultrasound based on string seed.
    Base64-encodes the seed to use as filename.
    Returns the filenmae as string.
    """
    cwd = os.getcwd()
    hash_object = hashlib.sha512(seed.encode())
    hex_dig = hash_object.hexdigest()

    infiles = []

    for i in range(1, len(hex_dig)):
        infiles.append('{}/source_audio/{}.wav'.format(cwd, hex_dig[i]))
    ultrasound_filename = base64.urlsafe_b64encode(seed.encode('utf-8')).decode('utf-8')
    outfile = '{}/output_audio/{}.wav'.format(cwd, ultrasound_filename)

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
    return ultrasound_filename
