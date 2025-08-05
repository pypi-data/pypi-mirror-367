# -*- coding: utf-8 -*-
# Author:   zhouju
# At    :   2025/8/3
# Email :   zhouju@sunline.com
# About :   https://blog.codingcat.net
# from bsu.youtube_subtitle import get_bilingual_subtitles, get_subtitles
#
# get_bilingual_subtitles("etsKTOsTckY")
# get_subtitles("etsKTOsTckY")
import os.path

from youtube_transcript_api import YouTubeTranscriptApi


def seconds_to_srt_time(total_seconds):
    """将秒数转换为SRT格式的时间戳（HH:MM:SS,ms）"""
    hours = int(total_seconds // 3600)
    remaining_seconds = total_seconds % 3600
    minutes = int(remaining_seconds // 60)
    seconds = remaining_seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def generate_subtitle(video_id, title):
    path_prefix = '/Users/codingcat/Downloads/Ariannita la Gringa'
    youtube = YouTubeTranscriptApi()
    if not os.path.exists(f"{path_prefix}/{title}.en.srt"):
        subtitles = youtube.fetch(video_id, languages=['en'])
        subtitle_text = ''
        for idx, subtitle in enumerate(subtitles, start=1):
            start = seconds_to_srt_time(subtitle.start)
            end = seconds_to_srt_time(subtitle.start + subtitle.duration)
            subtitle_text += f'{idx}\n{start} --> {end}\n{subtitle.text}\n\n'

        with open(f"{path_prefix}/{title}.en.srt", "w", encoding="utf-8") as f:
            f.write(subtitle_text)
    if not os.path.exists(f"{path_prefix}/{title}.en-zh-Hans.srt"):
        subtitles1 = youtube.fetch(video_id, languages=['en'])
        try:
            subtitles2 = youtube.fetch(video_id, languages=['zh-Hans'])
        except Exception as e:
            try:
                subtitles2 = youtube.fetch(video_id, languages=['zh-Hant'])
            except Exception as e:
                return
                # 合并为双语格式
        subtitle_text = ''
        for idx, s in enumerate(zip(subtitles1.snippets, subtitles2.snippets), start=1):
            start = seconds_to_srt_time(s[0].start)
            end = seconds_to_srt_time(s[0].start + s[0].duration)
            subtitle_text += f'{idx}\n{start} --> {end}\n{s[0].text}\n{s[1].text}\n\n'

        with open(f"{path_prefix}/{title}.en-zh-Hans.srt", "w", encoding="utf-8") as f:
            f.write(subtitle_text)


videos = []
for i in videos:
    generate_subtitle(i['videoId'], i['title'])

# import requests
# from bs4 import BeautifulSoup
#
#
# url = f"https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"
# html = requests.get(url)
# soup = BeautifulSoup(html, "html.parser")
#
# c = [i['richItemRenderer']['content']['videoRenderer'] for i in c if i.get('richItemRenderer')]
# vid = [{'videoId': i['videoId'], 'title': i['title']['runs'][0]['text']} for i in c]


video_name = {i.split('.')[1].strip(): i.split('.')[0] for i in os.listdir() if i.endswith('.mp4')}
null = []
for i in os.listdir():
    if not i.endswith('.srt'):
        continue
    name = i.split('.')[0].strip()
    if video_name.get(name):
        os.rename(i, f"{video_name.get(name)}. {i}")

print(len(null))
from collections import Counter

srt_f = [i.strip() for i in os.listdir() if i.endswith('.srt')]
c = Counter(srt_f)
cc = [i for i in c if c[i] > 1]

for i in os.listdir():
    os.rename(i, i.strip())
