import re
import subprocess
import os

def parse_video_id(video_identifier):
    """
    Parses a YouTube video identifier (URL or ID) and returns the video ID.
    If the identifier is invalid, it returns None.
    """
    if not video_identifier:
        return None

    # Check if the identifier is a URL
    url_match = re.match(r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)", video_identifier)
    if url_match:
        return url_match.group(1)
    
    # If not a URL, assume it's a video ID and check if it's a valid format
    if re.match(r"^[a-zA-Z0-9_-]+$", video_identifier):
        return video_identifier

    # Invalid identifier
    return None
def run_yt_dlp(video_id, quality, output_dir="y_mats/data_acquisition/y_mat_video"):
    """
    Runs yt-dlp to download a video with the specified ID and quality.
    Args:
        video_id (str): The YouTube video ID.
        quality (str): The desired video quality (e.g., "720p").
    Returns:
        str: The output filepath if successful, otherwise None.
    """
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
    output_filename_template = os.path.join(output_dir, f"{video_id}.%(ext)s")  # Use video ID as filename in the specified directory

    command = [
        "yt-dlp",
        "-f", f"bestvideo[height<={quality.replace('p', '')}]+bestaudio/best[height<={quality.replace('p', '')}]",  # Select best quality within the specified height
        "--merge-output-format", "mp4",  # Merge video and audio into mp4
        "-o", output_filename_template,
        f"https://www.youtube.com/watch?v={video_id}",
    ]

    print(f"Running yt-dlp command: {command}")  # Log the command being executed

    try:
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, check=True)
        print(f"yt-dlp stdout:\n{result.stdout}")  # Log stdout
        print(f"yt-dlp stderr:\n{result.stderr}")  # Log stderr

        # Construct the filepath directly, assuming mp4 extension due to --merge-output-format mp4
        filepath = os.path.join(output_dir, f"{video_id}.mp4")
        if os.path.exists(filepath):
            print(f"yt-dlp successfully downloaded to: {filepath}")  # Log success
            return filepath
        else:
            print(f"Error: yt-dlp reported download success but file not found at {filepath}")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp: {e}")
        print(f"yt-dlp output (stderr):\n{e.stderr.strip()}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def run_ffmpeg(video_filepath):
    """
    Extracts the audio stream from the given video file using ffmpeg.
    Args:
        video_filepath (str): The path to the video file.
    Returns:
        str: The filepath to the extracted audio file, or None if extraction fails.
    """
    if not os.path.exists(video_filepath):
        print(f"Error: Video file not found at {video_filepath}")
        return None

    output_dir = "y_mats/data_acquisition/y_mat_audio"
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, os.path.splitext(os.path.basename(video_filepath))[0] + ".mp3")  # Output as MP3 in the specified directory
    command = [
        "ffmpeg",
        "-i", video_filepath,
        "-q:a", "0",  # Best quality for MP3
        "-map", "a",  # Select only the audio stream
        "-y",  # Overwrite output file if it exists
        output_filename,  # Use output_filename here
    ]
    try:
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, check=True)

        if os.path.exists(output_filename):
            return output_filename
        else:
            print(f"Error: ffmpeg reported success, but audio file not found at {output_filename}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e}")
        print(f"ffmpeg output (stderr):\n{e.stderr.strip()}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def check_captions_available(video_id):
    """
    Checks if captions are available for the given video ID using yt-dlp.
    Args:
        video_id (str): The YouTube video ID.
    Returns:
        bool: True if captions are available, False otherwise.
    """
    command = [
        "yt-dlp",
        "--list-subs",
        f"https://www.youtube.com/watch?v={video_id}",
    ]

    try:
        process = subprocess.run(command, capture_output=True, text=True)
        # If yt-dlp lists any subtitles, captions are considered available
        return "available formats" in process.stdout.lower()
    except subprocess.CalledProcessError as e:
        # yt-dlp may return an error code even if subtitles are not found,
        # so we'll check the output for "No subtitles"
        return "no subtitles" not in e.stderr.lower()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
def download_transcript(video_id, output_dir="y_mats/data_acquisition/y_mat_transcript"):
    """
    Downloads the transcript for the given video ID using yt-dlp.
    Args:
        video_id (str): The YouTube video ID.
    Returns:
        str: The filepath to the downloaded transcript, or None if download fails.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"{video_id}.en.vtt")  # Assuming English subtitles and .vtt format in the specified directory
    command = [
        "yt-dlp",
        "--write-subs",  # Write subtitles to a file
        "--sub-langs", "en",  # Specify English subtitles
        "--skip-download",  # Skip video download, we only want the subtitles
        "-o", output_filename,
        f"https://www.youtube.com/watch?v={video_id}",
    ]
    try:
        result = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, check=True)
        # Check if the output file exists. yt-dlp might not raise an error
        # if subtitles are not found, but it will also not create the file.
        if os.path.exists(output_filename):
            return output_filename
        else:
            print(f"Error: yt-dlp did not download transcript for {video_id}. Subtitles might not be available.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp: {e}")
        print(f"yt-dlp output (stderr):\n{e.stderr.strip()}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None