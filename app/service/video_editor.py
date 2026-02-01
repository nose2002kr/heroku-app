import os
import tempfile
import time
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from loguru import logger

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

POSITION_MAP = {
    "top-left": ("left", "top"),
    "top-right": ("right", "top"),
    "bottom-left": ("left", "bottom"),
    "bottom-right": ("right", "bottom"),
    "center": ("center", "center")
}

SYMBOL_ASSETS = {
    "Logo": "logo.png"
}


def safe_unlink(filepath: str, retries: int = 3, delay: float = 0.5):
    """Safely delete a file with retries for Windows file locking issues."""
    for i in range(retries):
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
            return
        except PermissionError:
            if i < retries - 1:
                time.sleep(delay)
            else:
                logger.warning(f"Failed to delete temp file: {filepath}")


async def clip_video(
    file_bytes: bytes,
    filename: str,
    start_time: float = None,
    end_time: float = None
) -> bytes:
    """Clip video to specified time range."""
    tmp_in_path = None
    tmp_out_path = None
    clip = None
    clipped = None

    try:
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name

        clip = VideoFileClip(tmp_in_path)

        start = start_time if start_time is not None else 0
        end = end_time if end_time is not None else clip.duration

        clipped = clip.subclip(start, end)

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_out:
            tmp_out_path = tmp_out.name

        clipped.write_videofile(tmp_out_path, codec="libx264", audio_codec="aac", logger=None)

        with open(tmp_out_path, "rb") as f:
            result = f.read()

        return result
    except Exception as e:
        logger.error(f"clip_video error: {e}")
        raise
    finally:
        if clipped:
            try:
                clipped.close()
            except:
                pass
        if clip:
            try:
                clip.close()
            except:
                pass
        if tmp_out_path:
            safe_unlink(tmp_out_path)
        if tmp_in_path:
            safe_unlink(tmp_in_path)


async def add_watermark(
    file_bytes: bytes,
    filename: str,
    watermark_text: str = None,
    watermark_symbol: str = None,
    position: str = "bottom-right"
) -> bytes:
    """Add watermark to video."""
    tmp_in_path = None
    tmp_out_path = None
    clip = None
    watermark = None
    final = None

    try:
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name

        clip = VideoFileClip(tmp_in_path)
        pos = POSITION_MAP.get(position, ("right", "bottom"))

        if watermark_symbol and watermark_symbol in SYMBOL_ASSETS:
            asset_path = os.path.join(ASSETS_DIR, SYMBOL_ASSETS[watermark_symbol])
            if os.path.exists(asset_path):
                watermark = (ImageClip(asset_path)
                           .set_duration(clip.duration)
                           .set_position(pos)
                           .resize(height=50))
            else:
                watermark = (TextClip(watermark_symbol, fontsize=30, color="white")
                           .set_duration(clip.duration)
                           .set_position(pos))
        elif watermark_text:
            watermark = (TextClip(watermark_text, fontsize=30, color="white")
                       .set_duration(clip.duration)
                       .set_position(pos))
        else:
            watermark = (TextClip("Video Editor", fontsize=30, color="white", stroke_color="black", stroke_width=1)
                       .set_duration(clip.duration)
                       .set_position(pos))

        final = CompositeVideoClip([clip, watermark])

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_out:
            tmp_out_path = tmp_out.name

        final.write_videofile(tmp_out_path, codec="libx264", audio_codec="aac", logger=None)

        with open(tmp_out_path, "rb") as f:
            result = f.read()

        return result
    except Exception as e:
        logger.error(f"add_watermark error: {e}")
        raise
    finally:
        if final:
            try:
                final.close()
            except:
                pass
        if watermark:
            try:
                watermark.close()
            except:
                pass
        if clip:
            try:
                clip.close()
            except:
                pass
        if tmp_out_path:
            safe_unlink(tmp_out_path)
        if tmp_in_path:
            safe_unlink(tmp_in_path)


async def convert_to_gif(
    file_bytes: bytes,
    filename: str,
    fps: int = 10,
    width: int = None,
    height: int = None,
    start_time: float = 0,
    duration: float = None
) -> bytes:
    """Convert video to GIF."""
    tmp_in_path = None
    tmp_out_path = None
    clip = None
    resized_clip = None

    try:
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name

        clip = VideoFileClip(tmp_in_path)

        end_time = start_time + duration if duration else clip.duration
        clip = clip.subclip(start_time, min(end_time, clip.duration))

        if width or height:
            if width and height:
                resized_clip = clip.resize((width, height))
            elif width:
                resized_clip = clip.resize(width=width)
            else:
                resized_clip = clip.resize(height=height)
            clip = resized_clip

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as tmp_out:
            tmp_out_path = tmp_out.name

        clip.write_gif(tmp_out_path, fps=fps, logger=None)

        with open(tmp_out_path, "rb") as f:
            result = f.read()

        return result
    except Exception as e:
        logger.error(f"convert_to_gif error: {e}")
        raise
    finally:
        if resized_clip:
            try:
                resized_clip.close()
            except:
                pass
        if clip:
            try:
                clip.close()
            except:
                pass
        if tmp_out_path:
            safe_unlink(tmp_out_path)
        if tmp_in_path:
            safe_unlink(tmp_in_path)


async def extract_audio(file_bytes: bytes, filename: str) -> bytes:
    """Extract audio from video as MP4 (AAC)."""
    tmp_in_path = None
    tmp_out_path = None
    clip = None

    try:
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as tmp_in:
            tmp_in.write(file_bytes)
            tmp_in_path = tmp_in.name

        clip = VideoFileClip(tmp_in_path)

        if clip.audio is None:
            raise ValueError("Video has no audio track")

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_out:
            tmp_out_path = tmp_out.name

        clip.audio.write_audiofile(tmp_out_path, codec="aac", logger=None)

        with open(tmp_out_path, "rb") as f:
            result = f.read()

        return result
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"extract_audio error: {e}")
        raise
    finally:
        if clip:
            try:
                clip.close()
            except:
                pass
        if tmp_out_path:
            safe_unlink(tmp_out_path)
        if tmp_in_path:
            safe_unlink(tmp_in_path)
