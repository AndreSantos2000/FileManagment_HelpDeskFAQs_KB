from openai import OpenAI

client = OpenAI(base_url="http://10.14.208.198:1234/v1", api_key="lm-studio")

try:
    response = client.chat.completions.create(
        model="granite-3.1-8b-instruct",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, what is AI?"}
        ],
        timeout=30
    )
    print(response.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)