import whisper

model = None


def transcribe_video(video_path):
    global model

    if model is None:
        model = whisper.load_model("base")

    result = model.transcribe(
        str(video_path),
        fp16=False
    )

    return result["text"]