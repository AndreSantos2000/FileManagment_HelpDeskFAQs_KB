from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

try:
    completion = client.chat.completions.create(
        model="granite-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2 + 2?"}
        ],
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print("Connection error:", e)