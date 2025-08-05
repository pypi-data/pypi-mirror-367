# -*- coding: utf-8 -*-
# Author:   zhouju
# At    :   2025/7/31
# Email :   zhouju@sunline.com
# About :   https://blog.codingcat.net

import asyncio

from .uploader import BilibliSubtitleUploader


def upload_subtitle_by_video(sessdata, bili_jct, buvid3, bvid, subtitle_path):
    uploader = BilibliSubtitleUploader(
        sessdata=sessdata,
        bili_jct=bili_jct,
        buvid3=buvid3
    )
    asyncio.run(uploader.upload_subtitle_by_video(bvid=bvid, subtitle_path=subtitle_path))


def upload_subtitle_by_series(sessdata, bili_jct, buvid3, series_id, subtitle_path):
    uploader = BilibliSubtitleUploader(
        sessdata=sessdata,
        bili_jct=bili_jct,
        buvid3=buvid3
    )
    asyncio.run(uploader.upload_subtitle_by_series(series_id=series_id, subtitle_path=subtitle_path))
