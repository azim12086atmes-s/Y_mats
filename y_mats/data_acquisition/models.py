import dataclasses
from typing import Optional, List


@dataclasses.dataclass
class VideoMetadata:
    title: str
    description: str
    published_date: str  # or a datetime object
    channel_id: str
    channel_title: str
    tags: Optional[List[str]]
    view_count: Optional[int]
    like_count: int
    comment_count: int
    duration: str  # or a timedelta object
    definition: str  # "hd" or "sd"
    caption_availability: bool


@dataclasses.dataclass
class AcquisitionOutput:
    video_id: str
    metadata: Optional[VideoMetadata]
    video_filepath: Optional[str]
    audio_filepath: Optional[str]
    transcript_source_type: str  # "api", "asr_required", "unavailable"
    raw_transcript_filepath: Optional[str]
    status: str  # "success", "error"
    error_message: Optional[str]