# Content Distribution and Media

How to upload, process, store, and serve media at scale. This topic covers the video pipeline (YouTube, Netflix), file sync (Dropbox, Google Drive), and image optimization — all common system design interview problems where the data is large, the processing is heavy, and CDN costs dominate the budget.

## Key Points

- **Video transcoding** — upload → store original → split into chunks → transcode to multiple resolutions in parallel → store variants → serve via CDN. Use resumable uploads for large files.
- **Adaptive bitrate streaming** — pre-transcode into multiple bitrates, serve via HLS/DASH manifest. Player switches quality mid-stream based on bandwidth.
- **CDN cost optimization** — serve popular content from CDN, long-tail from origin. Multi-tier caching. Newer codecs (H.265, AV1) save 30–50% bandwidth.
- **File sync** — block-level storage with deduplication. Metadata DB tracks versions. Notify other devices via WebSocket. Conflicts: keep both versions and let user resolve.
- **Image processing** — on-upload thumbnailing or on-the-fly URL-based transforms (image CDN). WebP/AVIF for smaller sizes. Progressive JPEG for perceived performance.

## Example

Designing the video upload and serving pipeline for a video-sharing platform:

```text
Requirements:
  500 hours of video uploaded per minute.
  1B video views per day. Global audience.
  Must support 480p through 4K.

Upload flow:
  Client → resumable upload to S3 (chunked, 5 MB parts).
  Upload complete → publish "VideoUploaded" event to Kafka.

Processing pipeline:
  Transcoding workers consume events.
  DAG: Extract audio → Transcode video (4 parallel: 480p, 720p, 1080p, 4K)
       → Generate thumbnails → Extract metadata → Update DB.
  Each resolution: split into 6-second segments for HLS.
  Store all segments in S3. Write manifest (.m3u8) per resolution.
  Total processing time: ~2× video duration on GPU instances.

Serving:
  Viewer opens video → fetch master manifest from API.
  Player downloads 480p first segment (fast start).
  Measures bandwidth → switches to 1080p if bandwidth allows.
  All segments served from CDN (pull model — first view populates cache).

Cost optimization:
  Top 1% of videos (viral) → pre-warm on all CDN edges.
  Bottom 80% (long tail) → serve from origin or regional CDN only.
  Encode new uploads in AV1 (50% smaller than H.264).
  Estimated CDN savings: $2M/month at this scale.
```
