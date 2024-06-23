import cv2 
import base64
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

from utils.gpt_prompt import CRITIQUE_SYSTEM_MESSAGE
from video_processing.process import process_video

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def critique_video(user_video_path: str) -> str:
    smaller_ref = process_video("data/reference_video.mp4", "frames/reference")
    print(len(smaller_ref), "frames read from reference video.")

    smaller_user = process_video(user_video_path, "frames/user")
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
        # "response_format": { "type": "json_object" }
    }
    
    result = client.chat.completions.create(**params)
    res = json.loads(result.choices[0].message.content)
    print(res)
    print(type(res))
    return res

if __name__ == "__main__":
    user_video_path = "data/freethrow.mp4"  # Example user video path
    response = critique_video(user_video_path)
    print(response)

    # python3 -m critic.gptv
