Hello Gemini. Your task is to act as a systems architect. We will design the complete functional specification for a new application. Read this entire brief and all provided reference material carefully.

Your final output for this prompt should be a detailed "Functional Specification Document." Do not generate any code.

\*\*1. PROJECT BRIEF\*\*

\* \*\*Project Name:\*\* "CineGen"  
\* \*\*Objective:\*\* To design a stable and reliable tool for filmmakers and creative professionals. The tool's primary function is to provide a predictable workflow for generating cinematically consistent characters and environments using Google's Imagen 4 model.  
\* \*\*Core Challenge:\*\* The system must solve for visual consistency across multiple generated images by correctly implementing a specific set of prompting techniques. It must be designed to mitigate issues like "style bias" and "prompt drift."  
\* \*\*Key Principles of Operation:\*\*  
    \* \*\*Character & Scene Consistency:\*\* This is the foremost priority. The application's architecture and user flow must be built from the ground up to support the generation of the same character and environment across multiple distinct images.  
    \* \*\*Architectural Stability:\*\* The application must be architecturally simple and robust. The connection between user input and the final image should be as direct and reliable as possible, minimizing unexpected variations or errors.  
    \* \*\*Stateless Operation:\*\* The application must not rely on user accounts or long-term data storage. All information required for consistency must be managed within a single, active user session.  
    \* \*\*Secure API Key Management:\*\* The system must be designed such that the Google Cloud API key is never exposed to the end-user or in any publicly accessible component.  
    \* \*\*Fixed Aspect Ratio:\*\* For the initial version of this tool, all generated images will have a fixed widescreen aspect ratio of 16:9 to maintain a consistent cinematic feel.

\*\*2. USER FLOW PRINCIPLE\*\*

The application's workflow must follow a strict two-stage process to ensure stability and predictability:

\* \*\*Stage 1: Character Definition & Seeding.\*\* A user finalizes a character's description using a set of detailed inputs. The system then performs a single call to the image generation model to create a definitive character portrait. From this initial generation, the system \*\*must\*\* capture and store a "consistency seed" value for the session. This "Character Package" (the user's textual description \+ the captured consistency seed) becomes the single source of truth for that character.  
\* \*\*Stage 2: Scene Generation.\*\* The user selects a saved "Character Package" and describes a new scene. The system then performs subsequent calls to the image generation model, always reusing the original character's textual description and the captured consistency seed to ensure the character remains visually consistent across different shots.

\*\*3. REFERENCE DOCUMENTATION: IMAGEN 4 API & PROMPTING GUIDE\*\*

The system's logic must be built around the specifications and best practices detailed in the following documents. All generated prompts must adhere to these guidelines.

\---  
START  
\[REFERENCE DOCUMENTATION: Imagen 4 API\]

\*\*\#\# Supported Models\*\*  
The system will target the \`imagen-4.0-ultra-generate-001\` model. \[cite\_start\]Other available models include \`imagen-4.0-generate-001\` and \`imagen-4.0-fast-generate-001\`\[cite: 5\].

\*\*\#\# API Parameters (Image Generation)\*\*

\* \*\*prompt\*\* (\`string\`): Required. \[cite\_start\]The text prompt describing the desired image\[cite: 9\].  
\* \*\*sampleCount\*\* (\`int\`): Required. The number of images to generate. \[cite\_start\]The default is 4, but the accepted value for our target model is 1-4\[cite: 53, 54\].  
\* \*\*seed\*\* (\`Uint32\`): Optional. \[cite\_start\]A non-negative integer used to make image output deterministic\[cite: 80\]. \[cite\_start\]Providing the same seed and prompt will result in the same image\[cite: 81\].  
    \* \[cite\_start\]\*\*CRITICAL:\*\* This parameter is unavailable if \`addWatermark\` is set to \`true\`\[cite: 27, 82\].  
    \* \[cite\_start\]\*\*CRITICAL:\*\* This parameter will not work if \`enhancePrompt\` is set to \`true\`\[cite: 28\].  
\* \*\*enhancePrompt\*\* (\`boolean\`): Optional. \[cite\_start\]Uses an LLM to rewrite the user's prompt for higher quality and better adherence\[cite: 12, 64\]. \[cite\_start\]The default is \`true\`\[cite: 65\].  
    \* \[cite\_start\]Note: For the \`imagen-4.0-fast-generate-001\` model, complex prompts with this feature enabled may produce undesirable results\[cite: 6\].  
\* \*\*negativePrompt\*\* (\`string\`): Optional. \[cite\_start\]A description of what to discourage in the generated images\[cite: 17\].  
    \* Note: The documentation states this is not supported by \`imagen-3.0-generate-002\` and newer models, which implies it may not work with Imagen 4\. This must be tested.  
\* \*\*aspectRatio\*\* (\`string\`): Optional. The aspect ratio for the image. \[cite\_start\]The default is "1:1"\[cite: 11\]. \[cite\_start\]Supported values include "1:1", "3:4", "4:3", "16:9", and "9:16"\[cite: 63\].  
\* \*\*addWatermark\*\* (\`bool\`): Optional. \[cite\_start\]Adds an invisible watermark to the generated images\[cite: 59\]. \[cite\_start\]The default is \`true\`\[cite: 10, 60\]. \[cite\_start\]Must be set to \`false\` to enable the use of the \`seed\` parameter\[cite: 61, 62\].  
\* \*\*personGeneration\*\* (\`string\`): Optional. \[cite\_start\]A safety setting to control the generation of people\[cite: 19\].  
    \* \[cite\_start\]Values: \`"dont\_allow"\`, \`"allow\_adult"\` (default), \`"allow\_all"\`\[cite: 19, 20, 74\].  
\* \*\*safetySetting\*\* (\`string\`): Optional. \[cite\_start\]Controls the level of safety filtering\[cite: 21, 75\]. \[cite\_start\]The default is \`"block\_medium\_and\_above"\`\[cite: 25, 77\].  
\* \*\*storageUri\*\* (\`string\`): Optional. A Cloud Storage URI to store the generated images. \[cite\_start\]If not provided, images are returned as base64-encoded bytes\[cite: 29, 84\].  
\* \*\*language\*\* (\`string\`): Optional. \[cite\_start\]The language of the prompt\[cite: 13\]. \[cite\_start\]Can be set to "auto" for automatic detection and translation to English\[cite: 14\].  
\* \*\*outputOptions\*\* (\`object\`): Optional. \[cite\_start\]An object that describes the output image format, including \`mimeType\` ("image/png" or "image/jpeg") and \`compressionQuality\`\[cite: 18, 30, 31, 32, 33\].

\*\*\#\# Response Body\*\*  
\[cite\_start\]The API response will be a JSON object containing a \`predictions\` array\[cite: 34\]. Each object in the array represents a generated image and contains:  
\* \[cite\_start\]\`bytesBase64Encoded\`: The base64 encoded image string\[cite: 37\].  
\* \[cite\_start\]\`mimeType\`: The MIME type of the generated image\[cite: 38\].  
\* \`prompt\`: If \`enhancePrompt\` was used, this field will contain the rewritten prompt used by the model.  
END

\---  
START  
\[REFERENCE DOCUMENTATION: Prompt and Image Attribute Guide\]

\*\*\#\# Prompt Writing Basics\*\*

\[cite\_start\]Good prompts are descriptive and clear, though they don't need to be long or complex\[cite: 114\]. \[cite\_start\]A good starting point is to think of three main components\[cite: 115\]:  
\* \[cite\_start\]\*\*Subject:\*\* The main object, person, animal, or scenery in the image\[cite: 122\].  
\* \[cite\_start\]\*\*Context and Background:\*\* The environment where the subject is placed\[cite: 123\].  
\* \[cite\_start\]\*\*Style:\*\* The desired artistic style, such as a photograph, painting, sketch, or a more specific style like charcoal drawing or isometric 3D\[cite: 125, 126\].

\*\*\#\# The Importance of Iteration\*\*

\[cite\_start\]The best results come from an iterative process\[cite: 128\]. \[cite\_start\]Start with a core idea and then progressively add more details to the prompt until the generated image matches your vision\[cite: 128, 134\].  
\* \*Example Progression:\*  
    \* \[cite\_start\]\`A park in the spring next to a lake\` \[cite: 129\]  
    \* \[cite\_start\]\`A park in the spring next to a lake, the sun sets across the lake, golden hour\` \[cite: 129, 130\]  
    \* \[cite\_start\]\`A park in the spring next to a lake, the sun sets across the lake, golden hour, red wildflowers\` \[cite: 131\]

\*\*\#\# Generating Text in Images\*\*

Imagen has the ability to render text within images. \[cite\_start\]Key guidance for this feature includes\[cite: 149\]:  
\* \[cite\_start\]\*\*Keep it short:\*\* For best results, limit text to 25 characters or less\[cite: 153\].  
\* \[cite\_start\]\*\*Use multiple phrases:\*\* You can experiment with two or three distinct phrases, but avoid more than three\[cite: 154, 155\].  
\* \[cite\_start\]\*\*Guide placement:\*\* You can suggest text placement, but expect variations\[cite: 158\].  
\* \[cite\_start\]\*\*Inspire font style:\*\* Suggest a general font style (e.g., "bold font") to influence the creative interpretation\[cite: 157, 160, 161\].  
\* \[cite\_start\]\*\*Suggest font size:\*\* Indicate a general size like small, medium, or large\[cite: 162\].

\*\*\#\# Prompt Parameterization\*\*

To control outputs systematically, prompts can be parameterized. \[cite\_start\]This involves using a template with placeholders that are filled in by user selections\[cite: 164, 165\].  
\* \*Example Template:\* \`A {logo\_style} logo for a {company\_area} company on a solid color background. \[cite\_start\]Include the text {company\_name}.\` \[cite: 168\]

\*\*\#\# Advanced Prompting Techniques\*\*

\*\*\#\#\# Style Modifiers\*\*  
\* \[cite\_start\]\*\*Photography:\*\* To get a photographic style, start the prompt with "A photo of..."\[cite: 187, 188\].  
\* \[cite\_start\]\*\*Illustration and Art:\*\* To get artistic styles, start with phrases like "A painting of..." or "A sketch of..."\[cite: 195\].

\[cite\_start\]\*\*\#\#\# Photography-Specific Modifiers\*\* \[cite: 208, 209\]  
\* \[cite\_start\]\*\*Camera Proximity:\*\* Use terms like \`Close up\` or \`taken from far away\`\[cite: 210\].  
\* \[cite\_start\]\*\*Camera Position:\*\* Use terms like \`aerial\` or \`from below\`\[cite: 213\].  
\* \[cite\_start\]\*\*Lighting:\*\* Use descriptive words for lighting, such as \`natural\`, \`dramatic\`, \`warm\`, or \`cold\`\[cite: 216\].  
\* \[cite\_start\]\*\*Camera Settings:\*\* Include terms like \`motion blur\`, \`soft focus\`, or \`bokeh\`\[cite: 219\].  
\* \[cite\_start\]\*\*Lens Types:\*\* Specify lens types, for example \`35mm\`, \`fisheye\`, or \`macro\`\[cite: 222\].  
\* \[cite\_start\]\*\*Film Types:\*\* Include film styles like \`black and white\` or \`polaroid\`\[cite: 226\].

\*\*\#\#\# Shapes and Materials\*\*  
\* \[cite\_start\]You can specify materials and shapes using phrases like "...made of..." or "...in the shape of..."\[cite: 231\].  
\* \[cite\_start\]\*Example:\* \`an armchair made of paper, studio photo, origami style\`\[cite: 236\].

\*\*\#\#\# Historical Art References\*\*  
\* \[cite\_start\]Reference historical art movements or periods by including "...in the style of..."\[cite: 239\].  
\* \[cite\_start\]\*Example:\* \`generate an image in the style of an impressionist painting: a wind farm\`\[cite: 242\].

\*\*\#\#\# Image Quality Modifiers\*\*  
\* \[cite\_start\]To signal that a high-quality asset is desired, use certain keywords\[cite: 247\].  
\* \[cite\_start\]\*\*General:\*\* \`high-quality\`, \`beautiful\`, \`stylized\`\[cite: 249\].  
\* \[cite\_start\]\*\*Photos:\*\* \`4K\`, \`HDR\`, \`Studio Photo\`\[cite: 250\].  
\* \[cite\_start\]\*\*Art/Illustration:\*\* \`by a professional\`, \`detailed\`\[cite: 251\].

\*\*\#\# Negative Prompts\*\*  
\[cite\_start\]A negative prompt can be used to describe elements you want to omit from the image\[cite: 275, 277\].  
\* \[cite\_start\]\*\*Recommended:\*\* Plainly describe what you don't want (e.g., \`greenery, plants, forest\`)\[cite: 278, 284\].  
\* \[cite\_start\]\*\*Not Recommended:\*\* Avoid instructive language like "no" or "don't" (e.g., "no walls" or "don't show walls")\[cite: 279, 280\].

\*\*\#\# Guidelines for Photorealistic Images\*\*

\* \[cite\_start\]\*\*Use Case: People (Portraits)\*\* \[cite: 292\]  
    \* \[cite\_start\]\*\*Lens Type:\*\* Prime, zoom \[cite: 292\]  
    \* \[cite\_start\]\*\*Focal Lengths:\*\* 24-35mm \[cite: 292\]  
    \* \[cite\_start\]\*\*Additional Details:\*\* black and white film, Film noir, Depth of field, duotone \[cite: 292\]  
\* \[cite\_start\]\*\*Use Case: Food, insects, plants (Objects, still life)\*\* \[cite: 300\]  
    \* \[cite\_start\]\*\*Lens Type:\*\* Macro \[cite: 300\]  
    \* \[cite\_start\]\*\*Focal Lengths:\*\* 60-105mm \[cite: 300\]  
    \* \[cite\_start\]\*\*Additional Details:\*\* High detail, precise focusing, controlled lighting \[cite: 300\]  
\* \[cite\_start\]\*\*Use Case: Sports, wildlife (Motion)\*\* \[cite: 305\]  
    \* \[cite\_start\]\*\*Lens Type:\*\* Telephoto zoom \[cite: 305\]  
    \* \[cite\_start\]\*\*Focal Lengths:\*\* 100-400mm \[cite: 305\]  
    \* \[cite\_start\]\*\*Additional Details:\*\* Fast shutter speed, Action or movement tracking \[cite: 305\]  
\* \[cite\_start\]\*\*Use Case: Astronomical, landscape (Wide-angle)\*\* \[cite: 293\]  
    \* \[cite\_start\]\*\*Lens Type:\*\* Wide-angle \[cite: 293\]  
    \* \[cite\_start\]\*\*Focal Lengths:\*\* 10-24mm \[cite: 293\]  
    \* \[cite\_start\]\*\*Additional Details:\*\* Long exposure times, sharp focus, smooth water or clouds \[cite: 293\]

\*\*\#\# Aspect Ratios\*\*  
\[cite\_start\]Imagen allows for five distinct aspect ratios\[cite: 257\]:  
\* \[cite\_start\]\*\*Square (1:1):\*\* The default, common for social media posts\[cite: 258\].  
\* \[cite\_start\]\*\*Fullscreen (4:3):\*\* Commonly used in film and photography\[cite: 259, 261\].  
\* \[cite\_start\]\*\*Portrait Fullscreen (3:4):\*\* Captures more verticality than 1:1\[cite: 264\].  
\* \[cite\_start\]\*\*Widescreen (16:9):\*\* The most common ratio for modern TVs and monitors; good for landscapes\[cite: 267, 268\].  
\* \[cite\_start\]\*\*Portrait (9:16):\*\* Tall ratio popularized by short-form video, good for vertical objects like skyscrapers\[cite: 270, 271, 272\].  
END  
\---

\*\*4. YOUR TASK: GENERATE THE FUNCTIONAL SPECIFICATION\*\*

Based on all the information above, please generate a "Functional Specification Document" for the "CineGen" application. The document should have the following sections:

\* \*\*Section 1: Core User Interface Components.\*\* Describe the necessary UI elements in abstract terms. Do not describe styling. (e.g., "An input area for defining character details like facial features and wardrobe," "A button to initiate the initial character generation and seed capture," "A display area for generated images," "An input for scene descriptions," "A toggle to enable or disable the 'enhance prompt' feature.").  
    \* Note: There will be no user-facing option to change the aspect ratio. This parameter is fixed for the initial build.

\* \*\*Section 2: Data Flow Logic.\*\* Describe the step-by-step flow of data through the system.  
    \* Example: "1. The user provides inputs for the 'Character Definition'. 2\. The system constructs a prompt based on the 'Master Cinematic Prompt' structure. 3\. The system makes a call to the \`imagen-4.0-ultra-generate-001\` model. 4\. The system receives the image and captures the \`seed\` value from the response..." and so on for the entire user flow.

\* \*\*Section 3: API Call Parameter Map.\*\* Create a list or table detailing which user inputs and system-managed values (like the seed) map to which specific parameters in the Imagen 4 API call. Refer to the provided API documentation.  
    \* \*\*aspectRatio:\*\* This parameter will be hardcoded to \`"16:9"\` for all API calls to ensure a consistent cinematic widescreen format.  
    \*(The other parameter mappings would be detailed here as well, such as prompt, seed, enhancePrompt, etc.)\*  
