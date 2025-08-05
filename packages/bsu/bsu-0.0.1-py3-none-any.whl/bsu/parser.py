# -*- coding: utf-8 -*-
# Author:   zhouju
# At    :   2025/7/31
# Email :   zhouju@sunline.com
# About :   https://blog.codingcat.net
import json
import os

from pysubs2 import SSAFile


class BccParser(object):
    @staticmethod
    def srt2bcc(srtf, code='utf-8'):
        bss_dict = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": []
        }
        count1 = 1
        count2 = 2
        stime = 1
        etime = 1
        num = 1
        content = ""
        with open(os.path.join('./inf', srtf), 'r', encoding=code) as f:
            counttt = len(f.readlines())
        with open(os.path.join('./inf', srtf), 'r', encoding=code) as f:
            for index, value in enumerate(f.readlines()):
                value = value.strip('\n')
                if value == str(num):
                    count1 = index + 1
                    count2 = count1 + 1
                    num = num + 1
                elif index == count1:
                    st1 = value.strip().split(':')[0]
                    st2 = value.strip().split(':')[1]
                    st3 = value.strip().split(':')[2].split(',')[0]
                    st4 = value.strip().split(':')[2].split(',')[1].split()[0]
                    et1 = value.strip().split(':')[2].split()[2]
                    et2 = value.strip().split(':')[3]
                    et3 = value.strip().split(':')[4].split(',')[0]
                    et4 = value.strip().split(':')[4].split(',')[1]
                    stime = str(int(st1) * 3600 + int(st2) * 60 + int(st3)) + "." + st4
                    etime = str(int(et1) * 3600 + int(et2) * 60 + int(et3)) + "." + et4
                elif index == count2:
                    content = value
                elif value == "":
                    dic = {"from": float(stime), "to": float(etime), "location": 2, "content": content}
                    bss_dict['body'].append(dic)
                elif index == counttt:
                    content = content + "\n" + value
                    dic = {"from": float(stime), "to": float(etime), "location": 2, "content": content}
                    bss_dict['body'].append(dic)
                elif value:
                    content = content + "\n" + value
        return bss_dict

    @staticmethod
    def ass2bcc(ass_file, code='utf-8'):
        # 读取ASS文件
        subs = SSAFile.load(ass_file)

        # 构建BCC格式的JSON结构
        bcc_content = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": []
        }

        # 转换每条字幕
        for line in subs:
            bcc_content["body"].append({
                "from": line.start / 1000,  # 转换为秒
                "to": line.end / 1000,
                "content": line.text
            })
        return bcc_content

    @staticmethod
    def bcc(bcc_file, code='utf-8'):
        with open(bcc_file, 'r', encoding=code) as f:
            bcc_content = json.loads(f.read())
        return bcc_content

    def parse(self, file, code='utf-8'):
        func_map = {
            'srt': self.srt2bcc,
            'ass': self.ass2bcc,
            'bcc': self.bcc
        }
        func = func_map.get(file.split('.')[-1])
        if func:
            return func(file, code)
        else:
            raise ValueError("不支持的文件格式")
