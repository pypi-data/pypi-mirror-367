# -*- coding: utf-8 -*-
# Author:   zhouju
# At    :   2025/7/31
# Email :   zhouju@sunline.com
# About :   https://blog.codingcat.net

import click
from .bsu import upload_subtitle_by_video


@click.command()
@click.option('--sessdata', required=True, help='sessdata')
@click.option('--bili_jct', required=True, help='bili_jct')
@click.option('--buvid3', required=True, help='buvid3')
@click.option('--bvid', required=True, help='bvid')
@click.option('--subtitle_path', required=True, help='字幕文件所在路径')
def bsu(sessdata, bili_jct, buvid3, bvid, subtitle_path):
    upload_subtitle_by_video(sessdata, bili_jct, buvid3, bvid, subtitle_path)
