import openai
import os
from datetime import datetime
from dotenv import load_dotenv

from utils import read_file_to_list, read_json_from_file, save_json_to_file, validate_voiceover_script, validate_shot_designs
from pipelines import create_voiceover_script, design_shots, generate_speech
from diffuse import generate_diffuse_shot

# Read novel from file
novel_list = read_file_to_list()
full_novel_text = "\n".join(novel_list)
print(f"Novel list length: {len(novel_list)}")

# Initialize OpenAI client
load_dotenv()
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

VOICEOVER_SCRIPT_FILENAME = "voiceover_script.json"
SHOTS_DESIGN_FILENAME = "shots.json"


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
characters = voiceover_script['characters']


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


# Create skeleton character features file for user to fill in
character_features = {}
for character in characters:
    character_features[character] = {
        "gender": "",
        "description": ""
    }
now = datetime.now()
timestamp = now.strftime("%m%d%y%H%M")
character_features_filename = f"character_features_{timestamp}.json"
save_json_to_file(character_features, character_features_filename)

print(f"\nCreated character features file: {character_features_filename}")
print(f"Please fill in gender (M/F) and descriptions for each character in this file.")
print(f"The characters are: {', '.join(characters)}")
input("Press Enter when you have completed editing the character features file...")

# Load character features from the edited file
character_features = read_json_from_file(character_features_filename)
print("\nLoaded character features:")
for character, features in character_features.items():
    desc_preview = features["description"][:50] + "..." if len(features["description"]) > 50 else features["description"]
    print(f"- {character} ({features['gender']}): {desc_preview}")


# Generate speech audio for each line
print("\nGenerating speech audio for each line...")
audio_paths = []
for i, line in enumerate(script):
    voice_name = line['voice_name']
    content = line['content']
    index = line['index']
    if voice_name[1:] == "arrator":
        gender = "F"
    else:
        gender = character_features[voice_name]['gender']    
    audio_path = generate_speech(content, index, gender)
    audio_paths.append(audio_path)
    print(f"Generated audio for line {index}: {voice_name}               ", end="\r")
print("\nSpeech generation complete! Generated {len(audio_paths)} audio files.")


# Generate images for each shot
results = []
for i, shot in enumerate(shots['shots']):
    coverage = shot['coverage']
    description = shot['description']
    character_name = shot['character_name']
    character_feature = character_features[character_name]
    # Create scene description
    image_path = generate_diffuse_shot(description, character_feature, i+1)
    # Add to results
    results.append((description, image_path))
    print(f"Generated image for shot {i+1}", end="\r")
print("Done!                                            ")
