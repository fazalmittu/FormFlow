from flask import render_template, request, session
import json
from critic.gptv import client

def display_initial_analysis(video_path):
    critique_result = session.get('critique_result', {})
    overall_critique = critique_result.get('overall_critique', '')
    score = get_score_from_gpt(overall_critique)
    return render_template('summary.html', overall_critique=overall_critique, score=score, video_path=video_path)

def get_score_from_gpt(overall_critique):
    prompt = f"Given the following critique of a basketball shot: '{overall_critique}', rate the shot form on a scale from 1 to 10."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=50
    )
    score = response.choices[0].message.content.strip()
    return score
