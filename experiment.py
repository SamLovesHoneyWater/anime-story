import openai
import os, time
from dotenv import load_dotenv

from utils import read_file_to_list, read_json_from_file, save_json_to_file, validate_voiceover_script, validate_shot_designs
from pipelines import create_voiceover_script, design_shots, generate_shot_image

# Read novel from file
novel_list = read_file_to_list()
full_novel_text = "\n".join(novel_list)
print(f"Novel list length: {len(novel_list)}")

# Initialize OpenAI client
load_dotenv()
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

VOICEOVER_SCRIPT_FILENAME = "voiceover_script.json"
SHOTS_DESIGN_FILENAME = "shots.json"

CHARACTER_REFERENCE_IMGS = {
    "江洛": "nanzhu.png",
    "柳如烟": "baimao.png",
    "蒋鑫城": "nanzhu.png"
}

# Check if voiceover script already exists
if os.path.exists(VOICEOVER_SCRIPT_FILENAME):
    # Load existing voiceover script
    print(f"(1) Voiceover script already exists, loading from {VOICEOVER_SCRIPT_FILENAME}...")
    voiceover_script = read_json_from_file(VOICEOVER_SCRIPT_FILENAME)
    validate_voiceover_script(voiceover_script)
    print("(2) Successfully validated existing voiceover script.")
else:
    # Create new voiceover script
    print("(0) Creating voiceover script...")
    voiceover_script = create_voiceover_script(full_novel_text, client)
    print("(1) Finished generating voiceover script, validating...")
    validate_voiceover_script(voiceover_script)
    print(f"(2) Successfully validated voiceover script")
    # Add index to each line in the script
    for i, item in enumerate(voiceover_script['script']):
        item['index'] = i + 1
    save_json_to_file(voiceover_script, VOICEOVER_SCRIPT_FILENAME)
print(f"[INFO] Voiceover script characters: {voiceover_script['characters']}, length: {len(voiceover_script['script'])}")
script = voiceover_script['script']
characters = voiceover_script['characters'][1:]

# Check if shots design already exists
if os.path.exists(SHOTS_DESIGN_FILENAME):
    # Load existing shots design
    print(f"(1) Shots design already exists, loading from {SHOTS_DESIGN_FILENAME}...")
    shots = read_json_from_file(SHOTS_DESIGN_FILENAME)
    validate_shot_designs(shots, len(script), characters)
    print("(2) Successfully validated existing shot designs.")
else:
    # Create shot designs
    print("(0) Creating shot designs...")
    shots = design_shots(script, characters, client)
    print("(1) Finished generating shot designs, validating...")
    validate_shot_designs(shots, len(script), characters)
    print(f"(2) Successfully validated shot designs, length: {len(shots['shots'])}")
    save_json_to_file(shots, "shots.json")
print(f"[INFO] Shots design length: {len(shots['shots'])}")

# Generate images for each shot
results = []
for i, shot in enumerate(shots['shots']):
    coverage = shot['coverage']
    description = shot['description']
    
    # Create scene description
    reference_imgs = [CHARACTER_REFERENCE_IMGS[shot['character_name']]]
    image_path = generate_shot_image(description, i, reference_imgs, client)
    
    # Add to results
    results.append((description, image_path))
    print(f"Generated image for shot {i+1}", end="\r")
print("Done!                ")

# Print the final results
print("\nResults:")
for line, image_path in results:
    print(f"Line: {line[:50]}... -> Image: {image_path}")
