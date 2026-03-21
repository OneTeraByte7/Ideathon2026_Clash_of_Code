"""
Quick inline test of Gemini API
"""
import google.generativeai as genai

# Using your API key (REVOKE THIS AFTER TESTING!)
API_KEY = "AIzaSyBec2eSOh4T7KEr_iCNur64JGz-aLEPR8s"

print("=" * 60)
print("Gemini API Test - Finding Available Models")
print("=" * 60)
print()

genai.configure(api_key=API_KEY)

print("📋 Listing all available models that support generateContent:")
print()

available_models = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            model_name = m.name.replace('models/', '')
            available_models.append(model_name)
            print(f"  ✅ {model_name}")
except Exception as e:
    print(f"❌ Error listing models: {e}")
    exit(1)

print()
print("=" * 60)
print("Testing models:")
print("=" * 60)

# Try different models
test_models = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest"
]

working_model = None

for model_name in test_models:
    if model_name not in available_models:
        print(f"⏭️  {model_name} - Not in available models list, skipping")
        continue
    
    print(f"🧪 Testing: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Reply with just: Hello from Gemini!")
        print(f"   ✅ SUCCESS! Response: {response.text[:50]}")
        if not working_model:
            working_model = model_name
        print()
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        print()

print()
print("=" * 60)
print("RECOMMENDATION:")
print("=" * 60)

if working_model:
    print(f"✅ Use this model in gemini_client.py:")
    print(f'   model = genai.GenerativeModel("{working_model}")')
else:
    print("❌ No working models found!")
    print("   Available models:", ", ".join(available_models[:5]))

print()
print("⚠️  SECURITY WARNING:")
print("   IMMEDIATELY revoke this API key at:")
print("   https://aistudio.google.com/app/apikey")
print("   Then generate a new one!")
print("=" * 60)
