import openai
import pinecone
import homonzi.prompts as prompts

from elevenlabs import generate, play, set_api_key, save
elevenlabs_api = "42a0612af6b2541354a05072144c9e57"
set_api_key(elevenlabs_api)

OPENAI_API_KEY = "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"
PINECONE_API_KEY = "a16b3f9a-2a04-40e6-8de1-dd57cf0e979e"
PINECONE_ENVIRONMENT = "eu-west4-gcp"
PINECONE_INDEX_NAME = "kobegpt"
PINECONE_ENDPOINT = "https://kobegpt-deb658d.svc.eu-west4-gcp.pinecone.io"

openai.api_key = OPENAI_API_KEY
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

index = pinecone.Index(PINECONE_INDEX_NAME)

history_messsages = list()

def get_voice(text):
    
    return generate(text=text, voice="Bella")

def get_embeddings_openai(text):
    try:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        response = response['data']
        return [x["embedding"] for x in response]
    except Exception as e:
        print(f"Error in get_embeddings_openai: {e}")
        raise

def semantic_search(query, index, **kwargs):
    try:
        xq = get_embeddings_openai(query)


        xr = index.query(vector=xq[0], top_k=kwargs.get('top_k', 1), include_metadata=kwargs.get('include_metadata', True))

        if xr.error:
            print(f"Invalid response: {xr}")
            raise Exception(f"Query failed: {xr.error}")

        # titles = [r["metadata"]["title"] for r in xr["matches"]]
        transcripts = [r["metadata"]["text"] for r in xr["matches"]]
        return list(transcripts)

    except Exception as e:
        print(f"Error in semantic_search: {e}")
        raise

def construct_messages(history):
    messages = [{"role": "system", "content": prompts.system_message}]
    
    for entry in history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    
    return messages

def generate_response(prompt):
    try:
        search_results = semantic_search(prompt, index, top_k=3)
    except:
        search_results = semantic_search(prompt, index, top_k=3)

    context = ""
    for transcript in search_results:
        context += f"Snippet from: \n {transcript}\n\n"

    query_with_context = prompts.human_template.format(query=prompt, context=context)

    # Convert chat history to a list of messages
    messages = construct_messages(history_messsages)
    
    messages.append({"role": "user", "content": query_with_context})

    # Run the LLMChain
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    # print(messages)

    # Parse response
    bot_response = response["choices"][0]["message"]["content"]

    message1 = {'is_user':True, 'message':prompt}
    message2 = {'is_user':False, 'message':bot_response}

    history_messsages.append(message1)
    history_messsages.append(message2)

    print(history_messsages)

    return bot_response