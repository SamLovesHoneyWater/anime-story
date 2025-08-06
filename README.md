# anime-story

Exploring AI generated content

## Geting Started

1. Install dependencies
2. Create .env file and define OPENAI_API_KEY
3. Add sample.txt
4. Run experiment.py

    i. When prompted, edit the latest character_features json file. Enter the the gender each character should sound like (M/F)

    ii. Also add visual descriptions for each character except the narrator. It should look like this:
        "description": "(very handsome), (man), (tall), (black hair), (short hair), (sharp black eyes), (cool), (slim)"
    
    Note: Character consistency is automatically enforced. To differentiate characters, change descriptions such as hair color.

5. The script will generate voiceover with Edge TTS and pictures with MeinaMix_V11.
6. After all components have been generated, run produce_video.py to generate the final video.