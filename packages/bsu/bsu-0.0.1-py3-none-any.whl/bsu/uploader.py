import os
import time

from bilibili_api import video, Credential, channel_series

from .constants import SLEEP_TIME
from .lang import parse_lan_by_name
from .parser import BccParser


class BilibliSubtitleUploader:

    def __init__(self, sessdata, bili_jct, buvid3):
        self.credential = Credential(
            sessdata=sessdata,
            bili_jct=bili_jct,
            buvid3=buvid3
        )
        self.submit = True
        self.sign = False
        self.code = 'utf-8'

    async def upload_subtitle_by_video(self, bvid, subtitle_path):
        """
        按视频上传字幕
        :param bvid: 视频bvid
        :param subtitle_path: 字幕所在本地路径
        :return:
        """
        if isinstance(bvid, str):
            v = video.Video(bvid=bvid, credential=self.credential)
        else:
            v = bvid
        srt_files = [i for i in os.listdir(subtitle_path) if
                     i.endswith('.srt') or i.endswith('.bcc') or i.endswith('.ass')]
        subtitle_parser = BccParser()
        pages = await v.get_pages()
        for c in pages:
            try:
                subtitle_files = [i for i in srt_files if i.startswith(c['part'])]
                if not subtitle_files:
                    print(f'{c["part"]} 没有字幕')
                    continue
                for subtitle_file in subtitle_files:
                    lang = parse_lan_by_name(subtitle_file)
                    subtitle_file_path = os.path.join(subtitle_path, subtitle_file)
                    subtitle_content = subtitle_parser.parse(subtitle_file_path, self.code)
                    await v.submit_subtitle(lan=lang,
                                            data=subtitle_content,
                                            submit=self.submit,
                                            sign=self.sign,
                                            cid=c['cid'])
            except Exception as e:
                print(f'异常{e}')
            time.sleep(SLEEP_TIME)

    async def upload_subtitle_by_series(self, series_id, subtitle_path):
        """
        按合集上传字幕
        :param series_id: 合集Id
        :param subtitle_path: 字幕所在本地路径
        :return:
        """
        series = channel_series.ChannelSeries(id_=series_id, credential=self.credential)
        videos = await series.get_videos()
        for v in videos:
            await self.upload_subtitle_by_video(v, subtitle_path)
