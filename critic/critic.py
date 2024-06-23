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


def main(critique):
    asyncio.run(start_conversation(critique))
