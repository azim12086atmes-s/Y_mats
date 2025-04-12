# YouTube Video Data Acquisition Pipeline

This document describes the data flow and pipeline structure of the YouTube video data acquisition system.

## Pipeline Stages

The pipeline consists of the following stages:

1.  **Input:**

    *   A YouTube video identifier (URL or ID) is provided as input to the `acquire_data` function.
    *   **Data:** Video identifier (string).
    *   **Storage:** In memory, as a function parameter.

2.  **Input Validation:**

    *   The system validates the input video identifier. (Placeholder implementation fully functional)

3.  **Metadata Retrieval:**

    *   Video metadata (title, description, channel information, etc.) *would be* retrieved from the YouTube Data API. (Placeholder: currently returns dummy data).
    *   **Data:** Currently, dummy video metadata (strings).
    *   **Storage:** In memory, within a `VideoMetadata` object.
    *   **Note:** This stage uses a placeholder. The actual implementation would involve interacting with the YouTube Data API and parsing the response.

4.  **Video Download:**

    *   The video file is downloaded from YouTube.
    *   **Data:** Video file (MP4).
    *   **Storage:** Temporarily in `/tmp/y_mats_downloads/`, with the filename based on the video ID (e.g., `/tmp/y_mats_downloads/{video_id}.mp4`).

    *   **Note:** This stage uses a placeholder. The actual implementation would involve downloading the video using a library like `yt-dlp`.
5.  **Audio Extraction:**

    *   The audio stream is extracted from the downloaded video file.
    *   **Data:** Audio file (WAV).
    *   **Storage:** Temporarily in `/tmp/y_mats_audio/`, with the filename based on the video ID (e.g., `/tmp/y_mats_audio/{video_id}.wav`).

    *   **Note:** This stage uses a placeholder. The actual implementation would involve extracting the audio using a tool like `ffmpeg`.
6.  **Transcript Handling:**

    *   The system checks for available captions/transcripts.
        *   If a transcript is available via the YouTube API, it is downloaded.
            *   **Data:** Transcript text (format TBD, potentially SRT).
            *   **Storage:** Temporarily, path to file stored in memory.
        *   If no transcript is available, the system flags the video as requiring Automatic Speech Recognition (ASR).
            *   **Data:** Flag indicating ASR is required.
            *   **Storage:** In memory, as a status within the `AcquisitionOutput` object.
    *   **Current Implementation:** Always returns "unavailable" and `None` (no transcript).
    *   **Note:** This stage is a placeholder. The actual implementation would involve checking for available transcripts (potentially using the YouTube Data API or another method) and either downloading them or flagging the need for ASR.

7.  **Output:**

    *   The system returns an `AcquisitionOutput` object containing:
        *   Video ID
        *   Video Metadata
        *   Filepaths to the downloaded video and audio
        *   Transcript source information (API, ASR required, or unavailable) and filepath (if available)
        *   Overall status (success or error)
        *   Error message (if any)
    *   **Data:** Aggregated data from previous stages.
    *   **Storage:** In memory, as an `AcquisitionOutput` object.

## Data Flow Diagram (Conceptual)