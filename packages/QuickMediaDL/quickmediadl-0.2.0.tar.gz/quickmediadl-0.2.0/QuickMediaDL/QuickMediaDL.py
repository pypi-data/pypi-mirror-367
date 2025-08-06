import yt_dlp
import os
from tqdm import tqdm
import logging

# Configure a more professional logger to display messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class QuickMediaDL:
    """
    An advanced library for downloading videos and audio from online sources using yt-dlp.
    """

    def __init__(self, download_path="downloads"):
        """
        Initializes the downloader with a default download path.

        :param download_path: The path where files will be saved.
        """
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        self.progress_bar = None

    def get_yt_dlp_options(self, filename=None, quality="720p", audio_only=False, subtitle_langs=None, no_playlist=True):
        """
        Creates yt-dlp options based on user inputs.
        """
        # Determine the output template
        if filename:
            outtmpl = os.path.join(self.download_path, f"{filename}.%(ext)s")
        else:
            outtmpl = os.path.join(self.download_path, '%(title)s.%(ext)s')

        # Basic yt-dlp options
        opts = {
            'outtmpl': outtmpl,
            'noplaylist': no_playlist,
            'logger': self.get_logger(),
            'progress_hooks': [self.progress_hook],
            'writesubtitles': bool(subtitle_langs),
            'subtitleslangs': subtitle_langs if subtitle_langs else [],
        }

        # Select video or audio quality
        if audio_only:
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]/best'

        return opts

    def get_logger(self):
        """
        A custom logger to display yt-dlp messages.
        """
        class YtdlpLogger:
            def debug(self, msg):
                # We ignore debug messages
                pass

            def warning(self, msg):
                logging.warning(msg)

            def error(self, msg):
                logging.error(msg)

        return YtdlpLogger()

    def progress_hook(self, d):
        """
        A progress hook to display a status bar with tqdm.
        """
        if d['status'] == 'downloading':
            if self.progress_bar is None:
                self.progress_bar = tqdm(total=d.get('total_bytes'), unit='B', unit_scale=True, desc=d.get('filename'))
            self.progress_bar.update(d['downloaded_bytes'] - self.progress_bar.n)
        elif d['status'] == 'finished':
            if self.progress_bar:
                self.progress_bar.close()
                self.progress_bar = None
            logging.info(f"Successfully downloaded {d.get('filename')}.")

    def get_available_formats(self, url):
        """
        Gets a list of available formats for a specific URL.

        :param url: The video URL.
        :return: A list of available formats.
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('formats', [])
        except Exception as e:
            logging.error(f"Error fetching formats: {e}")
            return []

    def download(self, url, quality="720p", audio_only=False, filename=None, subtitle_langs=None, no_playlist=True):
        """
        Downloads video or audio with custom settings.

        :param url: The video or playlist URL.
        :param quality: The desired video quality (e.g., "720p", "1080p").
        :param audio_only: If True, only the audio will be downloaded.
        :param filename: A custom filename (without extension).
        :param subtitle_langs: A list of subtitle languages (e.g., ["en", "fa"]).
        :param no_playlist: If True, prevents downloading a playlist.
        """
        ytdl_opts = self.get_yt_dlp_options(filename, quality, audio_only, subtitle_langs, no_playlist)
        try:
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            logging.error(f"An error occurred during download: {e}")

    def set_output_directory(self, path):
        """
        Changes the default directory for saving files.

        :param path: The new path.
        """
        self.download_path = path
        if not os.path.exists(path):
            os.makedirs(path)
        logging.info(f"Output directory changed to {path}")