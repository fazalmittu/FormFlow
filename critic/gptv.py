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

def critique_video(user_video_path: str):
    smaller_ref = process_video("data/reference_video.mp4", "static/images/reference")
    print(len(smaller_ref), "frames read from reference video.")

    smaller_user = process_video(user_video_path, "static/images/user")
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

    print('BEFORE RESULT')
    
    result = client.chat.completions.create(**params)
    # replace single quotes with double quotes
    result_content = result.choices[0].message.content.replace("'", '"')
    # replace all new lines with nothing
    result_content = result_content.replace('\n', '')
    print(result_content)
    #replace "    " with nothing
    result_content = result_content.replace('    ', '')
    print(result_content)
    result_content = result_content.replace('   ', '')
    print(result_content)
    result_content = result_content.replace('  ', '')
    print(result_content)
    # replace '```json' with nothing
    result_content = result_content.replace('```json', '')
    print(result_content)

    result_content = result_content.replace('```', '')
    print(result_content)

    # replace "s with 's
    result_content = result_content.replace('"s', "'s")
    print(result_content)

    # replace ,'s with ,\"s
    result_content = result_content.replace(",'s", ',"s')
    print(result_content)

    result_content = result_content.replace("{'s", '{"s')
    print(result_content)

    # replace "t with 't
    result_content = result_content.replace('"t', "'t")
    print(result_content)

    # replace ,'t with ,\"t
    result_content = result_content.replace(",'t", ',"t')
    print(result_content)

    #replace '"' with \"
    result_content = result_content.replace('"', '\"')
    print(result_content)



    print('AFTER RESULT')
    res = json.loads(fr"""{result_content}""")
    print(res)
    print(type(res))
    return res

if __name__ == "__main__":
    user_video_path = "data/freethrow.mp4"  # Example user video path
    response = critique_video(user_video_path)
    print(response)

    # python3 -m critic.gptv
