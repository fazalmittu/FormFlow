import asyncio
from hume import HumeVoiceClient, MicrophoneInterface
from dotenv import load_dotenv
import os

load_dotenv()
HUME_API_KEY = os.getenv("HUME_API_KEY")

async def main() -> None:
    # Connect and authenticate with Hume
    client = HumeVoiceClient(HUME_API_KEY)

    # Start streaming EVI over your device's microphone and speakers
    async with client.connect() as socket:
        while True:
            response = await MicrophoneInterface.start(socket)
            print("Hume AI Response:", response)
            # Process the response and continue the conversation
            # You can add more logic here to handle the conversation flow

if __name__ == "__main__":
    asyncio.run(main())

    # python3 -m critic.critic
