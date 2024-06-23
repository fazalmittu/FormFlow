import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import time
from openai import OpenAI
import os
from dotenv import load_dotenv

from utils.gpt_prompt import CRITIQUE_SYSTEM_MESSAGE
from video_processing.process import process_video

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

smaller_ref = process_video("data/reference_video.mp4", "frames/reference")
print(len(smaller_ref), "frames read from reference video.")

smaller_user = process_video("data/freethrow.mp4", "frames/user")
print(len(smaller_user), "frames read from uploaded video.")

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
            *map(lambda x: {"image": x, "resize": 768}, smaller_ref),
            *map(lambda x: {"image": x, "resize": 768}, smaller_user),
        ],
    } 
]
params = {
    "model": "gpt-4o",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 2000,
}

if __name__ == "__main__":  
    result = client.chat.completions.create(**params)
    print(result.choices[0].message.content)
