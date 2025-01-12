import os
import yt_dlp

FFMPEG_PATH = "/usr/bin/ffmpeg"

class YTDownloader:

    @staticmethod
    def mp3_options():
        mp3_options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
            }],
            'ffmpeg_location': FFMPEG_PATH,
            'outtmpl': '%(title)s.%(ext)s',
            }
        return mp3_options

    @staticmethod
    def video_options():
        video_options = {
            'format': 'bestvideo+bestaudio/best',
            'ffmpeg_location': FFMPEG_PATH,
            'outtmpl': '%(title)s.%(ext)s',
            }
        return video_options
    
    @staticmethod
    def download_video(url: str, options: dict) -> str:
        """
        yt-dlp를 사용하여 YouTube 영상/오디오 다운로드
        """
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                result = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(result)
        except Exception as e:
            print(f"다운로드 실패: {e}")
            return None




