# pip install moviepy pydub
import moviepy.editor as mp
#from pydub import AudioSegment

def extract_audio(filepath,out):
    clip = mp.VideoFileClip(filepath)
    clip.audio.write_audiofile(out)

def change_num_channels(filepath="output.wav"):
    sound = AudioSegment.from_wav(filepath)
    sound = sound.set_channels(1)
    sound.export(filepath, format="wav")
    

file_name = '2024.03.27 - Ресторан Джек Лондон'
video_path = 'C:/Users/Alexandr/Downloads/{}.mp4'.format(file_name)
audio_path = 'C:/Users/Alexandr/Downloads/{}.mp3'.format(file_name)

extract_audio(video_path, audio_path)
print('audio is extracted!')
#change_num_channels(audio_path)
#print('chanels are changed!!')

input()

'''
https://riverside.fm/transcription#
'''
