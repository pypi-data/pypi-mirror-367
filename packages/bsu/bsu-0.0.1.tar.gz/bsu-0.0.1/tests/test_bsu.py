import unittest
from bsu.bsu import upload_subtitle_by_video, upload_subtitle_by_series
from bsu.parser import BccParser


class TestBsu(unittest.TestCase):

    def setUp(self) -> None:
        self.sessdata = "562daab4%2C1769431183%2C7822f%2A72CjAJM7aFB3JQl0AU4Ahdu6ut0oPlW8mIJj32LORjVC3GpUkSGXiKIosO_aWcNV9-pVwSVnNMZFQxQ2c4dE9ST0JRbzhfdU5aTVhxNG11MndFUDJiS19GcWszdS1nYlJGY0REWTlHT3lrazhEUlNsN3h1VTluRk9EQlJVVklDeUpKUjUxQ3M0WWhRIIEC"
        self.bili_jct = "35de8934be82c404454117a0ea60f7a2"
        self.buvid3 = "ED4D87DB-9EC9-B31B-0FAA-973FBFAE579294253infoc"

    def test_upload_by_video(self):
        bvid = 'BV1dVhjziEmx'  # 修改为自己的bvid
        subtitle_path = '/Users/codingcat/Downloads/Ariannita la Gringa'  # 修改为自己的字幕路径
        upload_subtitle_by_video(self.sessdata, self.bili_jct, self.buvid3, bvid, subtitle_path)

    def test_upload_by_series(self):
        series_id = 0  # 修改为自己的合集Id
        subtitle_path = '/xxx'  # 修改为自己的字幕路径
        upload_subtitle_by_series(self.sessdata, self.bili_jct, self.buvid3, series_id, subtitle_path)


class TestBccParser(unittest.TestCase):

    def test_ass2bcc(self):
        bcc_dict = BccParser.ass2bcc("/xxx")  # 修改为自己的字幕路径
        assert bcc_dict

    def test_srt2ass(self):
        bcc_dict = BccParser.srt2bcc("/xxx")  # 修改为自己的字幕路径
        assert bcc_dict


if __name__ == '__main__':
    unittest.main()
