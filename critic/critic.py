import asyncio
from hume import HumeVoiceClient, MicrophoneInterface
from dotenv import load_dotenv
import os

load_dotenv()

HUME_API_KEY = os.getenv("HUME_API_KEY")
print(HUME_API_KEY)

async def main() -> None:
  # Connect and authenticate with Hume
  client = HumeVoiceClient(HUME_API_KEY)

  # Start streaming EVI over your device's microphone and speakers
  async with client.connect() as socket:
      await MicrophoneInterface.start(socket)

asyncio.run(main())