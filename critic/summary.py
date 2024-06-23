from flask import render_template, request, session
import json
from critic.gptv import client
from openpose_overlay.overlay import process_image_and_get_elbow_angle

def display_initial_analysis(video_path):
    critique_result = session.get('critique_result', {})
    overall_critique = critique_result.get('overall_critique', '')
    score = float(get_score_from_gpt(overall_critique))
    
    # Get the key frame paths from the critique result
    key_frames = critique_result.get('student_key_frames', [])
    if len(key_frames) >= 4:
        shooting_key_frame = key_frames[3]
        elbow_angle = process_image_and_get_elbow_angle(f'static/images/user/frame_{shooting_key_frame}.jpg')
        if elbow_angle is None:
            elbow_angle = process_image_and_get_elbow_angle(f'static/images/user/frame_{key_frames[0]}.jpg')
        if elbow_angle is not None:
            elbow_angle = f"{elbow_angle:.2f}"
    else:
        elbow_angle = 'N/A'
    
    return render_template('summary.html', overall_critique=overall_critique, score=score, elbow_angle=elbow_angle, video_path=video_path)

def get_score_from_gpt(overall_critique):
    prompt = f"Given the following critique of a basketball shot: '{overall_critique}', rate the shot form on a scale from 1 to 10. Please return ONLY A NUMBER. I AM PARSING THE RESPONSE AS AN INTEGER."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=5
    )
    score = response.choices[0].message.content.strip()
    return score
