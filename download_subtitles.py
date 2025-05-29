import yt_dlp
import argparse
import os

def download_subtitles(video_url, preferred_languages=['pl', 'en']):
    """
    Downloads subtitles for a YouTube video in the preferred languages.
    """
    try:
        # Options to get video info, including available subtitles
        ydl_opts_info = {
            'skip_download': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_title = info_dict.get('title', 'video')

        available_subs = info_dict.get('subtitles', {})
        # automatic_subs = info_dict.get('automatic_captions', {}) # This is less reliable for pre-checking availability

        selected_lang = None
        is_auto_caption = False # Flag to indicate if we're targeting an auto-caption

        # 1. Prioritize preferred languages for manually created subtitles in VTT format
        for lang in preferred_languages:
            if lang in available_subs:
                for sub_info in available_subs[lang]:
                    if sub_info.get('ext') == 'vtt':
                        selected_lang = lang
                        print(f"Found manual VTT subtitle for '{lang}'.")
                        break  # Found VTT for this lang
            if selected_lang:
                break # Found a manual subtitle in preferred languages

        # 2. If no manual subtitle found, iterate through preferred languages for auto-generated subtitles
        if not selected_lang:
            is_auto_caption = True # We are now targeting auto-captions
            for lang_pref in preferred_languages:
                selected_lang = lang_pref
                print(f"No manual VTT found. Attempting auto-generated for preferred language: '{selected_lang}'.")
                
                safe_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
                final_ydl_opts = {
                    'skip_download': True,
                    'subtitlesformat': 'vtt',
                    'subtitleslangs': [selected_lang],
                    'writeautomaticsub': True,
                    'writesubtitles': False, # Ensure we only try for auto subtitles here
                    'outtmpl': {'default': f'{safe_title} [{selected_lang}].%(ext)s'}, # Revert to this
                    # 'verbose': True, 
                }

                print(f"Attempting to download subtitle for language: '{selected_lang}' (Auto-caption: True)")
                try:
                    # yt-dlp naming convention for subtitles: outtmpl_val_before_ext.lang_code.ext_val
                    downloaded_filename = f"{safe_title} [{selected_lang}].{selected_lang}.vtt"
                    final_desired_filename = f"{safe_title} [{selected_lang}].vtt"

                    # Ensure potential old files from previous attempts are removed
                    for f_name in [downloaded_filename, final_desired_filename]:
                        if os.path.exists(f_name):
                            try:
                                os.remove(f_name)
                            except OSError as e:
                                print(f"Warning: Could not remove pre-existing file '{f_name}': {e}")

                    with yt_dlp.YoutubeDL(final_ydl_opts) as ydl_downloader:
                        ydl_downloader.download([video_url])
                    
                    if os.path.exists(downloaded_filename):
                        print(f"INFO: Subtitle for '{selected_lang}' (auto) downloaded by yt-dlp as: {downloaded_filename}")
                        # Rename to desired format
                        try:
                            os.rename(downloaded_filename, final_desired_filename)
                            print(f"SUCCESS: Renamed subtitle to: {final_desired_filename}")
                            break # Exit loop on successful download and rename
                        except OSError as e:
                            print(f"ERROR: Failed to rename '{downloaded_filename}' to '{final_desired_filename}': {e}")
                            selected_lang = None # Indicate failure as rename failed
                            break # Stop if rename fails
                    else:
                        # yt-dlp completed but didn't create the file, meaning it likely reported no subs for this lang
                        print(f"INFO: yt-dlp call completed, but subtitle file '{expected_filename}' not found for '{selected_lang}'. This usually means yt-dlp found no subtitle for this language (check its output above).")
                        if lang_pref == preferred_languages[-1]: # If this was the last language in the list
                            print("All preferred languages for auto-captions attempted.")
                            selected_lang = None # Indicate no subtitle was successfully downloaded
                        else:
                            print(f"Trying next preferred language for auto-captions...")
                            selected_lang = None # Reset selected_lang before next iteration to ensure loop continues if this was not the last lang
                
                except yt_dlp.utils.DownloadError as de:
                    # This error might catch more general download issues with yt-dlp for this attempt
                    print(f"INFO: yt-dlp DownloadError for '{selected_lang}'. Message: {de}")
                    if lang_pref == preferred_languages[-1]:
                        print("All preferred languages for auto-captions attempted (DownloadError).")
                        selected_lang = None
                    else:
                        print(f"Trying next preferred language for auto-captions (DownloadError)...")
                        selected_lang = None # Reset before next iteration
                except Exception as exc:
                    print(f"An unexpected error occurred during download attempt for '{selected_lang}': {exc}")
                    selected_lang = None # Error, so no successful download
                    break # Stop on unexpected error
            
            if not selected_lang: # If loop finished and selected_lang is None (no success)
                 print("Failed to download any auto-generated subtitles for the preferred languages.")

        # 3. If manual subtitle was found and downloaded (selected_lang is set and is_auto_caption is False)
        elif selected_lang and not is_auto_caption:
            safe_title = "".join([c for c in video_title if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
            final_ydl_opts = {
                'skip_download': True,
                'subtitlesformat': 'vtt',
                'subtitleslangs': [selected_lang],
                'writesubtitles': True, # For manual subs
                'writeautomaticsub': False,
                'outtmpl': {'default': f'{safe_title} [{selected_lang}].%(ext)s'}, # Revert to this
            }
            print(f"Attempting to download MANUALLY selected subtitle for language: '{selected_lang}'")
            try:
                # Similar logic for manual: download with .lang.vtt, then rename
                downloaded_filename_manual = f"{safe_title} [{selected_lang}].{selected_lang}.vtt"
                final_desired_filename_manual = f"{safe_title} [{selected_lang}].vtt"

                for f_name in [downloaded_filename_manual, final_desired_filename_manual]:
                    if os.path.exists(f_name):
                        try:
                            os.remove(f_name)
                        except OSError as e:
                            print(f"Warning: Could not remove pre-existing file '{f_name}': {e}")

                with yt_dlp.YoutubeDL(final_ydl_opts) as ydl_downloader:
                    ydl_downloader.download([video_url])
                
                if os.path.exists(downloaded_filename_manual):
                    print(f"INFO: Manual subtitle for '{selected_lang}' downloaded by yt-dlp as: {downloaded_filename_manual}")
                    try:
                        os.rename(downloaded_filename_manual, final_desired_filename_manual)
                        print(f"SUCCESS: Renamed manual subtitle to: {final_desired_filename_manual}")
                    except OSError as e:
                        print(f"ERROR: Failed to rename manual sub '{downloaded_filename_manual}' to '{final_desired_filename_manual}': {e}")
                        selected_lang = None # Indicate failure
                else:
                    print(f"INFO: yt-dlp call completed for manual sub '{selected_lang}', but file '{downloaded_filename_manual}' not found.")
                    selected_lang = None # Indicate failure
            except yt_dlp.utils.DownloadError as de:
                print(f"ERROR: yt-dlp could not download manual subtitle for '{selected_lang}'. Message: {de}")
                selected_lang = None # Indicate failure
            except Exception as exc:
                print(f"An unexpected error occurred during manual download attempt for '{selected_lang}': {exc}")
                selected_lang = None

        # Fallback to English auto-generated if still no subtitle and 'en' was not in preferred or failed.
        # The original prompt mentioned "then auto-generated English if available".
        # This logic has become complex. The loop for auto preferred languages should handle 'en' if it's in the list.
        # If 'en' is a hardcoded final fallback, it would be here.
        # For now, the above logic should suffice if 'en' is in preferred_languages.

        if not selected_lang:
            # This case means preferred_languages was empty or all attempts (manual/auto) failed.
            print("No suitable subtitle downloaded after all attempts.")

    except yt_dlp.utils.DownloadError as e: # Catches errors from the initial extract_info
        print(f"Error during subtitle download: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download subtitles for a YouTube video.")
    parser.add_argument("url", help="The URL of the YouTube video.")
    parser.add_argument("--langs", nargs="+", default=['pl', 'en'], 
                        help="Preferred languages for subtitles, space-separated (e.g., pl en fr). Defaults to 'pl en'.")
    
    args = parser.parse_args()
    
    download_subtitles(args.url, args.langs)
