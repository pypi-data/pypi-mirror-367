# -*- coding: utf-8 -*-
# Author:   zhouju
# At    :   2025/8/1
# Email :   zhouju@sunline.com
# About :   https://blog.codingcat.net
from bsu.lang import parse_lan_by_name


def test_parse_lang():
    lang = parse_lan_by_name('009. Fast Eddy.en.srt')
    print(lang)


if __name__ == '__main__':
    test_parse_lang()
