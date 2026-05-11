## `UploadFile`

`UploadFile` is FastAPI's wrapper for multipart file uploads. Under the hood it's a `SpooledTemporaryFile` — small uploads sit in memory, large ones spill to disk — so a 4 GB upload doesn't blow up the worker.

```python
from fastapi import File, UploadFile

@app.post("/avatars")
async def upload_avatar(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }
```

`UploadFile` exposes an async `read()`, `write()`, `seek()`, and `close()`. For large files, stream chunks with `while chunk := await file.read(64 * 1024):` instead of `await file.read()` — the latter loads everything into memory.

For multiple files: `files: list[UploadFile] = File(...)`. Form fields alongside files: combine `Form(...)` with `File(...)` on the same handler.

## Object storage

Storing user uploads on the API server's local disk doesn't survive restarts or scale beyond one machine. Production apps push uploads to **object storage**: S3, Google Cloud Storage, Azure Blob, Backblaze B2, R2. The API receives the upload, forwards it to storage, and persists only the URL (or storage key) in its database.

```python
import boto3

s3 = boto3.client("s3")

@app.post("/avatars")
async def upload_avatar(file: UploadFile = File(...), user_id: int = ...):
    key = f"avatars/{user_id}/{file.filename}"
    s3.upload_fileobj(file.file, "my-bucket", key)
    return {"url": f"https://my-bucket.s3.amazonaws.com/{key}"}
```

The local API never holds the file long-term — only the durable storage does. This is what makes stateless APIs possible: the upload survives even if every worker restarts.

## Signed URLs

For large files (and to avoid forwarding bandwidth through your API at all), use **pre-signed URLs**. The client asks your API for a short-lived URL, then uploads directly to object storage. The API never touches the bytes.

```python
@app.post("/uploads/url")
async def get_upload_url(filename: str, user_id: int = ...):
    key = f"uploads/{user_id}/{uuid.uuid4()}/{filename}"
    url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": "my-bucket", "Key": key},
        ExpiresIn=900,    # 15 minutes
    )
    return {"upload_url": url, "key": key}

# Client then does: PUT <upload_url> with the file as the body
```

After upload, the client (or a webhook) tells your API "key X is ready" and you persist the reference. Same pattern in reverse for downloads: `generate_presigned_url("get_object", ...)` produces a short-lived link that bypasses your API.

Pre-signed URLs are how serious file-upload products work — gigabyte uploads never touch the application's bandwidth, memory, or CPU.
