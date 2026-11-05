# Content Distribution and Media

This topic owns the CDN and the media pipeline that fills it. A CDN keeps shared bytes near users. Upload, transcode, adaptive streaming, file sync, and image transforms are how those bytes get produced. Application caches for per-user data stay in Caching.

## Key Points

- **Why a CDN** — shared bytes, users in more than one region, and an origin you want to take off the path. Unique or single-region responses stay on the app cache.
- **Edge and origin** — the user hits a PoP; the origin is storage or the app that can build the object. Pull fills an edge on the first miss. Push uploads ahead of a premiere.
- **Cacheable and dynamic** — public, shared, reusable responses go to the edge. Cookies, `Authorization`, `private`, and `no-store` bypass it. `Vary: Cookie` quietly fragments the cache.
- **CDN TTL** — how long one edge may serve a copy. Long TTL for hashed names. Short TTL for a URL that changes in place. `s-maxage` is the shared-cache lifetime.
- **Purge and invalidation** — a new hashed URL beats a purge. Purge one stable URL when the name cannot change, and keep a short TTL behind it. A zone-wide purge is a miss storm.
- **PoPs and placement** — a PoP only helps if your users are near it and a miss does not still cross an ocean. One city next to the origin does not need a CDN yet.
- **Origin shield** — edges miss to one mid-tier cache, and only that cache calls the origin. Forty simultaneous edge misses become one origin fetch.
- **Video transcoding** — resumable upload, store the original, split, transcode renditions in parallel, write segments, then let the edge pull. Push only the premiere.
- **Adaptive bitrate** — several renditions, short segments, an HLS or DASH manifest. The player switches mid-stream. Both protocols are plain HTTP, so the edge rules above apply to each segment.
- **CDN cost** — hot titles on every edge, long-tail titles at the shield or origin, shield to cut origin fetches, smaller codecs and renditions to cut bytes.
- **File sync** — block-level storage with deduplication. A metadata DB tracks versions. Other devices hear about a change over a WebSocket. Conflicts: keep both and let the user resolve.
- **Image processing** — thumbnails on upload, or a URL transform at the edge. The transformed image is its own public object with a TTL. WebP or AVIF and progressive JPEG cut size and time-to-first-paint.

## Example

A video-sharing site, with the CDN decisions written next to the pipeline. The prices and the skew are invented.

```text
Requirements:
  500 hours of video uploaded per minute.
  1B video views per day. Viewers on six continents.
  Playback from 480p through 4K.

Upload and transcode:
  Client → resumable upload to object storage (5 MB parts).
  Upload complete → "VideoUploaded" on the queue.
  Workers: extract audio, transcode 480p/720p/1080p/4K in parallel,
  thumbnails, metadata, 6-second HLS segments, one manifest per rendition.

CDN:
  Ordinary titles use pull. The first view in a PoP fills that edge for the TTL.
  A scheduled premiere is pushed to the edges that will carry it.
  An origin shield sits in front of object storage so a TTL expiry
  does not turn every PoP into an origin GET.
  Hashed segment names, multi-day TTL, no purge.
  The master manifest is a stable URL: short TTL, purge that URL on republish.

Cost:
  Hot titles, about 10% of the catalog and most of the views, stay on every edge.
  A premiere in that set is pushed ahead of time. The long tail stays on the shield or the origin.
  New uploads are encoded in AV1, about half the bytes of H.264.
  At a made-up $0.02/GB of edge egress, a million 10-minute views
  cost $7,500 at 5 Mbps and $1,500 at 1 Mbps.
```

## See also

- [Caching](../05_Caching/) — cache-aside, write-through, eviction, and invalidation for application data. Not the CDN.
- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — the zero-to-millions stage that only mentions a CDN. The cards are here.
