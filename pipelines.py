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
    
def generate_shot_image(prompt, index, reference_imgs, client):
    """Generate an image for a shot using OpenAI API and save it"""
    if len(reference_imgs) != 1:
        raise ValueError(f"Expected 1 reference image, got {len(reference_imgs)}")
    try:
        base_img_path = reference_imgs[0]
        
        # Generate image
        response = client.images.edit(
            image=open(base_img_path, "rb"),
            prompt=prompt,
            model="gpt-image-1",
            n=1,
            size="1024x1024",
            quality="medium",
            background="auto"
        )
        
        # Get image data and save
        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Create output directory if it doesn't exist
        os.makedirs("images", exist_ok=True)
        
        # Save image
        filename = f"images/scene_{index:04d}.png"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        print(f"Saved image: {filename}")
        return filename
    except Exception as e:
        print(f"Error generating image: {e}")
        return None



'''
def create_scene_description(text, full_text, client):
    """Create a detailed scene description from text using OpenAI API"""

    prefix = f"""
    Your task is to create a scene description for an anime visual novel.
    You should be concise but detailed.
    You include only elements that are relevant to the viewer's perception.
    """
    prompt = f"""
    Your task is to create a scene description for an anime visual novel.
    The description should include the following elements:
    - style: always "realistic anime visual novel"
    - scene: where the scene takes place (e.g.: at the back rows of a high school classroom on the first floor)
    - setting: short description of the time of day and weather (e.g.: sunny noon)
    - character_name: the name of the main character in the scene (only one character per scene)
    - attire: what the character is wearing (e.g.: a white shirt and a black skirt, and a red ribbon, all part of a Japanese-style school uniform)
    - action: character's action and pose (e.g.: looking at "me" with a smile, holding a pencil in her right hand, left hand supporting her chin)
    - camera: specify the angle, usually directly facing the character (e.g.: medium shot of character, camera facing towards the window of the classroom)
    - background: describe the background elements (e.g., there are trees outside the window)

    The entire chapter is: {full_text}
    The scene you should describe corresponds to the following text: {text}

    Output a single string with the description elements separated by commas, no additional explanatory text.
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
        #return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error creating scene description: {e}")
        return {"description": f"Anime scene based on: {text}"}
'''
'''
def generate_and_save_image(prompt, index, client):
    """Generate an image using OpenAI API and save it"""
    try:
        base_img_path = "baimao.png"
        
        # Generate image
        response = client.images.edit(
            image=open(base_img_path, "rb"),
            prompt=prompt,
            model="gpt-image-1",
            n=1,
            size="1536x1024",
            quality="high",
            background="auto"
        )
        
        # Get image data and save
        image_base64 = response.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        # Create output directory if it doesn't exist
        os.makedirs("images", exist_ok=True)
        
        # Save image
        filename = f"images/scene_{index:04d}.png"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        print(f"Saved image: {filename}")
        return filename
    except Exception as e:
        print(f"Error generating image: {e}")
        return None
'''
