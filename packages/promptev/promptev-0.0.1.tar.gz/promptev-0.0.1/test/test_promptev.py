from promptev import PromptevClient

client = PromptevClient(
    project_key="pl_sk_bkcAkOf4pS_zdCrOeSmz8msunT4IOj_6",  # Replace with your real or test key
    base_url="http://localhost:8003",       # Pointing to your local server
    refresh_interval=10                     # Optional: faster refresh during test
)

# Test a prompt without variables
# output = client.get_prompt("test-static-prompt")
# print("Static prompt:", output)

# Test a prompt with variables
output = client.get_prompt("review-user-prompt", {
    "user_prompt_text": "How to improve LLM reasoning?"
})
print("Formatted prompt:", output)
