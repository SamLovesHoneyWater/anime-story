import json, os
import edge_tts

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
    
    Each description should consider the following elements:
    - character_name: the name of the main character in the scene (only one character per scene)
    - view: front, side, back, close-up, etc.
    - clothing: simple white dress, school uniform shirt, black gloves, etc.
    - expression: happy, sad, angry, surprised, etc.
    - pose: standing, sitting, lying down, clasped hands, etc.
    - action: cooking, looking at me, sleeping, etc.
    - setting: indoor, living room, gym, jungle, moon, day, etc.

    For each shot, you should compose a comma-separated list of words or short phrases that concisely and effectively describe the scene, e.g.: "medium shot, white gloves, white dress, wedding dress, bare shoulders, collarbone, excited, standing, tongue out, cutting cake, ceremony, flower, cake, fork"
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
            "description": string in English that contains comma-separated words and short phrases describing the scene
        ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": prefix},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise Exception(f"Error creating shot designs: {e}, got response: {response}")

def generate_speech(text, index, gender, language="zh-CN"):
    """Generate speech from text with retry on failure."""
    if gender == "F":
        if language == "zh-CN":
            voice = "zh-CN-XiaoxiaoNeural"
        elif language == "es-US":
            voice = "es-US-PalomaNeural"
    elif gender == "M":
        if language == "zh-CN":
            voice = "zh-CN-YunxiNeural"
        elif language == "es-US":
            voice = "es-US-AlonsoNeural"
    else:
        raise ValueError(f"Invalid gender {gender}, expected 'M' or 'F'")

    max_retries = 3
    retry_delay = 1
    attempt = 0

    dir_path = f'./audios/{language}'
    file_name = f'{index}.mp3'
    file_path = os.path.join(dir_path, file_name)

    while attempt < max_retries:
        try:
            # Create directories if they don't exist
            os.makedirs(dir_path, exist_ok=True)
            
            communicate = edge_tts.Communicate(text, voice, rate='+50%')
            communicate.save_sync(file_path)
            break
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed with error: {e}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
            else:
                print(f"Failed to save speech after {max_retries} attempts.")
    return file_path
