import sys
from y_mats.data_acquisition import core

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_acquisition.py <youtube_url> <api_key>")
        sys.exit(1)

    video_url = sys.argv[1]
    api_key = sys.argv[2]

    result = core.acquire_data(video_url, api_key)
    print(result)