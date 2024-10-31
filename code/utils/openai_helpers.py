import base64
import os
from openai import AzureOpenAI
import tiktoken
import PIL
from PIL import Image
import tempfile
import json
from env_vars import *
from typing import List, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    stop_after_delay,
    after_log
)

import re

############# GLOBAL VARIABLES


def get_encoder(model = "gpt-4"):
    if model == "text-search-davinci-doc-001":
        return tiktoken.get_encoding("p50k_base")
    elif model == "text-embedding-ada-002":
        return tiktoken.get_encoding("cl100k_base")
    elif model == "gpt-35-turbo": 
        return tiktoken.get_encoding("cl100k_base")
    elif model == "gpt-35-turbo-16k": 
        return tiktoken.get_encoding("cl100k_base")        
    elif model == "gpt-4-32k":
        return tiktoken.get_encoding("cl100k_base")
    elif model == "gpt-4":
        return tiktoken.get_encoding("cl100k_base")                
    elif model == "text-davinci-003":
        return tiktoken.get_encoding("p50k_base")           
    else:
        return tiktoken.get_encoding("cl100k_base")

def get_token_count(text, model = "gpt-4"):
    enc = get_encoder(model)
    return len(enc.encode(text))



OPENAI_API_BASE = f"https://{os.getenv('AZURE_OPENAI_RESOURCE')}.openai.azure.com/"
AZURE_OPENAI_EMBEDDING_API_BASE = f"https://{os.getenv('AZURE_OPENAI_EMBEDDING_MODEL_RESOURCE')}.openai.azure.com"

oai_client = AzureOpenAI(
    azure_endpoint = OPENAI_API_BASE, 
    api_key= AZURE_OPENAI_KEY,  
    api_version= AZURE_OPENAI_API_VERSION,
)

oai_emb_client = AzureOpenAI(
    azure_endpoint = AZURE_OPENAI_EMBEDDING_API_BASE, 
    api_key= AZURE_OPENAI_EMBEDDING_MODEL_RESOURCE_KEY,  
    api_version= AZURE_OPENAI_EMBEDDING_MODEL_API_VERSION,
)


# @retry(wait=wait_random_exponential(min=1, max=5), stop=(stop_after_delay(TENACITY_STOP_AFTER_DELAY) | stop_after_attempt(5)))             
def get_chat_completion(messages: List[dict], model = AZURE_OPENAI_MODEL, client = oai_client, temperature = AZURE_OPENAI_TEMPERATURE):
    # print(f"\nCalling OpenAI APIs with {len(messages)} messages - Model: {model} - Endpoint: {oai_client._base_url}\n")
    return client.chat.completions.create(model = model, temperature = temperature, messages = messages, timeout=TENACITY_TIMEOUT)


# @retry(wait=wait_random_exponential(min=1, max=5), stop=(stop_after_delay(TENACITY_STOP_AFTER_DELAY) | stop_after_attempt(5)))             
def get_embeddings(text, embedding_model = AZURE_OPENAI_EMBEDDING_MODEL, client = oai_emb_client):
    return client.embeddings.create(input=[text], model=embedding_model,timeout=TENACITY_TIMEOUT).data[0].embedding

# @retry(wait=wait_random_exponential(min=1, max=5), stop=(stop_after_delay(TENACITY_STOP_AFTER_DELAY) | stop_after_attempt(5)))             
def get_chat_completion_with_json(messages: List[dict], model = AZURE_OPENAI_MODEL, client = oai_client, temperature = AZURE_OPENAI_TEMPERATURE):
    # print(f"\nCalling OpenAI APIs with {len(messages)} messages - Model: {model} - Endpoint: {oai_client._base_url}\n")
    return client.chat.completions.create(model = model, temperature = temperature, messages = messages, response_format={ "type": "json_object" },timeout=TENACITY_TIMEOUT)


# @retry(wait=wait_random_exponential(min=1, max=5), stop=(stop_after_delay(TENACITY_STOP_AFTER_DELAY) | stop_after_attempt(5)))             
def get_chat_completion_stream(messages: List[dict], model = AZURE_OPENAI_MODEL, client = oai_client, temperature = AZURE_OPENAI_TEMPERATURE):
    # print(f"\nCalling OpenAI APIs with {len(messages)} messages - Model: {model} - Endpoint: {oai_client._base_url}\n")
    return client.chat.completions.create(model = model, temperature = temperature, messages = messages, timeout=TENACITY_TIMEOUT, stream=True)


# @retry(wait=wait_random_exponential(min=1, max=5), stop=(stop_after_delay(TENACITY_STOP_AFTER_DELAY) | stop_after_attempt(5)))             
def get_chat_completion_with_functions(messages: List[dict], functions: List[dict], function_call: str="auto", model = AZURE_OPENAI_MODEL, client = oai_client, temperature = 0.2):
    # print(f"\nCalling OpenAI APIs with Function Calling with {len(messages)} messages - Model: {model} - Endpoint: {oai_client._base_url}\n")
    return client.chat.completions.create(
        model = model,
        temperature=temperature,
        messages=messages,
        tools=functions,
        tool_choice=function_call,
        timeout=TENACITY_TIMEOUT
    )



# Function to encode an image file in base64
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file: 
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode('ascii')


def extract_json(s):
    code = re.search(r"```json(.*?)```", s, re.DOTALL)
    if code:
        return code.group(1)
    else:
        return s
    

def ask_LLM_with_images(images, labels, image_explanation_prompt = "You are a helpful vision assistant who will explain the attached image.", model_info = None, temperature = 0.2, with_json = False):

    if model_info is not None:
        client = AzureOpenAI(
                azure_endpoint =  f"https://{model_info['AZURE_OPENAI_RESOURCE']}.openai.azure.com" , 
                api_key= model_info['AZURE_OPENAI_KEY'],  
                api_version= AZURE_OPENAI_API_VERSION,
            )
        model = model_info['AZURE_OPENAI_MODEL']
    else:
        client = oai_client
        model = AZURE_OPENAI_MODEL


    image_messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": labels[i]
                },
                {
                    "type": "image_url",
                    "image_url": 
                    {
                        "url": f"data:image/jpeg;base64,{get_image_base64(image)}",
                    },
                },
            ],
        }
        for i, image in enumerate(images)
    ]
        
    messages=[
            { "role": "system", "content": "You are a helpful vision assistant." },
            { "role": "user", "content": image_explanation_prompt },
        ] + image_messages

    if with_json:
        response = get_chat_completion_with_json(messages, model = model, client = client, temperature = temperature)
    else:
        response = get_chat_completion(messages, model = model, client = client, temperature = temperature)
        
    return response.choices[0].message.content



def ask_LLM(prompt_or_messages, temperature = 0.2, model_info = None):

    if isinstance(prompt_or_messages, str):
        messages = []
        messages.append({"role": "system", "content": "You are a helpful assistant, who helps the user with their query."})     
        messages.append({"role": "system", "content": prompt_or_messages})     
    else:
        messages = prompt_or_messages

    if model_info is not None:
        client = AzureOpenAI(
                azure_endpoint =  f"https://{model_info['AZURE_OPENAI_RESOURCE']}.openai.azure.com" , 
                api_key= model_info['AZURE_OPENAI_KEY'],  
                api_version= AZURE_OPENAI_API_VERSION,
            )
        
        result = get_chat_completion(messages, model = model_info['AZURE_OPENAI_MODEL'], temperature = temperature, client=client)
    else:
        client = oai_client
        result = get_chat_completion(messages, temperature = temperature, client=client)

    return result.choices[0].message.content


def ask_LLM_streaming(messages, temperature= 0.2, model_info = None):
    if model_info is not None:
        client = AzureOpenAI(
                azure_endpoint =  f"https://{model_info['AZURE_OPENAI_RESOURCE']}.openai.azure.com" , 
                api_key= model_info['AZURE_OPENAI_KEY'],  
                api_version= AZURE_OPENAI_API_VERSION,
            )
        
        stream = get_chat_completion_stream(messages, model = model_info['AZURE_OPENAI_MODEL'], temperature = temperature, client=client)
    else:
        client = oai_client
        stream = get_chat_completion_stream(messages, temperature = temperature, client=client)

    return stream


def ask_LLM_with_JSON(prompt_or_messages, temperature = 0.2, model_info = None):

    if isinstance(prompt_or_messages, str):
        messages = []
        messages.append({"role": "system", "content": "You are a helpful assistant, who helps the user with their query. You are designed to output JSON."})     
        messages.append({"role": "system", "content": prompt_or_messages}) 
    else:
        messages = prompt_or_messages  

    if model_info is not None:
        client = AzureOpenAI(
                azure_endpoint =  f"https://{model_info['AZURE_OPENAI_RESOURCE']}.openai.azure.com" , 
                api_key= model_info['AZURE_OPENAI_KEY'],  
                api_version= AZURE_OPENAI_API_VERSION,
            )
        
        result = get_chat_completion_with_json(messages, model = model_info['AZURE_OPENAI_MODEL'], temperature = temperature, client=client)
    else:
        client = oai_client
        result = get_chat_completion_with_json(messages, temperature = temperature, client=client)

    return result.choices[0].message.content







def ask_LLM_with_functions(prompt_or_messages, functions_descr, functions = {}, args = {}, temperature = 0.2, model_info = None):

    if isinstance(prompt_or_messages, str):
        prompt = prompt_or_messages
        messages = []
        messages.append({"role": "system", "content": "You are a helpful assistant, who helps the user with their query. You are designed to take a decision on which function to call. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})     
        messages.append({"role": "user", "content": prompt})
    else:
        messages = prompt_or_messages


    if model_info is not None:
        client = AzureOpenAI(
                azure_endpoint =  f"https://{model_info['AZURE_OPENAI_RESOURCE']}.openai.azure.com" , 
                api_key= model_info['AZURE_OPENAI_KEY'],  
                api_version= AZURE_OPENAI_API_VERSION,
            )
        
        result = get_chat_completion_with_functions(messages, functions=functions, model = model_info['AZURE_OPENAI_MODEL'], temperature = temperature, client=client)
    else:
        client = oai_client
        result = get_chat_completion_with_functions(messages, functions=functions_descr, temperature = temperature, client=client)
        

    if result.choices[0].finish_reason == "tool_calls":
        rets = {}
        if len(functions) == 0:
            for f in result.choices[0].message.tool_calls:
                rets[f.function.name] = f.function.arguments
        else:
            for f in  result.choices[0].message.tool_calls:
                if f.function.name in functions:
                    print("Arguments: ", f.function.arguments)
                    rets[f.function.name] = functions[f.function.name](f.function.arguments)

        function_call_message = {
            "tool_calls": 
            [
                {
                    "id": result.choices[0].message.tool_calls[0].id,
                    "function": {
                        "name": result.choices[0].message.tool_calls[0].function.name,
                        "arguments": json.dumps(result.choices[0].message.tool_calls[0].function.arguments),
                    },
                    "type": "function"
                }
            ],
            "content": "",
            "role": "assistant"
        }

        # Create a message containing the result of the function call
        function_call_result_message = {
            "role": "tool",
            "name": result.choices[0].message.tool_calls[0].function.name,
            "content": json.dumps(rets),
            "tool_call_id": result.choices[0].message.tool_calls[0].id
        }
        
        if len(functions) == 0:
            return [ function_call_message]
        else:
            return [ function_call_message, function_call_result_message]
    else:
        return result.choices[0].message.content


def ask_LLM_with_structured_outputs(
    prompt_or_messages, 
    images=[], 
    temperature=0.2, 
    json_output=True, 
    response_format={"type": "json_object"}
):

    # Initialize the Azure OpenAI client using the environment variables.
    azure_client = AzureOpenAI(
        azure_endpoint=f"https://{os.getenv('AZURE_OPENAI_RESOURCE')}.openai.azure.com", 
        api_key=os.getenv('AZURE_OPENAI_KEY'), 
        api_version= AZURE_OPENAI_API_VERSION,
    )


    # Prepare the messages to be sent
    if isinstance(prompt_or_messages, str):
        messages = [
            {"role": "system", "content": "You are a helpful assistant, who helps the user with their query."},
            {"role": "system", "content": prompt_or_messages}
        ]
    else:
        messages = prompt_or_messages

    # Attach any images as base64 encoded strings
    image_messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{get_image_base64(image)}"},
                },
            ],
        }
        for image in images
    ]
    messages += image_messages

    # Call Azure OpenAI to get the chat completion with structured output
    result = azure_client.beta.chat.completions.parse(
        model=os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'),
        temperature=temperature,
        messages=messages,
        response_format=response_format if json_output else None
    )


    return result.choices[0].message.parsed

