'''
'''

from app import app, mongo
from scipy.io import wavfile
import audio_analysis, audio_hashing

users_collection = mongo.db.users
videos_collection = mongo.db.videos  # holds reference to user
ultrasound_collection = mongo.db.ultrasound  # holds reference to video
fingerprints_collection = mongo.db.fingerprints # holds reference to ultrasound (in couples)

# TODO: Change to filename
def match(ultrasound_filepath):
    _, data = wavfile.read(ultrasound_filepath)
    peaks = audio_analysis.analyse(data)
    fingerprints = audio_hashing.hasher(peaks)
    for fingerprint in fingerprints:
        address = fingerprint['address']
        absolute_time = fingerprint['absolute_time']
        print(fingerprints_collection.find_one({'address': address}))

match()