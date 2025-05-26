from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def AI_interaction(sys_content = "Answer in prose", user_content = "Give me an introduction on the historical context on the Republic by Plato"):
    completion = client.chat.completions.create(
    model="granite-3.1-8b-instruct",
    messages=[
        {"role": "system", "content": sys_content},#"Always answer in rhymes."},
        #{"role": "user", "content": "Introduce yourself."}
        {"role": "user", "content": user_content}#"What do you know?"}
    ],
    temperature=0.7,
    )
    print(completion.choices[0].message)


def get_embedding(text, model="granite-3.1-8b-instruct"):
   text = text.replace("\n", " ")
   return client.embeddings.create(model=model, input = [text], encoding_format="float").data[0].embedding


#AI_interaction("answer in verse")
#print(get_embedding("Once upon a time, ..."))
