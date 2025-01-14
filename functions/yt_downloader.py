import json
import yt_dlp
import logging

json_path = "./json/yt_options.json" 

class YTDownloader:
    @staticmethod
    def download_video(video_url: str, file_type: str) -> str:
        with open(json_path, 'r', encoding='utf-8') as file:
            options = json.load(file)
        try:
            with yt_dlp.YoutubeDL(options.get(file_type)) as ydl:
                result = ydl.extract_info(video_url, download=True)
                file_name = ydl.prepare_filename(result)
                file_name= file_name.replace(".webm", file_type)
                return file_name

        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Download error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        return None
