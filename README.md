# CineGenV5 - Cinematic Character Generation Tool

A CLI application for generating consistent cinematic characters and scenes using Google's Imagen 4.0 AI model. This tool helps filmmakers and creative professionals maintain visual consistency across multiple generated images through proper seeding and prompting techniques.

## Features

- **Character Creation**: Define detailed character descriptions and generate consistent character portraits
- **Reference Image Analysis**: Upload reference images and let AI extract character descriptions automatically
- **Scene Generation**: Create scenes with previously defined characters while maintaining visual consistency
- **Seed-Based Consistency**: Uses Imagen 4.0's seeding feature to ensure character consistency across multiple generations
- **Input Validation**: Comprehensive validation for all user inputs with helpful error messages
- **Organized File Management**: Session-based directory structure with separate folders for characters and scenes
- **Fixed Cinematic Aspect Ratio**: All images generated in 16:9 widescreen format for cinematic feel
- **Session-Based Storage**: Characters are stored in memory during the session for easy reuse

## Prerequisites

- Python 3.7 or higher
- Google Cloud account with Vertex AI enabled
- Google Cloud CLI installed and authenticated
- Imagen 4.0 API access

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd CineGenV5
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud authentication:
```bash
gcloud auth application-default login
```

4. Set required environment variables:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # or your preferred region
export GOOGLE_API_KEY="your-google-api-key"  # optional, for reference image analysis
```

## Usage

Run the application:
```bash
python main.py
```

### Workflow

The application follows a two-stage process:

#### Stage 1: Character Definition & Seeding
**Option A: Manual Creation**
1. Select "Create New Character" from the main menu
2. Enter a name for your character
3. Provide a detailed description (physical appearance, clothing, etc.)
4. Optionally add a negative prompt (what to avoid)
5. The system generates a character portrait and stores the consistency seed

**Option B: Reference Image Analysis**
1. Select "Create Character from Reference Image" from the main menu
2. Upload a reference image (JPG, PNG, WebP, max 10MB)
3. AI analyzes the image and extracts character descriptions
4. Review and edit the AI-generated description
5. Enter a name and optionally add a negative prompt
6. The system generates a character portrait and stores the consistency seed

#### Stage 2: Scene Generation
1. Select "Generate Scene with Character" from the main menu
2. Choose from your created characters
3. Describe the scene (action, environment, etc.)
4. The system generates the scene using the character's stored seed for consistency

### Menu Options

- **1. Create New Character**: Define and generate a new character manually
- **2. Create Character from Reference Image**: Upload an image and let AI extract character descriptions
- **3. Generate Scene with Character**: Create scenes with existing characters
- **4. List Created Characters**: View all characters in the current session
- **5. Exit**: Close the application

## Configuration

The application uses the following fixed parameters:
- **Model**: `imagen-4.0-ultra-generate-001`
- **Aspect Ratio**: 16:9 (widescreen)
- **Sample Count**: 1 image per generation

## File Structure

```
CineGenV5/
├── main.py                 # Main application code
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── CineGen-V5-Prompt.md   # Original project specification
└── Functional_Spec.md     # Functional specification (to be completed)
```

## Generated Files

Images are organized in session-based directories with the following structure:
```
cinegen_session_YYYYMMDD_HHMMSS/
├── characters/
│   ├── {character_name}_portrait.png
│   └── ...
└── scenes/
    ├── {character_name}_scene_{random_number}.png
    └── ...
```

**File Organization:**
- **Session directories**: Each run creates a timestamped session folder
- **Character portraits**: Stored in `characters/` subdirectory
- **Scene images**: Stored in `scenes/` subdirectory
- **Easy cleanup**: Delete entire session folders to remove all related files

## Technical Details

- Uses Google Cloud Vertex AI for image generation
- Implements seed-based consistency for character continuity
- Session-based character storage (not persistent across sessions)
- CLI interface for easy automation and scripting

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure you're logged in with `gcloud auth application-default login`
2. **Project Not Found**: Verify your `GOOGLE_CLOUD_PROJECT` environment variable is correct
3. **API Access Denied**: Ensure your project has Imagen 4.0 API enabled
4. **Region Issues**: Check that your `GOOGLE_CLOUD_LOCATION` is supported for Imagen 4.0

### Error Messages

- `ERROR: Please set the GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION environment variables.`
  - Solution: Set the required environment variables before running the script

- `!! Failed to initialize Vertex AI`
  - Solution: Check your authentication and project configuration

## Input Validation

The application includes comprehensive input validation to ensure reliable operation:

### Character Names
- **Length**: 1-50 characters
- **Characters**: Letters, numbers, spaces, and common punctuation
- **Restrictions**: No special characters that could cause file system issues
- **Reserved names**: Cannot use system-reserved names

### Descriptions
- **Length**: 10-1000 characters
- **Content**: Must be descriptive and specific
- **Repetition**: Limited to prevent excessive word repetition
- **Examples**: Physical features, clothing, distinctive characteristics

### Negative Prompts
- **Length**: 1-500 characters (optional)
- **Purpose**: Describe what you DON'T want in the image
- **Examples**: "blurry, low quality, cartoon style"

### Reference Images
- **Formats**: JPG, PNG, WebP
- **Size**: Maximum 10MB
- **Characters**: Maximum 2 people per image

## Limitations

- Characters are only stored in memory during the session
- No persistent storage between sessions
- Fixed aspect ratio (16:9) for all images
- Single image generation per request
- Requires active internet connection for API calls

## Future Enhancements

- Persistent character storage
- Multiple aspect ratio support
- Batch image generation
- Web interface
- Character template library
- Advanced prompt management

## Contributing

This is a prototype application. Contributions are welcome for:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Testing and validation

## License

[Add your license information here]

## Support

For issues and questions, please refer to the Google Cloud Vertex AI documentation or create an issue in this repository.
