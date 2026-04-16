import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory

async def test_azure_connection():
    load_dotenv(override=True)
    
    # 1. Check Env Vars
    required_vars = ["AZURE_OPENAI_DEPLOYMENT_NAME", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return

    # 2. Initialize Kernel
    kernel = Kernel()
    try:
        kernel.add_service(AzureChatCompletion(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview"
        ))
        print("✅ Kernel initialized with AzureChatCompletion.")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        return

    # 3. Corrected Ping
    print("🔄 Sending test ping to Azure gpt-4o-mini...")
    service = kernel.get_service(type=AzureChatCompletion)
    
    history = ChatHistory()
    history.add_user_message("Say 'Connection Successful'")

    try:
        # Get settings from the service
        settings = kernel.get_prompt_execution_settings_from_service_id(service_id="default")
        
        response = await service.get_chat_message_content(
            chat_history=history,
            settings=settings
        )
        print(f"🚀 Response: {response.content}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_azure_connection())
