import requests
import json
import yt_dlp
import logging

FFMPEG_PATH = "/usr/bin/ffmpeg"
logging.basicConfig(level=logging.INFO)


def read_github_json(json_url: str) -> dict:
    try:
        response = requests.get(json_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP request error: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {e}")
        return {}


class YTDownloader:
    @staticmethod
    def download_video(video_url: str, option: str, json_url='json/yt_options.json',) -> str:
        options = read_github_json(json_url)
        if not options:
            logging.error("Failed to load options from the JSON file.")
            return None

        download_options = options.get(option)
        if not download_options:
            logging.error(f"'{option}' option is not available in the JSON file.")
            return None

        try:
            with yt_dlp.YoutubeDL(download_options) as ydl:
                result = ydl.extract_info(video_url, download=True)
                return ydl.prepare_filename(result)
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Download error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        return None
