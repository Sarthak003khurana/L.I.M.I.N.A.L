import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


load_dotenv()

project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not project_endpoint:
    raise ValueError("FOUNDRY_PROJECT_ENDPOINT is missing")

if not deployment:
    raise ValueError("AZURE_OPENAI_DEPLOYMENT is missing")


print("Connecting to Microsoft Foundry...")
print(f"Deployment: {deployment}")

project_client = AIProjectClient(
    endpoint=project_endpoint,
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    model=deployment,
    input="Reply with exactly: LIMINAL AZURE CONNECTION SUCCESS",
    max_output_tokens=50,
)

print()
print(response.output_text)