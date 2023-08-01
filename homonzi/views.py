from django.shortcuts import render
from django.template import loader
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

import openai
import pinecone

from elevenlabs import generate, play, set_api_key, save

OPENAI_API_KEY = "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"
PINECONE_API_KEY = "33045f70-074b-449b-85ed-a09cb1469f75"
PINECONE_ENVIRONMENT = "asia-southeast1-gcp-free"
PINECONE_INDEX_NAME = "hormozigpt"
PINECONE_ENDPOINT = "https://hormozigpt-004922c.svc.asia-southeast1-gcp-free.pinecone.io"
elevenlabs_api = "42a0612af6b2541354a05072144c9e57"


set_api_key(elevenlabs_api)
openai.api_key = OPENAI_API_KEY
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
index = pinecone.Index(PINECONE_INDEX_NAME)

def get_voice(text):
    generate(text=text, voice="Hormozi")

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

def generate_response(prompt):
    try:
        search_results = semantic_search(prompt, index, top_k=3)
    except:
        search_results = semantic_search(prompt, index, top_k=3)

    print(search_results)
    context = ""
    for transcript in search_results:
        context += f"Snippet from: \n {transcript}\n\n"


    # Run the LLMChain
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo")
    # print(messages)

    # Parse response
    bot_response = response["choices"][0]["message"]["content"]
    print(bot_response)
    return bot_response

# Create your views here.

def index(request):
    template = loader.get_template('main.html')
    return HttpResponse(template.render())

@csrf_exempt
def runPrompt(request):
    user_prompt = request.POST['prompt']
    print(semantic_search(user_prompt, index, top_k=3))
    message = generate(user_prompt)
    # voice = get_voice(message)
    # template = loader.get_template('main.html')
    return TemplateResponse(request, 'main.html', {'message':message})