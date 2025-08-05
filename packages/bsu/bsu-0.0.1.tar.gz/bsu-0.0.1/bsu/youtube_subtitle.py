# -*- coding: utf-8 -*-
# Author:   zhouju
# At    :   2025/8/3
# Email :   zhouju@sunline.com
# About :   https://blog.codingcat.net

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi


def get_title(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.find("title").text.replace(' - YouTube', '', -1)
    return title


def seconds_to_srt_time(total_seconds):
    """将秒数转换为SRT格式的时间戳（HH:MM:SS,ms）"""
    hours = int(total_seconds // 3600)
    remaining_seconds = total_seconds % 3600
    minutes = int(remaining_seconds // 60)
    seconds = remaining_seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def get_subtitles(video_id, lang='en'):
    youtube = YouTubeTranscriptApi()
    subtitles = youtube.fetch(video_id, languages=[lang])
    with open(f"{get_title(video_id) or video_id}.{lang}.srt", "w", encoding="utf-8") as f:
        for idx, subtitle in enumerate(subtitles, start=1):
            start = seconds_to_srt_time(subtitle.start)
            end = seconds_to_srt_time(subtitle.start + subtitle.duration)
            f.write(f'{idx}\n{start} --> {end}\n{subtitle.text}\n\n')


def get_bilingual_subtitles(video_id, lang1='en', lang2='zh-Hans'):
    youtube = YouTubeTranscriptApi()
    subtitles1 = youtube.fetch(video_id, languages=[lang1])
    subtitles2 = youtube.fetch(video_id, languages=[lang2])
    # 合并为双语格式
    with open(f"{get_title(video_id) or video_id}.{lang1}-{lang2}.srt", "w", encoding="utf-8") as f:
        for idx, s in enumerate(zip(subtitles1.snippets, subtitles2.snippets), start=1):
            start = seconds_to_srt_time(s[0].start)
            end = seconds_to_srt_time(s[0].start + s[0].duration)
            f.write(f'{idx}\n{start} --> {end}\n{s[0].text}\n{s[1].text}\n\n')
