import ffmpeg
import os
import wave
import contextlib

from pydub import AudioSegment
from pydub.playback import play

filepath = os.path.dirname(os.path.abspath(__file__))

# use ffmpeg to mux files
# https://superuser.com/questions/1092291/merge-many-audio-files-with-specific-positions



# audio1 = ffmpeg.input('{}/audio1.wav'.format(filepath))
# audio2 = ffmpeg.input('{}/audio2.wav'.format(filepath))
# audio3 = ffmpeg.input('{}/audio3.wav'.format(filepath))

audioNameList = [
    '{}/audio1.wav'.format(filepath), 
    '{}/audio2.wav'.format(filepath), 
    '{}/audio3.wav'.format(filepath)
]

audiolist = [AudioSegment.from_wav(i) for i in audioNameList]

audio_out_file = "out_sine.wav"

# create 1 sec of silence audio segment
one_sec_segment = AudioSegment.silent(duration=1000)  #duration in milliseconds

#Add above two audio segments    
final_song = one_sec_segment
for i in audiolist:
    final_song += i + one_sec_segment

#Either save modified audio
final_song.export('{}/{}'.format(filepath, audio_out_file), format="wav")