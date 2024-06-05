import cv2
import moviepy.editor as mp
from moviepy.editor import *

def resize_video_with_audio(input_video, output_video, width, height):
    # Open the video file
    cap = cv2.VideoCapture(input_video)

    # Get the video's frame width and height
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec for the output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Get the input video's FPS
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create VideoWriter object for the output video
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # Resize the frame
            resized_frame = cv2.resize(frame, (width, height))
            # Write the resized frame
            out.write(resized_frame)
            # Display the resized frame
            cv2.imshow('Resized Frame', resized_frame)
            key = cv2.waitKey(1)
            
            if key == ord('q'):
                break
            elif key == ord('d'):
                width += 1
                print(width)
            elif key == ord('a') and width > 0:
                width -= 1
                print(width)
            
        else:
            break

    # Release everything when done
    cap.release()
    out.release()
    cv2.destroyAllWindows()


def extract_audio(filepath,out):
    clip = mp.VideoFileClip(filepath)
    clip.audio.write_audiofile(out)


def change_num_channels(filepath="output.wav"):
    sound = AudioSegment.from_wav(filepath)
    sound = sound.set_channels(1)
    sound.export(filepath, format="wav")

def composit(audio_name, video_name, output_name):
    videoclip = VideoFileClip(video_name)
    audioclip = AudioFileClip(audio_name)

    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(output_name)

# Example usage
input_video = 'C:/Users/Alexandr/Downloads/IMG_4580.MP4'
output_video = 'output_video.mp4'
output_audio= 'output_audio.mp3'
result_video = 'result.mp4'

width = 1060
height = 720
resize_video_with_audio(input_video, output_video, width, height)
extract_audio(input_video, output_audio)
composit(output_audio, output_video, result_video)
