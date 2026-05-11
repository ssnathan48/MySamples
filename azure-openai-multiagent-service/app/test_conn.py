import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

try:
    print("🔄 Connecting via API Key (Direct Path)...")

    # Clean the endpoint URL
    raw_endpoint = os.getenv("AI_FOUNDRY_ENDPOINT")
    base_endpoint = raw_endpoint.split("/api")[0]

    # Initialize with API Key - This bypasses all "Scope" errors
    client = AzureOpenAI(
        azure_endpoint=base_endpoint,
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-05-01-preview"
    )

    response = client.chat.completions.create(
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        messages=[{"role": "user", "content": "Hello! Connection test."}]
    )
    
    print("✅ SUCCESS:", response.choices[0].message.content)

except Exception as e:
    print(f"❌ FAILED: {str(e)}")
