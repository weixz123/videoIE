from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def split_video(input_video, output_folder, segment_duration=5):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 加载视频
    video = VideoFileClip(input_video)
    duration = video.duration  # 视频总时长

    # 计算切分的段数
    num_segments = int(duration // segment_duration)
    if duration % segment_duration != 0:
        num_segments += 1

    # 切分视频
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = min((i + 1) * segment_duration, duration)
        segment = video.subclipped(start_time, end_time)

        # 输出文件名
        output_file = os.path.join(output_folder, f"segment_{i+1}.mp4")
        segment.write_videofile(output_file, codec="libx264")

        print(f"Segment {i+1} saved to {output_file}")

    # 关闭视频对象
    video.close()

# 使用示例
input_video = "input.mp4"  # 输入视频文件路径
output_folder = "video"  # 输出文件夹路径
split_video(input_video, output_folder)