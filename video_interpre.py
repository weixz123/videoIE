import os
import sqlite3
import re
from modelscope import Qwen2VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
from modelscope import snapshot_download

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_path TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn

def save_to_db(conn, video_path, description):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO video_descriptions (video_path, description)
        VALUES (?, ?)
    ''', (video_path, description))
    conn.commit()

def natural_sort_key(s):
    """Function to generate a key for natural sorting of strings with numbers"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def infer_video(video_path, model, processor):
    # Get absolute path
    abs_video_path = os.path.abspath(video_path)
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "video",
                    "video": abs_video_path,
                    "max_pixels": 602112,  # Updated to match the limit
                    "fps": 1.0,
                },
                {"type": "text", "text": "采用动宾结构，用一句话详实地描述视频的操作行为，例如'用XX在yy上做zz'，注意描述操作行为的准确性和专业性，比如在主板的什么位置等等"},
            ],
        }
    ]

    try:
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        
        if video_inputs is None:
            raise ValueError(f"Failed to read video from {abs_video_path}")
            
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        generated_ids = model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        return output_text[0]
    except Exception as e:
        print(f"Error processing video {abs_video_path}: {str(e)}")
        return None

def main():
    # Initialize model
    model_dir = "./qwen2vl7b"
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        model_dir, torch_dtype="auto", device_map="auto"
    )
    processor = AutoProcessor.from_pretrained(model_dir)

    # Initialize database
    db_path = "video_descriptions.db"
    conn = init_db(db_path)

    # Video folder path
    video_folder = "video"
    
    # Ensure video folder exists
    if not os.path.exists(video_folder):
        print(f"Video folder '{video_folder}' does not exist!")
        return

    # Get list of video files and sort them naturally
    video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]
    video_files.sort(key=natural_sort_key)

    # Process videos in sorted order
    for video_file in video_files:
        video_path = os.path.join(video_folder, video_file)
        print(f"Processing video: {video_path}")

        description = infer_video(video_path, model, processor)
        if description:
            print(f"Description: {description}")
            save_to_db(conn, video_path, description)
        else:
            print(f"Failed to process video: {video_path}")

    conn.close()

if __name__ == "__main__":
    main()