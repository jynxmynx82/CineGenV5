import os
import random
import base64
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel, Image
import google.generativeai as genai

# --- Configuration ---
# IMPORTANT: Set these environment variables before running the script.
# 1. GOOGLE_CLOUD_PROJECT: Your Google Cloud project ID.
# 2. GOOGLE_CLOUD_LOCATION: The region for your project, e.g., "us-central1".
# 3. GOOGLE_API_KEY: Your Google API key for Gemini (optional, for reference image analysis).
#
# To authenticate, run the following command in your terminal:
# gcloud auth application-default login
try:
    PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
    LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
except KeyError:
    print("ERROR: Please set the GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION environment variables.")
    exit(1)

# Check for Google API key (optional, only needed for reference image analysis)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("⚠️  Note: GOOGLE_API_KEY not set. Reference image analysis will not be available.")
    print("   To enable it, set the GOOGLE_API_KEY environment variable.")

# Parameters from Functional_Spec.md
MODEL_NAME = "imagen-4.0-ultra-generate-001"
FIXED_ASPECT_RATIO = "16:9"
FIXED_SAMPLE_COUNT = 1

# Gemini configuration for image analysis
GEMINI_MODEL = "gemini-2.0-flash-exp"
MAX_IMAGE_SIZE_MB = 10
MAX_CHARACTERS_PER_IMAGE = 2

class CharacterPackage:
    """A class to hold the data for a consistent character, per the spec."""
    def __init__(self, name: str, description: str, seed: int, negative_prompt: Optional[str] = None):
        self.name = name
        self.description = description
        self.seed = seed
        self.negative_prompt = negative_prompt

    def __str__(self):
        return f"'{self.name}': {self.description[:70]}..."

def validate_character_name(name: str) -> tuple[bool, str]:
    """Validate character name and return (is_valid, error_message)"""
    if not name or not name.strip():
        return False, "Character name cannot be empty"
    
    name = name.strip()
    if len(name) > 50:
        return False, "Character name too long (max 50 characters)"
    
    # Check for invalid characters that could cause file system issues
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\t']
    for char in invalid_chars:
        if char in name:
            return False, f"Character name contains invalid character: '{char}'"
    
    # Check for reserved names
    reserved_names = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 
                     'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 
                     'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'}
    if name.lower() in reserved_names:
        return False, "Character name is a reserved system name"
    
    return True, ""

def validate_description(description: str) -> tuple[bool, str]:
    """Validate description and return (is_valid, error_message)"""
    if not description or not description.strip():
        return False, "Description cannot be empty"
    
    description = description.strip()
    if len(description) < 10:
        return False, "Description too short (minimum 10 characters)"
    
    if len(description) > 1000:
        return False, "Description too long (max 1000 characters)"
    
    # Check for excessive repetition
    words = description.split()
    if len(words) > 0:
        word_count = {}
        for word in words:
            word_lower = word.lower()
            word_count[word_lower] = word_count.get(word_lower, 0) + 1
            if word_count[word_lower] > 5:
                return False, "Description contains too much repetition"
    
    return True, ""

def validate_negative_prompt(negative_prompt: str) -> tuple[bool, str]:
    """Validate negative prompt and return (is_valid, error_message)"""
    if not negative_prompt or not negative_prompt.strip():
        return True, ""  # Empty negative prompt is valid
    
    negative_prompt = negative_prompt.strip()
    if len(negative_prompt) > 500:
        return False, "Negative prompt too long (max 500 characters)"
    
    return True, ""

def show_validation_help(input_type: str):
    """Show helpful tips for validation errors."""
    help_tips = {
        "character_name": [
            "💡 Character name tips:",
            "   • Use 1-50 characters",
            "   • Avoid special characters: / \\ : * ? \" < > |",
            "   • Use letters, numbers, spaces, and common punctuation",
            "   • Examples: 'John Smith', 'Agent 007', 'Dr. Watson'"
        ],
        "description": [
            "💡 Description tips:",
            "   • Use 10-1000 characters",
            "   • Be specific about physical features",
            "   • Include clothing and distinctive characteristics",
            "   • Avoid excessive repetition",
            "   • Examples: 'Tall woman with long red hair, green eyes, wearing a black leather jacket'"
        ],
        "negative_prompt": [
            "💡 Negative prompt tips:",
            "   • Use 1-500 characters",
            "   • Describe what you DON'T want",
            "   • Examples: 'blurry, low quality, cartoon style, text'",
            "   • Leave empty if not needed"
        ]
    }
    
    if input_type in help_tips:
        for tip in help_tips[input_type]:
            print(tip)

def setup_output_directories() -> str:
    """Create organized directories for outputs and return the session directory path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = f"cinegen_session_{timestamp}"
    
    # Create main session directory
    os.makedirs(session_dir, exist_ok=True)
    
    # Create subdirectories
    characters_dir = os.path.join(session_dir, "characters")
    scenes_dir = os.path.join(session_dir, "scenes")
    
    os.makedirs(characters_dir, exist_ok=True)
    os.makedirs(scenes_dir, exist_ok=True)
    
    return session_dir

def get_session_info(session_dir: str) -> Dict[str, Any]:
    """Get information about the current session."""
    characters_dir = os.path.join(session_dir, "characters")
    scenes_dir = os.path.join(session_dir, "scenes")
    
    # Count files in each directory
    character_count = len([f for f in os.listdir(characters_dir) if f.endswith('.png')]) if os.path.exists(characters_dir) else 0
    scene_count = len([f for f in os.listdir(scenes_dir) if f.endswith('.png')]) if os.path.exists(scenes_dir) else 0
    
    return {
        "session_dir": session_dir,
        "characters_dir": characters_dir,
        "scenes_dir": scenes_dir,
        "character_count": character_count,
        "scene_count": scene_count
    }

def save_character_image(image: Image, filename: str, session_dir: str) -> str:
    """Save character image to the characters directory."""
    characters_dir = os.path.join(session_dir, "characters")
    filepath = os.path.join(characters_dir, filename)
    image.save(filepath)
    return filepath

def save_scene_image(image: Image, filename: str, session_dir: str) -> str:
    """Save scene image to the scenes directory."""
    scenes_dir = os.path.join(session_dir, "scenes")
    filepath = os.path.join(scenes_dir, filename)
    image.save(filepath)
    return filepath

def validate_image_file(file_path: str) -> tuple[bool, str]:
    """Validate image file for upload."""
    try:
        path = Path(file_path)
        if not path.exists():
            return False, "File does not exist"
        
        # Check file size (10MB limit)
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            return False, f"File too large ({file_size_mb:.1f}MB). Maximum size is {MAX_IMAGE_SIZE_MB}MB"
        
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        if path.suffix.lower() not in valid_extensions:
            return False, f"Invalid file type. Supported formats: {', '.join(valid_extensions)}"
        
        return True, "File is valid"
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for Gemini API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_reference_image(image_path: str) -> List[Dict[str, Any]]:
    """
    Use Gemini 2.0 Flash to analyze reference image for characters.
    Returns a list of character descriptions.
    """
    try:
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Encode image
        image_data = encode_image_to_base64(image_path)
        
        # Create prompt for character analysis
        prompt = f"""
        Analyze this image and extract detailed descriptions of up to {MAX_CHARACTERS_PER_IMAGE} characters.
        
        For each character, provide:
        1. Physical appearance (hair color, eye color, facial features, body type)
        2. Clothing and accessories
        3. Any distinctive features or characteristics
        
        Focus on visual details that would be useful for recreating the character in a different scene.
        Be specific and descriptive. If there are more than {MAX_CHARACTERS_PER_IMAGE} characters, focus on the most prominent ones.
        
        Format your response as a JSON array with objects containing:
        - "description": detailed character description
        - "confidence": confidence level (high/medium/low)
        
        Example format:
        [
            {{
                "description": "A tall woman with long red hair, green eyes, wearing a black leather jacket and jeans",
                "confidence": "high"
            }}
        ]
        """
        
        # Generate response
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_data}
        ])
        
        # Parse response (assuming JSON format)
        import json
        try:
            characters = json.loads(response.text)
            return characters
        except json.JSONDecodeError:
            # Fallback: try to extract descriptions from text
            print("⚠️  Could not parse JSON response, using text extraction...")
            return [{"description": response.text, "confidence": "medium"}]
            
    except Exception as e:
        print(f"❌ Error analyzing image: {e}")
        return []

def get_image_file_path() -> Optional[str]:
    """Get image file path from user input."""
    print("\n📸 REFERENCE IMAGE UPLOAD")
    print("="*50)
    print("Supported formats: JPG, PNG, WebP")
    print(f"Maximum size: {MAX_IMAGE_SIZE_MB}MB")
    print(f"Maximum characters: {MAX_CHARACTERS_PER_IMAGE}")
    print()
    
    while True:
        file_path = input("Enter the path to your reference image (or 'cancel' to go back): ").strip()
        
        if file_path.lower() == 'cancel':
            return None
            
        # Validate file
        is_valid, error_msg = validate_image_file(file_path)
        if is_valid:
            return file_path
        else:
            print(f"❌ {error_msg}")
            retry = input("Try again? (y/n): ").strip().lower()
            if retry != 'y':
                return None

def get_multiline_input(prompt_text: str) -> str:
    """
    Get multiline input in a user-friendly way.
    User types 'END' on a new line when finished.
    """
    print(prompt_text)
    print("💡 Type 'END' on a new line when you're finished describing.")
    print("📝 Start typing your description:")
    print("   (Press Enter after each line, then type 'END' on a new line)")
    lines = []
    while True:
        try:
            line = input().strip()
            if line.upper() == 'END':
                break
            if line:  # Only add non-empty lines
                lines.append(line)
        except KeyboardInterrupt:
            print("\n❌ Input cancelled. Returning to main menu.")
            return ""
    return '\n'.join(lines)

def generate_image(
    prompt: str,
    seed: int,
    negative_prompt: Optional[str] = None,
    output_filename: str = "output.png",
    session_dir: Optional[str] = None,
    image_type: str = "general"
) -> Optional[Image]:
    """
    Calls the Imagen API with parameters defined in the Functional Spec
    and saves the generated image to a file.
    """
    print(f"\n-> Generating image with seed: {seed}")
    print(f"-> Prompt: {prompt}")

    try:
        # Explicitly set required parameters for seeded generation
        # addWatermark=False is required for seed functionality
        response = model.generate_images(
            prompt=prompt,
            number_of_images=FIXED_SAMPLE_COUNT,
            seed=seed,
            aspect_ratio=FIXED_ASPECT_RATIO,
            negative_prompt=negative_prompt,
            add_watermark=False,  # Required for seed functionality
        )
        image = response.images[0]
        
        # Save image to appropriate directory if session_dir is provided
        if session_dir:
            if image_type == "character":
                filepath = save_character_image(image, output_filename, session_dir)
            elif image_type == "scene":
                filepath = save_scene_image(image, output_filename, session_dir)
            else:
                # Fallback to general save
                filepath = os.path.join(session_dir, output_filename)
                image.save(filepath)
            print(f"-> Image saved successfully as '{filepath}'")
        else:
            # Legacy behavior - save to current directory
            image.save(output_filename)
            print(f"-> Image saved successfully as '{output_filename}'")
        
        return image
    except Exception as e:
        print(f"!! An error occurred during image generation: {e}")
        return None

def create_character(characters_in_session: List[CharacterPackage], session_dir: str):
    """Stage 1: Character Definition & Seeding."""
    print("\n" + "="*50)
    print("🎭 CREATE NEW CHARACTER")
    print("="*50)
    print("This will create a character portrait and save it for use in scenes.")
    print("The character will maintain the same appearance across all future scenes.")
    print()
    
    name = input("Enter a name for this character: ").strip()
    
    # Validate character name
    is_valid, error_msg = validate_character_name(name)
    if not is_valid:
        print(f"❌ {error_msg}")
        print("💡 Try using only letters, numbers, spaces, and common punctuation.")
        return
    
    print()
    print("📝 CHARACTER DESCRIPTION:")
    print("Describe the character's physical appearance, clothing, and distinctive features.")
    print("Examples: 'A tall woman with long red hair, wearing a black leather jacket'")
    print("         'A middle-aged man with glasses, in a business suit'")
    print()
    
    # Use the new user-friendly input method
    description = get_multiline_input("Enter a detailed character description:")
    
    # Check if description was cancelled or is empty
    if not description:
        print("❌ Character creation cancelled.")
        return

    # Validate description
    is_valid, error_msg = validate_description(description)
    if not is_valid:
        print(f"❌ {error_msg}")
        show_validation_help("description")
        return

    print()
    print("🚫 NEGATIVE PROMPT (Optional):")
    print("Describe what you DON'T want in the image (e.g., 'blurry, low quality, cartoon style')")
    print("Leave empty if you don't need this.")
    negative_prompt = input("Enter a negative prompt: ").strip()
    
    # Validate negative prompt
    is_valid, error_msg = validate_negative_prompt(negative_prompt)
    if not is_valid:
        print(f"❌ {error_msg}")
        print("💡 Try a shorter negative prompt.")
        return
    
    if not negative_prompt:
        negative_prompt = None

    print()
    print("🎨 GENERATING CHARACTER PORTRAIT...")
    print("This may take a few moments. The AI is creating your character...")
    
    # 1. Generate a random non-negative integer for the seed.
    seed = random.randint(0, 2**32 - 1)

    # 2. Construct the prompt with quality modifiers.
    stage1_prompt = f"cinematic portrait, high detail, studio lighting. {description}"

    # 3. Generate the image.
    output_filename = f"{name.replace(' ', '_')}_portrait.png"
    if generate_image(stage1_prompt, seed, negative_prompt, output_filename, session_dir, "character"):
        # 4. Create and store the Character Package.
        package = CharacterPackage(name, description, seed, negative_prompt)
        characters_in_session.append(package)
        print(f"\n✅ SUCCESS! Character '{name}' created and saved.")
        print(f"📁 Portrait saved as: {output_filename}")
        print("🎬 You can now use this character in scenes from the main menu.")

def create_character_from_reference(characters_in_session: List[CharacterPackage], session_dir: str):
    """Create character from reference image using AI analysis."""
    print("\n" + "="*50)
    print("📸 CREATE CHARACTER FROM REFERENCE IMAGE")
    print("="*50)
    print("Upload a reference image and AI will analyze it to extract character descriptions.")
    print("You can then review and edit the descriptions before creating your character.")
    print()
    
    # Check if API key is available
    if not GOOGLE_API_KEY:
        print("❌ Reference image analysis is not available.")
        print("💡 To enable this feature, set the GOOGLE_API_KEY environment variable.")
        print("   You can still create characters manually using option 1.")
        return
    
    # Get image file path
    image_path = get_image_file_path()
    if not image_path:
        print("❌ Image upload cancelled.")
        return
    
    print(f"\n🔍 Analyzing image: {Path(image_path).name}")
    print("This may take a few moments...")
    
    # Analyze image
    characters = analyze_reference_image(image_path)
    
    if not characters:
        print("❌ Could not analyze the image. Please try a different image or create character manually.")
        return
    
    print(f"\n✅ Found {len(characters)} character(s) in the image:")
    print()
    
    # Display analysis results
    for i, char in enumerate(characters, 1):
        print(f"Character {i} (Confidence: {char.get('confidence', 'unknown')}):")
        print(f"  {char.get('description', 'No description available')}")
        print()
    
    # Let user select which character to create
    if len(characters) > 1:
        print("Multiple characters detected. Which one would you like to create?")
        try:
            choice = int(input(f"Enter character number (1-{len(characters)}): ")) - 1
            if not 0 <= choice < len(characters):
                print("❌ Invalid selection. Character creation cancelled.")
                return
            selected_char = characters[choice]
        except (ValueError, IndexError):
            print("❌ Invalid selection. Character creation cancelled.")
            return
    else:
        selected_char = characters[0]
    
    # Get character name
    print("\n📝 CHARACTER DETAILS")
    print("="*50)
    name = input("Enter a name for this character: ").strip()
    
    # Validate character name
    is_valid, error_msg = validate_character_name(name)
    if not is_valid:
        print(f"❌ {error_msg}")
        print("💡 Try using only letters, numbers, spaces, and common punctuation.")
        return
    
    # Show AI-generated description and allow editing
    print(f"\n🤖 AI-Generated Description:")
    print(f"  {selected_char.get('description', 'No description available')}")
    print()
    print("💡 You can edit this description to make it more detailed or accurate.")
    print("   Type 'use' to keep the AI description, or enter a new description:")
    
    edit_choice = input("Edit description? (use/edit): ").strip().lower()
    
    if edit_choice == 'use':
        description = selected_char.get('description', '')
    else:
        print("\n📝 Enter your improved character description:")
        description = get_multiline_input("Enter a detailed character description:")
    
    # Validate description
    is_valid, error_msg = validate_description(description)
    if not is_valid:
        print(f"❌ {error_msg}")
        show_validation_help("description")
        return
    
    # Get negative prompt
    print()
    print("🚫 NEGATIVE PROMPT (Optional):")
    print("Describe what you DON'T want in the image (e.g., 'blurry, low quality, cartoon style')")
    print("Leave empty if you don't need this.")
    negative_prompt = input("Enter a negative prompt: ").strip()
    
    # Validate negative prompt
    is_valid, error_msg = validate_negative_prompt(negative_prompt)
    if not is_valid:
        print(f"❌ {error_msg}")
        print("💡 Try a shorter negative prompt.")
        return
    
    if not negative_prompt:
        negative_prompt = None
    
    # Generate character portrait
    print()
    print("🎨 GENERATING CHARACTER PORTRAIT...")
    print("This may take a few moments. The AI is creating your character...")
    
    seed = random.randint(0, 2**32 - 1)
    stage1_prompt = f"cinematic portrait, high detail, studio lighting. {description}"
    output_filename = f"{name.replace(' ', '_')}_portrait.png"
    
    if generate_image(stage1_prompt, seed, negative_prompt, output_filename, session_dir, "character"):
        package = CharacterPackage(name, description, seed, negative_prompt)
        characters_in_session.append(package)
        print(f"\n✅ SUCCESS! Character '{name}' created from reference image.")
        print(f"📁 Portrait saved as: {output_filename}")
        print("🎬 You can now use this character in scenes from the main menu.")

def generate_scene(characters_in_session: List[CharacterPackage], session_dir: str):
    """Stage 2: Scene Generation."""
    print("\n" + "="*50)
    print("🎬 GENERATE NEW SCENE")
    print("="*50)
    print("This will create a scene with one of your existing characters.")
    print("The character will maintain the same appearance from their portrait.")
    print()
    
    if not characters_in_session:
        print("❌ No characters have been created in this session.")
        print("💡 Please create a character first using option 1 from the main menu.")
        return

    list_characters(characters_in_session)
    print()
    try:
        char_index = int(input("Select the number of the character to use in the scene: ")) - 1
        if not 0 <= char_index < len(characters_in_session):
            raise ValueError
        selected_char = characters_in_session[char_index]
        print(f"✅ Selected character: {selected_char.name}")
    except (ValueError, IndexError):
        print("❌ Invalid selection. Scene generation cancelled.")
        return

    print()
    print("📝 SCENE DESCRIPTION:")
    print("Describe what the character is doing and the environment they're in.")
    print("Examples: 'Standing in a busy city street at night'")
    print("         'Sitting at a café table, reading a book'")
    print("         'Running through a forest during sunset'")
    print()
    
    # Use the new user-friendly input method
    scene_description = get_multiline_input("Enter a description for the scene:")

    # Validate scene description
    is_valid, error_msg = validate_description(scene_description)
    if not is_valid:
        print(f"❌ {error_msg}")
        show_validation_help("description")
        return

    print()
    print("🎨 GENERATING SCENE...")
    print("This may take a few moments. The AI is creating your scene...")
    
    # 1. Construct the combined prompt.
    stage2_prompt = f"{selected_char.description}. {scene_description}"

    # 2. Generate the image using the character's seed.
    output_filename = f"{selected_char.name.replace(' ', '_')}_scene_{random.randint(100,999)}.png"
    if generate_image(
        stage2_prompt,
        selected_char.seed,
        selected_char.negative_prompt,
        output_filename,
        session_dir,
        "scene"
    ):
        print(f"\n✅ SUCCESS! Scene generated with {selected_char.name}.")
        print(f"📁 Scene saved as: {output_filename}")
        print("🎬 You can create more scenes with this character or create new characters.")

def list_characters(characters_in_session: List[CharacterPackage], session_dir: str = None):
    """Lists all characters created in the current session."""
    print("\n" + "="*50)
    print("👥 AVAILABLE CHARACTERS")
    print("="*50)
    if not characters_in_session:
        print("📭 No characters created yet.")
        print("💡 Create your first character using option 1 from the main menu.")
    else:
        print(f"📋 Found {len(characters_in_session)} character(s) in this session:")
        print()
        for i, char in enumerate(characters_in_session):
            print(f"[{i+1}] {char}")
        print()
        print("💡 Use these characters in scenes with option 3 from the main menu.")
    
    # Show session information if available
    if session_dir:
        session_info = get_session_info(session_dir)
        print()
        print("📁 SESSION INFO:")
        print(f"   Session: {os.path.basename(session_dir)}")
        print(f"   Characters: {session_info['character_count']} images")
        print(f"   Scenes: {session_info['scene_count']} images")
        print(f"   Location: {session_dir}")
    
    print("="*50)

def main():
    """Main function to run the CineGen CLI."""
    print("=" * 60)
    print("🎬 Welcome to CineGen (CLI Version) 🎬")
    print("=" * 60)
    print("This tool helps you create consistent cinematic characters and scenes")
    print("using Google's Imagen 4.0 AI model.")
    print()
    print("📋 HOW IT WORKS:")
    print("1. First, create a character with a detailed description")
    print("2. Then, generate scenes with that character in different situations")
    print("3. The character will maintain visual consistency across all scenes")
    print()
    print("💡 TIP: Be specific in your descriptions for better results!")
    print("=" * 60)
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
    
    # Set up organized output directories for this session
    session_dir = setup_output_directories()
    print(f"📁 Session directory created: {session_dir}")
    print("   ├── characters/ (character portraits)")
    print("   └── scenes/ (generated scenes)")

    while True:
        print("\n" + "="*50)
        print("🎬 MAIN MENU")
        print("="*50)
        print("1. 🎭 Create New Character (Stage 1)")
        print("2. 📸 Create Character from Reference Image")
        print("3. 🎬 Generate Scene with Character (Stage 2)")
        print("4. 👥 List Created Characters")
        print("5. 🚪 Exit")
        print("="*50)
        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            create_character(characters_in_session, session_dir)
        elif choice == '2':
            create_character_from_reference(characters_in_session, session_dir)
        elif choice == '3':
            generate_scene(characters_in_session, session_dir)
        elif choice == '4':
            list_characters(characters_in_session, session_dir)
        elif choice == '5':
            print("\n👋 Thank you for using CineGen!")
            print(f"🎬 Your generated images are saved in: {session_dir}")
            print("   ├── characters/ (character portraits)")
            print("   └── scenes/ (generated scenes)")
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
