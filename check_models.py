import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    # --- Configure the Google API Key ---
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in .env file. Please check your configuration.")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    
    print("--- Successfully configured API key. ---")
    print("Checking for available models that support 'generateContent'...\n")
    
    # --- List Available Models ---
    available_models = []
    for m in genai.list_models():
      # Check if the model supports the 'generateContent' method
      if 'generateContent' in m.supported_generation_methods:
        available_models.append(m.name)

    if available_models:
        print("✅ Your API key has access to the following models:")
        for model_name in available_models:
            print(f"   - {model_name}")
        print("\nPlease copy one of these model names (e.g., 'models/gemini-pro') and use it in your src/graph/nodes.py file.")
    else:
        print("❌ Your API key is valid, but it does not have access to any models that support 'generateContent'.")
        print("This usually means the 'Generative Language API' is not enabled in your Google Cloud project.")

except Exception as e:
    print(f"\n--- An error occurred ---")
    print(f"Error: {e}")
    print("\nThis likely means your API key is invalid or your Google Cloud project is not configured correctly.")
    print("Please double-check your API key and ensure the Generative Language API is enabled in the Google Cloud Console.")
