import edge_tts
import asyncio

async def female_tts(text,output_name="output.mp3"):
    comms = edge_tts.Communicate(text,voice="fa-IR-DilaraNeural",rate="+0%",)
    await comms.save("output.mp3")
async def male_tts(text,output_name="output.mp3"):
    comms = edge_tts.Communicate(text,voice="fa-IR-FaridNeural",rate="+0%",)
    await comms.save("output.mp3")
