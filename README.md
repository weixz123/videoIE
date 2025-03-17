# videoIE
基于qwenvl进行视频信息抽取


# 文件结构
mllm
 ┣ video 经过切分处理的短视频
 ┃ ┣ segment_1.mp4
 ┃ ┣ ...
 ┃ ┗ segment_9.mp4
 ┣ input.mp4 输入视频
 ┣ split.py 视频切分，固定5s切一个视频
 ┣ video_descriptions.db 存储抽取的视频信息
 ┗ video_interpre.py 视频信息抽取主文件


 # 输入视频

 https://www.bilibili.com/video/BV1Su4y1T7M9/?spm_id_from=333.1387.favlist.content.click
