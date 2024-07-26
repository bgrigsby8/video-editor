#!/usr/bin/env python
"""
Script to cut a video file according to silences below
a threshold for a specified duration.
"""
import argparse
import logging
import math
import moviepy.editor as mpy
import numpy as np
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

SUBCLIPS_OUTPUT_FILEPATH = "edited_sub_clips/"
CONCATENATED_OUTPUT_FILEPATH = "edited_concatenated_clip/"


def _audio_to_db(audio_clip):
    """Takes in an audio clip and returns a numpy array
    of audio values in dB."""
    audio_samples = list(audio_clip.iter_frames())
    audio_array = numpy.array(audio_samples)
    audio_db = 20 * numpy.log10(numpy.abs(audio_array))

    return audio_db

def _check_output_directory(directory):
    """Checks to make sure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.debug(f"Created directory {directory}")


class VideoEditor:
    def __init__(self, video_file, dynamic_silence_threshold=True, silence_jacket=0.25, volume_threshold=0.1, original_file_path=''):
        self.edited_video = None
        self.sub_clips = []
        self.speaking_intervals = []
        self.video_clip = None
        self.video_file = video_file
        self.window_is_silent = []
        self.window_size = 0.1

        # Variables gather from user
        self.dynamic_silence_threshold = dynamic_silence_threshold # Default: True
        self.ease_in = silence_jacket # Default: 0.25
        self.volume_threshold = volume_threshold # Default: 0.01

        # Determine the output directory for subclips
        self.output_directory = os.path.join(os.path.dirname(original_file_path), 'edited_subclips')
        logging.debug(f"Output directory set to: {self.output_directory}")
        _check_output_directory(self.output_directory)

    def extract_video(self):
        logging.info("Extracting video and audio...")
        self.video_clip = mpy.VideoFileClip(self.video_file)
        logging.debug(f'Extracted video clip: {self.video_clip}')

    def get_audio_clip(self):
        logging.info("Extracting audio clip...")
        self.audio_clip = self.video_clip.audio
        logging.debug(f"Extracted audio clip from video clip.")

    def get_number_windows(self):
        logging.info("Calculating number of windows for audio...")
        self.num_windows = math.floor(self.audio_clip.end / self.window_size)
        logging.debug(f"Extracted {self.num_windows} windows of audio in provided file.")

    def get_silent_windows(self):
        logging.info("Identifying silent windows in audio...")
        for i in range(self.num_windows):
            s = self.audio_clip.subclip(i * self.window_size, (i + 1) * self.window_size)
            v = s.max_volume()
            # logging.info(f"Max volume for window #{i}: {v}")

            if i < 3 and self.dynamic_silence_threshold:
                self.volume_threshold = v if v > self.volume_threshold else self.volume_threshold
                logging.debug(f"Volume threshold set to {self.volume_threshold}")

            self.window_is_silent.append(v < self.volume_threshold)
        logging.info(f"List of silent windows: {self.window_is_silent}")

    def find_speaking(self):
        logging.info("Finding speaking intervals in audio...")
        self.get_audio_clip()
        self.get_number_windows()
        self.get_silent_windows()

        speaking_start = 0
        speaking_end = 0
        if len(self.window_is_silent) == 0:
            logging.error("Could not find instances where there was silence.")
            return

        for i in range(1, len(self.window_is_silent)):
            e1 = self.window_is_silent[i - 1]
            e2 = self.window_is_silent[i]

            if e1 and not e2:
                speaking_start = i * self.window_size

            if not e1 and e2:
                speaking_end = i * self.window_size
                new_speaking_interval = [speaking_start - self.ease_in, speaking_end + self.ease_in]
                need_to_merge = len(self.speaking_intervals) > 0 and self.speaking_intervals[-1][1] > new_speaking_interval[0]
                if need_to_merge:
                    merged_interval = [self.speaking_intervals[-1][0], new_speaking_interval[1]]
                    self.speaking_intervals[-1] = merged_interval
                else:
                    self.speaking_intervals.append(new_speaking_interval)

    def cut_video(self):
        logging.info("Cutting video into subclips...")
        logging.debug(f"Speaking intervals: {self.speaking_intervals}")
        if len(self.speaking_intervals) == 0:
            raise ValueError("Received empty list of speaking intervals.")

        self.sub_clips = []
        for speaking_interval in self.speaking_intervals:
            sub_clip = self.video_clip.subclip(speaking_interval[0], speaking_interval[1])
            sub_clip = sub_clip.set_audio(self.video_clip.audio.subclip(speaking_interval[0], speaking_interval[1]))
            self.sub_clips.append(sub_clip)
            logging.debug(f"Sub clip audio duration: {sub_clip.audio.duration if sub_clip.audio else 'No audio'}")

        logging.debug(f"Sub clips: {self.sub_clips}")
        logging.debug(f"Created {len(self.sub_clips)} speaking video sub clips.")

        self.sub_clips = [clip for clip in self.sub_clips if clip.duration > 0]
        if len(self.sub_clips) != len(self.speaking_intervals):
            logging.warning("Some sub clips had zero duration and were removed.")

        # Test 2: using ffmpeg directly
        # from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
        # self.sub_clips = [ffmpeg_extract_subclip(inputfile=self.video_file, start_time=start_time, end_time=end_time, outputfile="temp-file.mp4")

    def write_sub_clips(self):
        logging.info("Writing subclips...")
        for i, sub_clip in enumerate(self.sub_clips):
            try:
                output_filepath = os.path.join(self.output_directory, f"sub_clip_{i+1}.mp4")
                sub_clip_with_audio = sub_clip.set_audio(sub_clip.audio)
                sub_clip_with_audio.write_videofile(output_filepath, audio_codec='aac')
                logging.debug(f"Wrote clip {sub_clip_with_audio} to {output_filepath}")
            except Exception as e:
                logging.error(f"An error occurred writing the video file: {e}")

        self.video_clip.close()
        if self.audio_clip:
            self.audio_clip.close()

    def concatenate_videos(self):
        """Concatenate audio clips to a single video."""
        logging.debug("Concatenating videos")
        for i, clip in enumerate(self.sub_clips):
            logging.debug(f"Clip {i}: duration={clip.duration}, size={clip.size}, fps={clip.fps}")

        self.edited_video = mpy.concatenate(self.sub_clips)
        logging.info("Successfully concatenated sub clips.")

    def write_edited_video(self):
        """Writes the files to local memory."""
        _check_output_directory(CONCATENATED_OUTPUT_FILEPATH)
        try:
            output_filepath = os.path.join(CONCATENATED_OUTPUT_FILEPATH, f"concatenated_clip.mp4")
            self.edited_video.write_videofile(output_filepath)
            logging.info(f"Wrote concatenated video file as {CONCATENATED_OUTPUT_FILEPATH}")
        except Exception as e:
            logging.error(f"An error occurred writing the video file: ", e)
        finally:
            self.video_clip.close()
            if self.audio_clip:
                    self.audio_clip.close()

    def process_video(self, concatenate=False):
        logging.info("Starting video processing...")
        self.extract_video()
        self.find_speaking()
        self.cut_video()

        if concatenate:
            self.concatenate_videos()
            self.write_edited_video()
        else:
            self.write_sub_clips()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Edit video around silences found')
    parser.add_argument('-f', '--file', type=str, required=True, help='Path to the raw video file.')
    parser.add_argument('--dynamic-silence-threshold', type=bool, help='Dynamically find the minimum silence threshold from the first few video windows.')
    parser.add_argument('-s', '--silence-jacket', type=int, default=0.25, help='Jacket around non-silent clips to keep in seconds.')
    parser.add_argument('-v', '--volume-threshold', type=float, default=0.1, help='Minimum volume threshold if not dynamically calculated.')
    parser.add_argument('-c', '--concatenate', type=bool, default=False, help='Concatenate videos into one clip.')

    args = parser.parse_args()

    editor = VideoEditor(args.file, args.dynamic_silence_threshold, args.silence_jacket, args.volume_threshold)
    editor.process_video(args.concatenate)
