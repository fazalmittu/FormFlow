import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import time
from openai import OpenAI
import os
from dotenv import load_dotenv

from utils.gpt_prompt import CRITIQUE_SYSTEM_MESSAGE
# import requests

load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

reference_video = cv2.VideoCapture("data/reference_video.mp4")

base64Frames = []
while reference_video.isOpened():
    success, frame = reference_video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

smaller_ref = [frame[1] for frame in enumerate(base64Frames) if frame[0] % 3 == 0]

reference_video.release()
print(len(smaller_ref), "frames read.")

uploaded_video = cv2.VideoCapture("data/freethrow.mp4")

base64Frames2 = []
while uploaded_video.isOpened():
    success, frame = uploaded_video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames2.append(base64.b64encode(buffer).decode("utf-8"))

smaller_user = [frame[1] for frame in enumerate(base64Frames2) if frame[0] % 3 == 0]

uploaded_video.release()
print(len(smaller_user), "frames read.")


PROMPT_MESSAGES = [
    {
        "role": "system",
        "content": [
            CRITIQUE_SYSTEM_MESSAGE
        ]
    },
    {
        "role": "user",
        "content": [
            CRITIQUE_SYSTEM_MESSAGE,
            *map(lambda x: {"image": x, "resize": 350}, smaller_ref),
            *map(lambda x: {"image": x, "resize": 350}, smaller_user),
        ],

    } 
]
params = {
    "model": "gpt-4o",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 2000,
}

result = client.chat.completions.create(**params)
print(result.choices[0].message.content)