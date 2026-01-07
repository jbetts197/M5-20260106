import os
import re 
from openai import OpenAI

# Create client to OPENAI via the Hugging Face Proxy
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("AI_API_KEY"),  # SHOULD BE SET IN VAULT OR AS ARGPARSE
)

# Use completion method to send prompt to model
completion = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1",
    messages=[
        {
            "role": "system",
            "content": "Answer concisely. Please don't provide a sentence over 60 words."
        },
        {
            "role": "user",
            "content": "Explain Apache Kafka in one sentence."
        }
    ],
    temperature=0.3,
    max_tokens=60,
)

# Clean the result to exclude the thinking data
THINKING_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL)
def normalize_llm_output(text: str) -> str:
    text = THINKING_PATTERN.sub("", text)
    return text.strip()
cleaned_result = normalize_llm_output(completion.choices[0].message.content)

# Print the cleaned result
print(cleaned_result)