from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import Response
from typing import Optional
from loguru import logger

from app.service.video_editor import clip_video, add_watermark, convert_to_gif, extract_audio
from app.service.google_auth import verify_google_token, is_authenticated

video_edit_router = APIRouter(prefix='/api/video-edit')

ERROR_MESSAGE = "작업 중 오류 발생"


@video_edit_router.post("/clip")
async def api_clip_video(
    file: UploadFile = File(...),
    start_time: Optional[float] = Form(None),
    end_time: Optional[float] = Form(None),
    authorization: Optional[str] = Header(None)
):
    """Clip video to specified time range."""
    try:
        user_info = await verify_google_token(authorization)
        file_bytes = await file.read()

        result = await clip_video(
            file_bytes=file_bytes,
            filename=file.filename,
            start_time=start_time,
            end_time=end_time
        )

        if not is_authenticated(user_info):
            result = await add_watermark(
                file_bytes=result,
                filename="clip.mp4"
            )

        return Response(
            content=result,
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename=clip_{file.filename}"}
        )
    except Exception as e:
        logger.error(f"api_clip_video error: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGE)


@video_edit_router.post("/watermark")
async def api_add_watermark(
    file: UploadFile = File(...),
    watermark_text: Optional[str] = Form(None),
    watermark_symbol: Optional[str] = Form(None),
    watermark_position: Optional[str] = Form("bottom-right"),
    authorization: Optional[str] = Header(None)
):
    """Add watermark to video."""
    if not watermark_text and not watermark_symbol:
        raise HTTPException(status_code=400, detail="Either watermark_text or watermark_symbol is required")

    try:
        file_bytes = await file.read()

        result = await add_watermark(
            file_bytes=file_bytes,
            filename=file.filename,
            watermark_text=watermark_text,
            watermark_symbol=watermark_symbol,
            position=watermark_position
        )

        return Response(
            content=result,
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename=watermarked_{file.filename}"}
        )
    except Exception as e:
        logger.error(f"api_add_watermark error: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGE)


@video_edit_router.post("/gif")
async def api_convert_to_gif(
    file: UploadFile = File(...),
    fps: Optional[int] = Form(10),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    start_time: Optional[float] = Form(0),
    duration: Optional[float] = Form(None),
    authorization: Optional[str] = Header(None)
):
    """Convert video to GIF."""
    try:
        user_info = await verify_google_token(authorization)
        file_bytes = await file.read()

        if not is_authenticated(user_info):
            file_bytes = await add_watermark(
                file_bytes=file_bytes,
                filename=file.filename
            )

        result = await convert_to_gif(
            file_bytes=file_bytes,
            filename=file.filename,
            fps=fps,
            width=width,
            height=height,
            start_time=start_time,
            duration=duration
        )

        output_filename = file.filename.rsplit(".", 1)[0] + ".gif"

        return Response(
            content=result,
            media_type="image/gif",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except Exception as e:
        logger.error(f"api_convert_to_gif error: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGE)


@video_edit_router.post("/audio")
async def api_extract_audio(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """Extract audio from video."""
    try:
        file_bytes = await file.read()

        result = await extract_audio(
            file_bytes=file_bytes,
            filename=file.filename
        )

        output_filename = file.filename.rsplit(".", 1)[0] + "_audio.mp4"

        return Response(
            content=result,
            media_type="audio/mp4",
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except ValueError as e:
        logger.warning(f"api_extract_audio validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"api_extract_audio error: {e}")
        raise HTTPException(status_code=500, detail=ERROR_MESSAGE)
