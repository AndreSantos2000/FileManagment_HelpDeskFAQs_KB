import requests
from io import BytesIO
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

#################################### Upload a file ###############################################

def create_file(client, file_path):
    if file_path.startswith("http://") or file_path.startswith("https://"):
        # Download the file content from the URL
        response = requests.get(file_path)
        file_content = BytesIO(response.content)
        file_name = file_path.split("/")[-1]
        file_tuple = (file_name, file_content)
        result = client.files.create(
            file=file_tuple,
            purpose="assistants"
        )
    else:
        # Handle local file path
        with open(file_path, "rb") as file_content:
            result = client.files.create(
                file=file_content,
                purpose="assistants"
            )
    print("result id: ", result.id)
    return result.id

# Replace with your own file path or URL
file_id = create_file(client, "https://cdn.openai.com/API/docs/deep_research_blog.pdf")

################################# Create a vector store #######################################

vector_store = client.vector_stores.create(
    name="knowledge_base"
)

#print("vector store: ", vector_store)
#print("vector store id: ", vector_store.id)
#print("vector store name: ", vector_store.name)

################################ Add a file to a vector store #################################

#client.vector_stores.files.create(
#    vector_store_id=vector_store.id,
#    file_id=file_id
#)

################################ Check status #####################################

#result = client.vector_stores.files.list(
#    vector_store_id=vector_store.id
#)
#print(result)