# %% [markdown]
# # Managing conversation history with the ChatGPT model
# This sample notebook demonstrates a couple of simple patterns you can use for managing the prompts and conversation history with the ChatGPT model.

# %%
import os
import openai
import json

# %%
# Load config values
# with open(r'config.json') as config_file:
#     config_details = json.load(config_file)



# openai.api_key = os.getenv("OPENAI_API_KEY")



# Setting up the deployment name
# chatgpt_model_name = config_details['CHAT_GPT_MODEL']
chatgpt_model_name = "gpt-35-turbo"
# This is set to `azure`
openai.api_type = "azure"

# The API key for your Azure OpenAI resource.
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "1379f50b34ad4fbe9718dfbd72f17515"

# The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
# openai.api_base = config_details['OPENAI_API_BASE']
openai.api_base = "https://openaimmaus.openai.azure.com/"
# Currently OPENAI API have the following versions available: 2022-12-01
# openai.api_version = config_details['OPENAI_API_VERSION']
openai.api_version = "2022-12-01"

# %% [markdown]
# ## 1.0 Create the system message for ChatGPT

# %%
base_system_message = """
You are a marketing writing assistant. You help come up with creative content ideas and content like marketing emails, blog posts, tweets, ad copy, listicles, product FAQs, and product descriptions. 
You write in a friendly yet professional tone and you can tailor your writing style that best works for a user-specified audience. 

Additional instructions:
- Make sure you understand your user's audience so you can best write the content.
- Ask clarifying questions when you need additional information. Examples include asking about the audience or medium for the content.
- Don't write any content that could be harmful.
- Don't write any content that could be offensive or inappropriate.
- Don't write any content that speaks poorly of any product or company.
"""

system_message = f"<|im_start|>system\n{base_system_message.strip()}\n<|im_end|>"
print(system_message)

# %% [markdown]
# ## 2.0 Define helper functions
# 
# 

# %%
# Defining a function to create the prompt from the system message and the messages
# The function assumes `messages` is a list of dictionaries with `sender` and `text` keys
# Example: messages = [{"sender": "user", "text": "I want to write a blog post about my company."}]
def create_prompt(system_message, messages):
    prompt = system_message
    for message in messages:
        prompt += f"\n<|im_start|>{message['sender']}\n{ message['text']}\n<|im_end|>"
    prompt += "\n<|im_start|>assistant\n"
    return prompt

# %%
import tiktoken 

# Defining a function to estimate the number of tokens in a prompt
def estimate_tokens(prompt):
    cl100k_base = tiktoken.get_encoding("cl100k_base") 

    enc = tiktoken.Encoding( 
        name="chatgpt",  
        pat_str=cl100k_base._pat_str, 
        mergeable_ranks=cl100k_base._mergeable_ranks, 
        special_tokens={ 
            **cl100k_base._special_tokens, 
            "<|im_start|>": 100264, 
            "<|im_end|>": 100265
        } 
    ) 

    tokens = enc.encode(prompt,  allowed_special={"<|im_start|>", "<|im_end|>"})
    return len(tokens)

# Estimate the number of tokens in the system message. Tokens in the system message will be sent in every request.
token_count = estimate_tokens(system_message)
print("Token count: {}".format(token_count))

# %%
# Defining a function to send the prompt to the ChatGPT model
def send_message(prompt, model_name, max_response_tokens=500):
    response = openai.Completion.create(
        engine=chatgpt_model_name,
        prompt=prompt,
        temperature=0.5,
        max_tokens=max_response_tokens,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0,
        stop=['<|im_end|>']
    )
    return response['choices'][0]['text'].strip()

# Defining a function to print out the conversation in a readable format
def print_conversation(messages):
    for message in messages:
        print(f"[{message['sender'].upper()}]")
        print(message['text'])
        print()

# %% [markdown]
# ## 3.0 Start the conversation

# %%
# This is the first message that will be sent to the model. Feel free to update this.
user_message = "I want to write a blog post about the impact of AI on the future of work."

# %%
# Create the list of messages. Sender can be either "user" or "assistant"
messages = [{"sender": "user", "text": user_message}]

# Create the full prompt
prompt = create_prompt(system_message, messages)

print(prompt)

# %%
token_count = estimate_tokens(prompt)
print(f"Token count: {token_count}")

# %%
max_response_tokens = 500

response = send_message(prompt, chatgpt_model_name, max_response_tokens)
messages.append({"sender": "assistant", "text": response})

print_conversation(messages)

# %% [markdown]
# ## 4.0 Continue the conversation
# 
# When working with the ChatGPT model, it's your responsibity to make sure you stay within the token limits of the model. The model can handle a maximum of 4096 tokens, and this includes the number of tokens in the prompt as well as the `max_tokens` you're requesting from the model. If you exceed these limits, the model will return an error.
# 
# You should also consider the trade-off between maintaining more of the conversation history and the cost/latency that you'll incur by including those tokens in the prompt. Shorter prompts are cheaper and faster. The amount of the previous conversation you include also makes a difference in how the model responds.
# 
# In this notebook, we'll show two strategies for managing the conversation history when working with the ChatGPT model.
# - Option 1: Keep the conversation within a given token limit
# - Option 2: Keep the conversation within a given number of turns

# %% [markdown]
# ### Option 1: Keep the conversation within a given token limit
# 
# `overall_max_tokens` is the maximum number of tokens that you want to include in the prompt. Th maximum number this can be set to is 4096 but you can also consider reducing this number to reduce the cost and latency of the request.

# %%
overall_max_tokens = 4096
prompt_max_tokens = overall_max_tokens - max_response_tokens

# %% [markdown]
# You can continue the conversation below by editing the user_message and running the cell as many times as you would like.

# %%
user_message = "The target audience for the blog post should be business leaders working in the tech industry."
#user_message = "Let's talk about generative AI and keep the tone informational but also friendly."
#user_message = "Show me a few more examples"
messages.append({"sender": "user", "text": user_message})

prompt = create_prompt(system_message, messages)
token_count = estimate_tokens(prompt)
print(f"Token count: {token_count}")

# remove first message while over the token limit
while token_count > prompt_max_tokens:
    messages.pop(0)
    prompt = create_prompt(system_message, messages)
    token_count = estimate_tokens(prompt)

response = send_message(prompt, chatgpt_model_name, max_response_tokens)

messages.append({"sender": "assistant", "text": response})
print_conversation(messages)

# %% [markdown]
# ### Option 2: Keep the conversation within a given number of turns

# %%
max_messages = 10

overall_max_tokens = 4096
prompt_max_tokens = overall_max_tokens - max_response_tokens

# %% [markdown]
# You can continue the conversation below by editing the user_message and running the cell as many times as you would like.

# %%
user_message = "Make the post about generative AI aimed at business leaders who have some knowledge of the technology."
messages.append({"sender": "user", "text": user_message})

while len(messages) > max_messages:
    messages.pop(0)

prompt = create_prompt(system_message, messages)
token_count = estimate_tokens(prompt)

while token_count > prompt_max_tokens:
    # remove first message from messages
    messages.pop(0)
    prompt = create_prompt(system_message, messages, max_response_tokens)
    token_count = estimate_tokens(prompt)

response = send_message(prompt, chatgpt_model_name)
messages.append({"sender": "assistant", "text": response})
# print_conversation(messages)


# %%



