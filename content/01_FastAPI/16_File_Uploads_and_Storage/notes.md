# File Uploads and Storage

How FastAPI receives uploaded bytes, and where those bytes actually live in a production system.

## Key Points

- **`UploadFile`** — async wrapper around a `SpooledTemporaryFile`; small uploads stay in memory, large ones spill to disk.
- **Stream large files** — read in chunks (`await file.read(64 * 1024)`) instead of loading everything at once.
- **Object storage** — production apps don't keep uploads on local disk; push to S3/GCS/B2/R2 and store only the URL or key.
- **Pre-signed URLs** — for large or high-volume uploads, hand the client a short-lived URL and let them upload (or download) directly from storage; your API never touches the bytes.

## Example

Two upload paths in one app — small files proxied through the API, large files handled with pre-signed URLs:

```python
import uuid

import boto3
from fastapi import Depends, FastAPI, File, UploadFile
from pydantic import BaseModel

from app.config import get_settings, Settings

app = FastAPI()


def get_s3(settings: Settings = Depends(get_settings)):
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    )


# --- Small file: API receives and forwards ---
@app.post("/avatars")
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    s3=Depends(get_s3),
    settings: Settings = Depends(get_settings),
):
    if file.content_type not in {"image/png", "image/jpeg"}:
        raise HTTPException(415, "unsupported media type")
    key = f"avatars/{user_id}/{uuid.uuid4()}-{file.filename}"
    s3.upload_fileobj(file.file, settings.s3_bucket, key)
    return {"key": key, "size": file.size}


# --- Large file: pre-signed URL ---
class UploadTicket(BaseModel):
    upload_url: str
    key: str
    expires_in: int


@app.post("/uploads/ticket", response_model=UploadTicket)
async def request_upload_ticket(
    filename: str,
    user_id: int,
    s3=Depends(get_s3),
    settings: Settings = Depends(get_settings),
):
    key = f"uploads/{user_id}/{uuid.uuid4()}/{filename}"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=900,
    )
    return UploadTicket(upload_url=url, key=key, expires_in=900)


# --- Streaming read example ---
@app.post("/import")
async def import_csv(file: UploadFile = File(...)):
    """Stream a potentially huge CSV without buffering it in memory."""
    rows = 0
    while chunk := await file.read(64 * 1024):
        rows += chunk.count(b"\n")
    return {"rows": rows}
```

- `POST /avatars` — small image, the API forwards it to S3. Acceptable for a 200 KB profile picture.
- `POST /uploads/ticket` — client wants to upload a 500 MB video. API hands back a pre-signed PUT URL; the client uploads straight to S3 and notifies us when it's done.
- `POST /import` — large CSV proxied through the API, but streamed in 64 KB chunks so memory stays flat regardless of file size.
