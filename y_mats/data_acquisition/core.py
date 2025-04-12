import os
import json
import urllib.parse
import urllib.request

from typing import Optional

from y_mats.data_acquisition import utils
from .models import VideoMetadata, AcquisitionOutput


def validate_input(video_identifier):
    """
    Validates the input video identifier (URL or ID).
    Args:
        video_identifier (str): The YouTube video URL or ID.
    Returns:
        str: The canonical video ID if valid.
    Raises:
        ValueError: If the video identifier is invalid.
    """
    video_id = utils.parse_video_id(video_identifier)
    if not video_id:
        raise ValueError("Invalid video identifier.")
    return video_id


def retrieve_metadata(video_id, api_key):
    """
    Retrieves metadata for the given video ID from the YouTube Data API.
    Args:
        video_id (str): The YouTube video ID.
    Returns:
        VideoMetadata: An instance of the VideoMetadata dataclass.
    """
    if not api_key:
        raise ValueError("YouTube API key not set.")

    base_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,contentDetails,statistics",
        "id": video_id,
        "key": api_key,
    }
    url = f"{base_url}?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                raise urllib.error.HTTPError(url, response.status, "Invalid request", response.headers, None)
            data = json.load(response)

            if not data["items"]:
                raise ValueError(f"Video with ID '{video_id}' not found.")

            item = data["items"][0]
            snippet = item["snippet"]
            content_details = item.get("contentDetails", {})
            statistics = item.get("statistics", {})

            # Extract relevant metadata, handling potential missing fields
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            published_date = snippet.get("publishedAt", "")
            channel_id = snippet.get("channelId", "")
            channel_title = snippet.get("channelTitle", "")
            tags = snippet.get("tags", [])
            view_count = int(statistics.get("viewCount", 0))
            like_count = int(statistics.get("likeCount", 0))
            comment_count = int(statistics.get("commentCount", 0))
            duration = content_details.get("duration", "")
            definition = content_details.get("definition", "sd")  # Default to "sd" if missing
            caption_availability = "caption" in content_details.get("caption", "false")  # Check for caption field

            return VideoMetadata(
            title=title,
            description=description,
            published_date=published_date,
            channel_id=channel_id,
            channel_title=channel_title,
            tags=tags,
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count,
            duration=duration,
            definition=definition,
            caption_availability=caption_availability,
            )
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise ValueError(f"Error fetching metadata: {e}")


def download_video(video_id):
    """
    Downloads the video file for the given video ID.
    Args:
        video_id (str): The YouTube video ID.
    Returns:
        str: The filepath to the downloaded video file.
    """
    output_path = utils.run_yt_dlp(video_id, "720p")
    if not output_path:
        raise ValueError("yt-dlp failed to provide an output path.")
    # The output_path from run_yt_dlp should already have the correct extension.
    return output_path



def extract_audio(video_filepath):
    """
    Extracts the audio stream from the given video file.
    Args:
        video_filepath (str): The path to the video file.
    Returns:
        str: The filepath to the extracted audio file.
        Raises:
            NotImplementedError: Because actual implementation is pending.
        """
        # Placeholder: Replace with actual audio extraction logic using ffmpeg
        # For now, simulate a successful extraction
    return utils.run_ffmpeg(video_filepath)


def handle_transcript(video_id):
    """
    Handles transcript acquisition: either downloads an existing transcript or
    flags the need for ASR.
    Args:
        video_id (str): The YouTube video ID.
    Returns:
        tuple[str, Optional[str]]: (transcript_source_type, raw_transcript_filepath), where
                                  transcript_source_type is one of 'api', 'asr_required', 'unavailable',
                                  and raw_transcript_filepath is the path to the downloaded transcript
                                  if available, or None otherwise.
    """
    try:
        # Check if captions are available (placeholder logic)
        if utils.check_captions_available(video_id):  # Assume this function exists
            # Download transcript (placeholder logic)
            transcript_filepath = utils.download_transcript(video_id)  # Assume this function exists and returns the filepath
            if transcript_filepath:
                return "api", transcript_filepath
            else:
                return "unavailable", None  # Download failed for some reason
        else:
            return "asr_required", None  # No captions available, ASR needed (not implemented)
    except Exception as e:
        print(f"Error handling transcript: {e}")
        return "unavailable", None  # An error occurred


def acquire_data(video_identifier, api_key):
    """
    Orchestrates the data acquisition process for a given YouTube video.
    Args:
        video_identifier (str): The YouTube video URL or ID.
    Returns:
        AcquisitionOutput: An instance of the AcquisitionOutput dataclass.
    """
    try:
        video_id = validate_input(video_identifier)
    except ValueError as e:
        return AcquisitionOutput(
            video_id=None,
            metadata=None,
            video_filepath=None,
            audio_filepath=None,
            transcript_source_type=None,
            raw_transcript_filepath=None,
            status="error",
            error_message=str(e),
        )

    metadata = retrieve_metadata(video_id, api_key)
    if not metadata:
        transcript_source_type, raw_transcript_filepath = handle_transcript(video_id)  # Get transcript info even if metadata fails
        return AcquisitionOutput(
            video_id=video_id,
            metadata=None,
            video_filepath=None,
            audio_filepath=None,
            transcript_source_type=None,
            raw_transcript_filepath=None,
            status="error",
            error_message="Failed to retrieve metadata.",
        )

    video_filepath = download_video(video_id)
    if not video_filepath:
        transcript_source_type, raw_transcript_filepath = handle_transcript(video_id)  # Get transcript info even if download fails
        return AcquisitionOutput(
            video_id=video_id,
            metadata=metadata,
            video_filepath=None,
            audio_filepath=None,
            transcript_source_type=None,
            raw_transcript_filepath=None,
            status="error",
            error_message="Failed to download video.",
        )

    audio_filepath = extract_audio(video_filepath)
    if not audio_filepath:
        transcript_source_type, raw_transcript_filepath = handle_transcript(video_id)  # Get transcript info even if audio extraction fails
        return AcquisitionOutput(
            video_id=video_id,
            metadata=metadata,
            video_filepath=video_filepath,
            audio_filepath=None,
            transcript_source_type=None,
            raw_transcript_filepath=None,
            status="error",
            error_message="Failed to extract audio.",
        )

    transcript_source_type, raw_transcript_filepath = handle_transcript(video_id)

    return AcquisitionOutput(
        video_id=video_id,
        metadata=metadata,
        video_filepath=video_filepath,
        audio_filepath=audio_filepath,
        transcript_source_type=transcript_source_type,
        raw_transcript_filepath=raw_transcript_filepath,
        status="success",
        error_message=None,
    )


if __name__ == "__main__":
    # Example usage (with placeholder values):
    video_identifier = "dQw4w9WgXcQ"  # Replace with a real video ID or URL for testing
    result = acquire_data(video_identifier)
    print(result)