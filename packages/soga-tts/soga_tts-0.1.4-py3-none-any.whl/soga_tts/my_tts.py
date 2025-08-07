import asyncio
import os
import edge_tts


def raw_text_to_speech_tool(text: str) -> str:
    """Generates speech from text using the edge-tts library and saves it to a file.

    Args:
        text: The text to generate speech from.

    Returns:
        A string representing the path to the generated audio file.
    """
    # Create a placeholder file name
    safe_text = "".join(c for c in text if c.isalnum() or c in " _-").rstrip()
    file_name = f"audio_for_{safe_text[:50]}.mp3"
    file_path = os.path.join("/tmp", file_name)

    async def _generate():
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(file_path)

    # Run the async function
    # A new event loop is created for each call to avoid issues with running asyncio in a sync context.
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(_generate())

    return file_path

