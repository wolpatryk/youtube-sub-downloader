# YouTube Subtitle Downloader

This script downloads subtitles for a given YouTube video. It allows users to specify preferred languages and prioritizes manually created subtitles in VTT format.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1.  **Clone the repository or download the script.**
    (Assuming the user has `download_subtitles.py` and `requirements.txt` in the same directory)

2.  **Install dependencies:**
    Open your terminal or command prompt, navigate to the directory where the script is saved, and run:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `yt-dlp`, which is required for the script to work.

## Usage

To download subtitles, run the script from your terminal:

```bash
python download_subtitles.py <youtube_video_url> [options]
```

**Arguments:**

-   `<youtube_video_url>`: (Required) The full URL of the YouTube video for which you want to download subtitles.

**Options:**

-   `--langs LANG [LANG ...]`: (Optional) A list of preferred language codes, separated by spaces. The script will try to download subtitles in these languages in the order they are provided. If not specified, it defaults to Polish (`pl`) and then English (`en`).

    Example: `pl en es` for Polish, English, and Spanish.

**Examples:**

1.  **Download subtitles with default language preferences (Polish, then English):**
    ```bash
    python download_subtitles.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ```

2.  **Download subtitles with specified preferred languages (e.g., English, then Spanish):**
    ```bash
    python download_subtitles.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --langs en es
    ```

3.  **Download subtitles for a video, preferring French:**
    ```bash
    python download_subtitles.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --langs fr
    ```

The script will attempt to find and download subtitles in VTT format. It prioritizes:
1.  Manually created subtitles in the first preferred language.
2.  Manually created subtitles in subsequent preferred languages.
3.  Auto-generated subtitles in the first preferred language.
4.  Auto-generated subtitles in subsequent preferred languages.
5.  If no preferred language subtitles are found, it will try to download auto-generated English subtitles as a fallback.

Downloaded subtitle files will be saved in the same directory as the script, with a filename format like: `Video Title [language_code].vtt`.
