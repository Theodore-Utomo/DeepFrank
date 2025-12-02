"""Test script for image analysis with Claude"""
import asyncio
import sys
import base64
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from anthropic import Anthropic
from core.config import ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_TEMPERATURE, IMAGE_ANALYSIS_SYSTEM_PROMPT


async def test_image_analysis():
    """Test image analysis with a sample image"""
    # Find an image in the Data folder
    # In Docker container, Data is mounted at /app/data
    # Locally, it's at the repo root
    data_dir = Path("/app/data") if Path("/app/data").exists() else Path(__file__).parent.parent.parent / "Data"
    test_image_path = data_dir / "cat_body_parts_dataset" / "images" / "test" / "Abyssinian_10.jpg"
    
    if not test_image_path.exists():
        print(f"Image not found at: {test_image_path}")
        # Try another image
        test_image_path = data_dir / "cat_body_parts_dataset" / "images" / "test" / "Bengal_124.jpg"
        if not test_image_path.exists():
            print(f"Image not found at: {test_image_path}")
            return
    
    print(f"Testing with image: {test_image_path}")
    print(f"Claude Model: {CLAUDE_MODEL}")
    
    if not ANTHROPIC_API_KEY:
        print("\nERROR: ANTHROPIC_API_KEY not set!")
        print("Please set the ANTHROPIC_API_KEY environment variable.")
        print("You can get an API key from: https://console.anthropic.com/")
        return
    
    print("-" * 80)
    
    # Read image bytes
    with open(test_image_path, "rb") as f:
        image_bytes = f.read()
    
    print(f"Image size: {len(image_bytes)} bytes")
    print("Converting to base64...")
    
    # Convert image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    print("Initializing Claude client...")
    
    # Initialize Claude client
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    print("Calling Claude API for analysis...")
    print("-" * 80)
    
    try:
        # Call Claude API with vision
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            temperature=CLAUDE_TEMPERATURE,
            system=IMAGE_ANALYSIS_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please analyze this cat image and provide the body language analysis."
                        }
                    ]
                }
            ]
        )
        
        # Extract text from response
        response_text = message.content[0].text
        
        print("\n=== ANALYSIS RESULT ===")
        print(response_text)
        print("=" * 80)
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_image_analysis())
