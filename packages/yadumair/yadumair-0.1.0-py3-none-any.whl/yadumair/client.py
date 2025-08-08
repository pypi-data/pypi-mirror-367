from openai import OpenAI

# Your embedded API key (WARNING: publicly exposing this key is risky)
_API_KEY = "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"

client = OpenAI(api_key=_API_KEY)

def generate_bedtime_story(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )
    return response.output_text
