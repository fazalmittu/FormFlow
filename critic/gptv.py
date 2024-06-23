import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import time
from openai import OpenAI
import os
from dotenv import load_dotenv

from utils.gpt_prompt import CRITIQUE_SYSTEM_MESSAGE

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_video(video_path, output_dir, frame_interval=3):
    video = cv2.VideoCapture(video_path)
    base64_frames = []
    frame_count = 0

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            # Add frame number text
            text = f"Frame: {frame_count}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, text, (10, 30), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # Save frame to output directory
            frame_filename = os.path.join(output_dir, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)

            # Encode frame to base64
            _, buffer = cv2.imencode(".jpg", frame)
            base64_frames.append(base64.b64encode(buffer).decode("utf-8"))

        frame_count += 1

    video.release()
    return base64_frames

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
