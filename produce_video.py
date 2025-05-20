import os
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip

# Read all image files from images/ directory
image_files = []
if os.path.exists("images"):
    image_files = sorted([os.path.join("images", f) for f in os.listdir("images") if f.endswith(('.png', '.jpg', '.jpeg'))])

# Read all audio files from audios/{language}/ directory
audio_files = []
language_dirs = [d for d in os.listdir("audios") if os.path.isdir(os.path.join("audios", d))]

language = "zh-CN"  # Default language
assert language in language_dirs, f"Language {language} not found in audio directories."
print(f"Using language: {language}")

audio_dir = os.path.join("audios", language)
if os.path.exists(audio_dir):
    audio_files.extend(sorted([os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith('.mp3')], 
                                key=lambda x: int(os.path.splitext(os.path.basename(x))[0])))
else:
    raise FileNotFoundError(f"Audio directory {audio_dir} does not exist.")


# Create clips from images and audios
clips = []
for img_path, audio_path in zip(image_files, audio_files):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(img_path).with_duration(audio_clip.duration).with_audio(audio_clip)
    clips.append(image_clip)

# Concatenate clips and write to output file
final_clip = concatenate_videoclips(clips, method="compose")
# Create output directory if it doesn't exist
output_dir = os.path.join("output", language)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
final_clip.write_videofile(f"./output/{language}/out.mp4", fps=24)
