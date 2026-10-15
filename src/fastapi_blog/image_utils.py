# uuid id for generating unique file name
import uuid 
# BytesIO: Pillow can read the file directly from memory
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps

PROFILE_PICS_DIR = Path("src/fastapi_blog/media/profile_pics")

# Note: ------------------
# Our FastAPI application is async but image processing with Pillow is a CPU-bound task. If we perform this work directly inside an async endpoint, it can block the event loop and prevent other requests from being processed efficiently.
# SOLUTION: Implement the Pillow image-processing logic as a regular synchronous function, then offload its execution to a separate thread using a thread pool. This prevents CPU-bound image processing from directly blocking the event loop, allowing FastAPI to remain responsive and handle other asynchronous operations concurrently.
# ------------------------

def process_profile_image(content: bytes) -> str:
  with Image.open(BytesIO(content)) as original:
    img = ImageOps.exif_transpose(original)

    img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

    if img.mode in ("RGBA", "LA", "P"):
      img = img.convert("RGB")

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = PROFILE_PICS_DIR / filename

    PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)

    img.save(filepath, "JPEG", quality=85, optimize=True)

  return filename


def delete_profile_image(filename: str | None) -> None:
  if filename is None:
    return

  filepath = PROFILE_PICS_DIR / filename
  if filepath.exists:
    filepath.unlink()
