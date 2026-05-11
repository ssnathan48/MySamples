import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
load_dotenv(os.path.join(root_dir, ".env"))

def setup():
    # SDK combines endpoint + project_name to match your portal URL
    client = AIProjectClient(
        endpoint=os.getenv("AI_FOUNDRY_ENDPOINT"),
        subscription_id=os.getenv("AI_FOUNDRY_SUBSCRIPTION"),
        resource_group_name=os.getenv("AI_FOUNDRY_RG"),
        project_name=os.getenv("AI_FOUNDRY_PROJECT"),
        credential=DefaultAzureCredential()
    )

    with open(os.path.join(root_dir, "config", "roles.json"), "r") as f:
        roles = json.load(f)

    # Creating the Agent
    agent = client.agents.create_agent(
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        name="Foundry-Manager",
        instructions=roles["manager"]
    )

    print(f"\n✅ SUCCESS! Manager Agent Created.")
    print(f"MANAGER_AGENT_ID={agent.id}")

if __name__ == "__main__":
    setup()
