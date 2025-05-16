import json

def read_file_to_list(file_path="sample.txt"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read all lines and strip whitespace
            lines = file.readlines()
            # Filter out empty lines
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            return non_empty_lines
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
def read_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

def save_json_to_file(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving JSON to file: {e}")
    
def validate_voiceover_script(voiceover_script):
    if not isinstance(voiceover_script, dict):
        raise TypeError("Voiceover script must be a dictionary")

    if 'characters' not in voiceover_script or not isinstance(voiceover_script['characters'], list):
        raise ValueError("Voiceover script must contain a 'characters' list")

    if 'script' not in voiceover_script or not isinstance(voiceover_script['script'], list):
        raise ValueError("Voiceover script must contain a 'script' list")

    for i, item in enumerate(voiceover_script['script']):
        if not isinstance(item, dict):
            raise TypeError(f"Script item {i} must be a dictionary")
        if 'voice_name' not in item:
            raise ValueError(f"Script item {i} missing 'voice_name' field")
        if 'content' not in item:
            raise ValueError(f"Script item {i} missing 'content' field")

def validate_shot_designs(shots, total_lines, characters):
    '''
    Checks that the shot json looks like:
    {
        "shots": [
            "character_name": string, one of: {characters}
            "coverage": [index_1, index_2, ...] # A list of int indices of the lines covered by this shot, at most length 2
            "description": string in English that includes the required elements, separated by commas
        ]
    }
    '''

    if not isinstance(shots, dict):
        raise TypeError("Shots must be a dictionary")
    
    if 'shots' not in shots or not isinstance(shots['shots'], list):
        raise ValueError("Shots must contain a 'shots' list")
    
    expected_indices = set(range(1, total_lines + 1))
    for i, shot in enumerate(shots['shots']):
        if not isinstance(shot, dict):
            raise TypeError(f"Shot {i} must be a dictionary")
        if 'character_name' not in shot or not isinstance(shot['character_name'], str):
            raise ValueError(f"Shot {i} missing 'character_name' field")
        if shot['character_name'] not in characters:
            raise ValueError(f"Shot {i} character '{shot['character_name']}' not in characters list")
        if 'description' not in shot or not isinstance(shot['description'], str):
            raise ValueError(f"Shot {i} missing 'description' field")
        if 'coverage' not in shot or not isinstance(shot['coverage'], list):
            raise ValueError(f"Shot {i} missing 'coverage' field")
        if len(shot['coverage']) > 3:
            raise ValueError(f"Shot {i} coverage exceeds 3 lines, got length {len(shot['coverage'])}: {shot['coverage']}")
        for idx in shot['coverage']:
            if not isinstance(idx, int):
                raise TypeError(f"Shot {i} coverage index must be an integer")
            if idx not in expected_indices:
                raise ValueError(f"Shot {i} coverage index {idx} out of range")
            expected_indices.remove(idx)
    if expected_indices:
        raise ValueError(f"Some lines are not covered by any shot: {expected_indices}")