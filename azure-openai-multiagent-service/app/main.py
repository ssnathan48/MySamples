from fastapi import FastAPI, HTTPException
import os
import json
from fastapi import FastAPI
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


# 1. Get the path of the current file (app/main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(current_dir), "data")

os.makedirs(DATA_DIR, exist_ok=True)

client = AzureOpenAI(
    azure_endpoint=os.getenv("AI_FOUNDRY_ENDPOINT").split("/api")[0],
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview"
)



# 2. Go up one level to the root, then into the config folder
CONFIG_DIR = os.path.join(os.path.dirname(current_dir), "config")

# Load All Configs
def load_config(name):
    path = os.path.join(CONFIG_DIR, f"{name}.json")
    with open(path, "r") as f:
        return json.load(f)

ROLES = load_config("roles")
GROUNDING = load_config("grounding")
GUARDRAILS = load_config("guardrails")

@app.post("/agent/{role}")
async def run_agent(role: str, session_id: str, user_input: str):
    history_path = os.path.join(DATA_DIR, f"history_{session_id}.json")
    
    history = []

    # Validate role
    if role not in ROLES:
        raise HTTPException(status_code=400, detail="Unknown agent role")

    # Load history if exists
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                # If file is empty or corrupted, start fresh
                history = []
    else:
        history = []

    # Build system message
    system_content = (
        f"### ROLE\n{ROLES[role]}\n\n"
        f"### RULES\n{GUARDRAILS['tone']}\n\n"
        f"### FACTS\n{GROUNDING}"
    )

    # Add user message
    history.append({"role": "user", "content": user_input})

    # Call Azure Foundry model
    response = client.chat.completions.create(
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        messages=[{"role": "system", "content": system_content}] + history
    )

    reply = response.choices[0].message.content

    # ⭐ Minimal change: store agent name separately, no prefix in content
    history.append({
        "role": "assistant",
        "agent": role,
        "content": reply
    })

    # Save updated history
    with open(history_path, "w") as f:
        json.dump(history, f)

    return {"reply": reply, "agent": role}

@app.post("/team/colloborate")
async def team_chat(session_id: str, user_input: str):
    # 1. Researcher verifies facts
    res_data = await run_agent("researcher", session_id, f"Research this: {user_input}")
    
    # 2. Writer drafts based on research
    write_data = await run_agent("writer", session_id, "Write a draft based on the latest research in our history.")
    
    # 3. Manager reviews
    manage_data = await run_agent("manager", session_id, "Summarize the final output for the user.")
    
    return {"reply": manage_data["reply"], "agent": "team"}