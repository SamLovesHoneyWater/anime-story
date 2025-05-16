import json, base64, os
from diffuse import simple_diffuse

def create_voiceover_script(full_text, client):
    prompt = f"""
    {full_text}
    I want to turn this into a video novel. We will have a series of anime images to make up a video, and a voiceover to narrate the story.
    Generate the script for the voiceover, and define different characters, including the narrator.
    Output a json that follows:
    {{
        "characters": ["narrator", "character_1", ...],
        "script": [
            "voice_name": string in English,
            "content": string in Chinese
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a voiceover script generator."},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Error creating voiceover script: {e}, got response: {response}")

def design_shots(script, characters, client):
    """Create a list of detailed shot descriptions from voiceover script"""

    prefix = f"""
    Your task is to design shots and describe them for an anime visual novel.
    Think of yourself as a playwright or director.
    You should be concise but detailed. You should include only elements that are relevant to the viewer's perception.
    
    Each description should be a single string with the following elements:
    - character_name: the name of the main character in the scene (only one character per scene)
    - style: always "realistic anime visual novel"
    - scene: where the shot takes place (e.g.: at the back rows of a high school classroom on the first floor)
    - setting: short description of the time of day and weather (e.g.: sunny noon)
    - attire: what the character is wearing (e.g.: a white shirt and a black skirt, and a red ribbon, all part of a Japanese-style school uniform)
    - action: character's action and pose (e.g.: looking at "me" with a smile, holding a pencil in her right hand, left hand supporting her chin)
    - camera: specify the angle, usually directly facing the character (e.g.: medium shot of character, camera facing towards the window of the classroom)
    - background: describe the background elements (e.g., there are trees outside the window)
    """
    prompt = f"""
    Full script: {script}
    
    The shots you design should cover the entire script.
    Usually, one shot corresponds to one line, but you can design a shot that covers at most 2 lines if they are related and short.

    Output a json that follows:
    {{
        "shots": [
            "character_name": string, one of: {characters}
            "coverage": [index_1, index_2, ...] # A list of int indices of the lines covered by this shot, at most length 2
            "description": string in English that includes the required elements, separated by commas
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": prefix},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Error creating shot designs: {e}, got response: {response}")

def generate_diffuse_shot(shot_description, character_feature, index):
    gender = character_feature["gender"]
    character_description = character_feature["description"]
    # Force single character
    if "M" in gender:
        prompt = "(1boy), "
    elif "F" in gender:
        prompt = "(1girl), "
    else:
        raise ValueError(f"Invalid gender: {gender}, expected 'M' or 'F'")
    prompt += f"(masterpiece), {character_description}, {shot_description}"
    image = simple_diffuse(prompt)
    # Create output directory if it doesn't exist
    os.makedirs("images", exist_ok=True)

    # Save image
    filename = f"images/scene_{index:04d}.png"
    image.save(filename)
    return filename
