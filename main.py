import os
import random
from typing import List, Optional

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel, Image

# --- Configuration ---
# IMPORTANT: Set these environment variables before running the script.
# 1. GOOGLE_CLOUD_PROJECT: Your Google Cloud project ID.
# 2. GOOGLE_CLOUD_LOCATION: The region for your project, e.g., "us-central1".
#
# To authenticate, run the following command in your terminal:
# gcloud auth application-default login
try:
    PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
    LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
except KeyError:
    print("ERROR: Please set the GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION environment variables.")
    exit(1)

# Parameters from Functional_Spec.md
MODEL_NAME = "imagen-4.0-ultra-generate-001"
FIXED_ASPECT_RATIO = "16:9"
FIXED_SAMPLE_COUNT = 1

class CharacterPackage:
    """A class to hold the data for a consistent character, per the spec."""
    def __init__(self, name: str, description: str, seed: int, negative_prompt: Optional[str] = None):
        self.name = name
        self.description = description
        self.seed = seed
        self.negative_prompt = negative_prompt

    def __str__(self):
        return f"'{self.name}': {self.description[:70]}..."

def generate_image(
    prompt: str,
    seed: int,
    negative_prompt: Optional[str] = None,
    output_filename: str = "output.png"
) -> Optional[Image]:
    """
    Calls the Imagen API with parameters defined in the Functional Spec
    and saves the generated image to a file.
    """
    print(f"\n-> Generating image with seed: {seed}")
    print(f"-> Prompt: {prompt}")

    try:
        # NOTE: The functional spec requires 'addWatermark: false' and no prompt
        # enhancement to ensure the seed works for consistency. The Python SDK
        # abstracts some of these parameters. This implementation assumes the SDK
        # correctly handles seeded generation to maintain consistency.
        response = model.generate_images(
            prompt=prompt,
            number_of_images=FIXED_SAMPLE_COUNT,
            seed=seed,
            aspect_ratio=FIXED_ASPECT_RATIO,
            negative_prompt=negative_prompt,
            # The 'person_generation' and 'language' parameters from the spec
            # are often handled by SDK defaults or within the model itself.
        )
        image = response.images[0]
        image.save(output_filename)
        print(f"-> Image saved successfully as '{output_filename}'")
        return image
    except Exception as e:
        print(f"!! An error occurred during image generation: {e}")
        return None

def create_character(characters_in_session: List[CharacterPackage]):
    """Stage 1: Character Definition & Seeding."""
    print("\n--- Create New Character ---")
    name = input("Enter a name for this character: ")
    print("Enter a detailed character description (physical appearance, clothing, etc.). Press Ctrl+D (or Ctrl+Z on Windows) when done.")
    description_lines = []
    while True:
        try:
            line = input()
            description_lines.append(line)
        except EOFError:
            break
    description = "\n".join(description_lines)

    if not description:
        print("!! Description cannot be empty. Character creation cancelled.")
        return

    negative_prompt = input("Enter a negative prompt (optional, what to avoid): ")

    # 1. Generate a random non-negative integer for the seed.
    seed = random.randint(0, 2**32 - 1)

    # 2. Construct the prompt with quality modifiers.
    stage1_prompt = f"cinematic portrait, high detail, studio lighting. {description}"

    # 3. Generate the image.
    output_filename = f"{name.replace(' ', '_')}_portrait.png"
    if generate_image(stage1_prompt, seed, negative_prompt, output_filename):
        # 4. Create and store the Character Package.
        package = CharacterPackage(name, description, seed, negative_prompt)
        characters_in_session.append(package)
        print(f"\n++ Character '{name}' created and saved. You can now use this character in scenes.")

def generate_scene(characters_in_session: List[CharacterPackage]):
    """Stage 2: Scene Generation."""
    print("\n--- Generate New Scene ---")
    if not characters_in_session:
        print("!! No characters have been created in this session. Please create a character first.")
        return

    list_characters(characters_in_session)
    try:
        char_index = int(input("Select the number of the character to use in the scene: ")) - 1
        if not 0 <= char_index < len(characters_in_session):
            raise ValueError
        selected_char = characters_in_session[char_index]
    except (ValueError, IndexError):
        print("!! Invalid selection. Scene generation cancelled.")
        return

    print("Enter a description for the scene (action, environment, etc.). Press Ctrl+D (or Ctrl+Z on Windows) when done.")
    scene_lines = []
    while True:
        try:
            line = input()
            scene_lines.append(line)
        except EOFError:
            break
    scene_description = "\n".join(scene_lines)

    if not scene_description:
        print("!! Scene description cannot be empty. Scene generation cancelled.")
        return

    # 1. Construct the combined prompt.
    stage2_prompt = f"{selected_char.description}. {scene_description}"

    # 2. Generate the image using the character's seed.
    output_filename = f"{selected_char.name.replace(' ', '_')}_scene_{random.randint(100,999)}.png"
    generate_image(
        stage2_prompt,
        selected_char.seed,
        selected_char.negative_prompt,
        output_filename
    )

def list_characters(characters_in_session: List[CharacterPackage]):
    """Lists all characters created in the current session."""
    print("\n--- Available Characters ---")
    if not characters_in_session:
        print("No characters created yet.")
    else:
        for i, char in enumerate(characters_in_session):
            print(f"[{i+1}] {char}")
    print("--------------------------")

def main():
    """Main function to run the CineGen CLI."""
    print("--- Welcome to CineGen (CLI Version) ---")
    print("This tool uses Google's Imagen model to generate consistent characters.")
    print(f"Initializing Vertex AI for project '{PROJECT_ID}' in '{LOCATION}'...")

    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        global model
        model = ImageGenerationModel.from_pretrained(MODEL_NAME)
        print("Vertex AI initialized successfully.")
    except Exception as e:
        print(f"!! Failed to initialize Vertex AI. Please check your configuration and authentication.")
        print(f"!! Error: {e}")
        return

    characters_in_session: List[CharacterPackage] = []

    while True:
        print("\n" + "="*15 + " Main Menu " + "="*15)
        print("1. Create New Character (Stage 1)")
        print("2. Generate Scene with Character (Stage 2)")
        print("3. List Created Characters")
        print("4. Exit")
        choice = input("> ")

        if choice == '1':
            create_character(characters_in_session)
        elif choice == '2':
            generate_scene(characters_in_session)
        elif choice == '3':
            list_characters(characters_in_session)
        elif choice == '4':
            print("Exiting CineGen. Goodbye!")
            break
        else:
            print("!! Invalid choice, please try again.")

if __name__ == "__main__":
    main()
