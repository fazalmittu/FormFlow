import asyncio
from hume import HumeVoiceClient, LanguageModelConfig, MicrophoneInterface, VoiceConfig, VoiceIdentityConfig
from utils.hume_prompt import HUME_BASKETBALL_SHOT_CRITIQUE_PROMPT
from dotenv import load_dotenv
import os
from uuid import uuid4

load_dotenv()
HUME_API_KEY = os.getenv("HUME_API_KEY")

async def start_conversation(critique: str) -> None:
    # Connect and authenticate with Hume
    client = HumeVoiceClient(HUME_API_KEY)

    prompt = HUME_BASKETBALL_SHOT_CRITIQUE_PROMPT + f"\n\n{critique}"

    # Create a new config with the critique information
    config: VoiceConfig = client.create_config(
        name=f"basketball-coach-{uuid4()}",
        prompt=prompt,
        language_model=LanguageModelConfig(
            model_provider="OPEN_AI",
            model_resource="gpt-4o",
            temperature=0.1
        ),
        voice_identity_config=VoiceIdentityConfig(
            name="DACHER"
        )
    )
    print("Created config: ", config.id)

    # Start the conversation agent
    async with client.connect(config_id=config.id) as socket:
        await MicrophoneInterface.start(socket)

        print("Conversation started. Type 'exit' to end the conversation.")
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Ending conversation...")
                break

if __name__ == "__main__":
    critique = """
    Basketball Shot Form Analysis
    Stance and Position

    Feet Position: The player's feet are positioned shoulder-width apart, providing a stable foundation for the shot. The alignment of the toes with the basket is crucial for balance.
    Knees: The knees are bent, demonstrating a good power stance for the jump. This position helps in generating the necessary lift for the shot.
    Hips: The hips are slightly pushed back, ensuring the player's weight is balanced over their feet, contributing to overall stability.
    Upper Body

    Back: The player's back is straight, maintaining a good posture that is essential for an accurate shot.
    Shoulders: Shoulders are squared to the basket, indicating proper alignment, which is critical for shooting accuracy.
    Elbows: The shooting elbow is tucked close to the body and aligned with the knee and basket, forming a straight line which is vital for a consistent shot release.
    Arm and Hand Position

    Shooting Hand: The shooting hand is positioned correctly under the ball, providing control and support. The wrist is cocked back, ready to snap forward for the release.
    Guide Hand: The guide hand is positioned on the side of the ball, ensuring stability without interfering with the shot's trajectory.
    Fingers: The fingers of the shooting hand are spread wide, ensuring a firm grip on the ball, which is essential for control and precision.
    Follow Through

    Wrist: The wrist is flicked forward at the release point, demonstrating a good follow-through, which is crucial for applying the correct spin on the ball.
    Fingers: The fingers point towards the basket post-release, which helps in directing the ball's path and achieving the desired arc.
    Eyes: The player's eyes are focused on the basket, which shows good concentration and helps in aiming accurately.
    Overall Motion

    Smoothness: The shooting motion appears smooth and fluid, without any jerks, indicating good practice and muscle memory.
    Timing: The synchronization between the legs and arms is well-coordinated, showing an efficient and cohesive shooting form.
    Improvements

    Core Engagement: Engaging the core muscles more could enhance overall stability and control during the shot.
    Release Point: Consistently ensuring a high release point and a full wrist snap can improve the shot's arc and consistency.
    Leg Power: Utilizing more power from the legs can help in extending the shooting range and improving shot efficiency.

    """
    asyncio.run(start_conversation(critique))