import sys
from video_processor import transcribe_video


if __name__ == "__main__":
    video_path = sys.argv[1]

    transcript = transcribe_video(video_path)

    print(transcript)