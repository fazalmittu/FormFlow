import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
# import requests

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

reference_video = cv2.VideoCapture("data/output_video.mp4")

base64Frames = []
while reference_video.isOpened():
    success, frame = reference_video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

reference_video.release()
print(len(base64Frames), "frames read.")

uploaded_video = cv2.VideoCapture("data/output_video.mp4")

base64Frames2 = []
while uploaded_video.isOpened():
    success, frame = uploaded_video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames2.append(base64.b64encode(buffer).decode("utf-8"))

uploaded_video.release()
print(len(base64Frames2), "frames read.")


PROMPT_MESSAGES = [
    {
        "role": "user",
        "content": [
            """
            These are frames from two videos. The first video is a reference video with good technique for basketball shooting form. 
            The second video is my basketball shooting form. Your response must be in json format with three keys. The first key is 
            reference_key_features, which is a list of the 5 most important frames from the first reference video. The second key is upload_key_frames, which also
            has the 5 most important frames from the second reference video, and these frames should be used for comparison to the first 
            reference video key frames. The last key is overall_critique, and this is your overall detailed critique of my basketball shooting form, given
            the reference video and your own knowledge. Be fair in your critique.
            """,
            *map(lambda x: {"image": x, "resize": 768}, base64Frames),
            *map(lambda x: {"image": x, "resize": 768}, base64Frames2),
        ],
    },
]
params = {
    "model": "gpt-4o",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 200,
}

result = client.chat.completions.create(**params)
print(result.choices[0].message.content)