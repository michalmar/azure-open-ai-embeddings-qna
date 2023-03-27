import streamlit as st
from urllib.error import URLError
import pandas as pd
from utilities import utils, translator
import os


import openai

from dotenv import load_dotenv
load_dotenv()


# Return a semantically aware response using the Completion endpoint
def get_semantic_answer_chatgpt(df, question, explicit_prompt="", model="DaVinci-text", engine='babbage', limit_response=True, tokens_response=100, temperature=0.0):
    openai.api_type = "azure"
    openai.api_base = "https://openaimmaus.openai.azure.com/"
    openai.api_version = "2022-12-01"
    # openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = "1379f50b34ad4fbe9718dfbd72f17515"
    model = "gpt-35-turbo"

    restart_sequence = "\n\n"
    question += "\n"

    # res = search_semantic_redis(df, question, n=3, pprint=False, engine=engine)

    prompt= """<|im_start|>system
Assistant helps user with Azure OpenAI service, and questions about data, privacy and security for Azure OpenAI. Be brief in your answers.
Answer ONLY with the facts listed in the source below. If there is no information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question.
Source:
The ChatGPT model (gpt-35-turbo) is a language model designed for conversational interfaces and the model behaves differently than previous GPT-3 models. Previous models were text-in and text-out, meaning they accepted a prompt string and returned a completion to append to the prompt. However, the ChatGPT model is conversation-in and message-out. The model expects a prompt string formatted in a specific chat-like transcript format, and returns a completion that represents a model-written message in the chat. While the prompt format was designed specifically for multi-turn conversations, you'll find it can also work well for non-chat scenarios too.
The ChatGPT model can be used with the same completion API that you use for other models like text-davinci-002, but it requires a unique prompt format known as Chat Markup Language (ChatML). It's important to use the new prompt format to get the best results. Without the right prompts, the model tends to be verbose and provides less useful responses.
<|im_end|>
<CONVERSTAION HISTORY>
<|im_start|>user
<QUESTION>
<|im_end|>
<|im_start|>assistant
"""
    history = ""
    prompt = prompt.replace("<QUESTION>", question)
    if history:
        prompt = prompt.replace("<CONVERSTAION HISTORY>", f"<|im_start|>user {history} <|im_end|>")
            

    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=temperature,
        max_tokens=tokens_response,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    # print(f"{response['choices'][0]['text'].encode().decode()}\n\n\n")

    return prompt,response#, res['page'][0]


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

# Defining a function to create the prompt from the system message and the messages
# The function assumes `messages` is a list of dictionaries with `sender` and `text` keys
# Example: messages = [{"sender": "user", "text": "I want to write a blog post about my company."}]
def create_prompt(system_message, messages):
    prompt = system_message
    for message in messages:
        prompt += f"\n<|im_start|>{message['sender']}\n{ message['text']}\n<|im_end|>"
    prompt += "\n<|im_start|>assistant\n"
    return prompt



def ask_bot():
    # utils.get_semantic_answer(df, question, st.session_state['prompt'] ,model=model, engine='davinci', limit_response=st.session_state['limit_response'], tokens_response=st.tokens_response, temperature=st.temperature)
    st.session_state['full_prompt'], st.session_state['response'] = get_semantic_answer_chatgpt(df, st.session_state['question'], st.session_state['prompt'] ,model=model, engine='davinci', limit_response=st.session_state['limit_response'], tokens_response=st.tokens_response, temperature=st.temperature)
    return True

def clear_conversation():
    st.session_state['messages'] = []
    st.session_state.clear()
    # st.session_state['response'] = None
    # st.session_state['response'] = {
    #     "choices" :[{
    #         "text" : default_answer
    #     }]
    # }
    # st.session_state['full_prompt'] = ""
    st.session_state['question'] = default_question
    print("conversation cleared")



df = utils.initialize(engine='davinci')

# @st.cache_data(suppress_st_warning=True)
def get_languages():
    return translator.get_available_languages()

try:

    default_prompt = "" 
    default_question = "" 
    default_answer = ""
    messages = []

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'prompt' not in st.session_state:
        st.session_state['prompt'] = os.getenv("QUESTION_PROMPT", "Please reply to the question using only the information present in the text above. If you can't find it, reply 'Not in the text'.\nQuestion: _QUESTION_\nAnswer:").replace(r'\n', '\n')
    if 'response' not in st.session_state:
        st.session_state['response'] = {
            "choices" :[{
                "text" : default_answer
            }]
        }    
    if 'limit_response' not in st.session_state:
        st.session_state['limit_response'] = True
    if 'full_prompt' not in st.session_state:
        st.session_state['full_prompt'] = ""
    if 'messages' not in st.session_state:
        st.session_state['messages'] = messages
        # st.write("init")
        print("messages doesn't exists")
    else:
        print("messages exists")

    
    #  Set page layout to wide screen and menu item
    menu_items = {
	'Get help': None,
	'Report a bug': None,
	'About': '''
	 ## Embeddings App
	 Embedding testing application.
	'''
    }
    st.set_page_config(layout="wide", menu_items=menu_items, initial_sidebar_state="collapsed")

    # Get available languages for translation
    available_languages = get_languages()

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        st.image(os.path.join('images','microsoft.png'))

    col1, col2, col3 = st.columns([2,2,2])
    with col3:
        with st.expander("Settings"):
            model = st.selectbox(
                "OpenAI GPT-3 Model",
                (os.environ['OPENAI_ENGINES'].split(','))
            )
            st.text_area("Prompt",height=100, key='prompt')
            st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
            st.temperature = st.slider("Temperature", 0.0, 1.0, 0.1)
            st.selectbox("Language", [None] + list(available_languages.keys()), key='translation_language')


    question = st.text_input("Chat", default_question)
    
    st.button("Ask", on_click=ask_bot)
    st.button("Clear conversation", on_click=clear_conversation)
    
    if question != '':
        if question != st.session_state['question']:
            # send question to the chatbot
            st.session_state['question'] = question
            
            # add question to session
            st.session_state['messages'].append({"sender": "user", "text": question})
            
            # st.session_state['full_prompt'], st.session_state['response'] = utils.get_semantic_answer(df, question, st.session_state['prompt'] ,model=model, engine='davinci', limit_response=st.session_state['limit_response'], tokens_response=st.tokens_response, temperature=st.temperature)
            # st.session_state['full_prompt'], st.session_state['response'] = get_semantic_answer_chatgpt(df, question, st.session_state['prompt'] ,model=model, engine='davinci', limit_response=st.session_state['limit_response'], tokens_response=st.tokens_response, temperature=st.temperature)
            st.write(f"Qa: {question}")  

            for m in st.session_state['messages']:
                st.write(f"U: {m}/{len(st.session_state['messages'])}")

            # st.write(st.session_state['response']['choices'][0]['text'])
            st.markdown(f"{st.session_state['response']['choices'][0]['text']}")
            with st.expander("Question and Answer Context"):
                st.text(st.session_state['full_prompt'].replace('$', '\$')) 
        else:

            st.write(f"Qb: {st.session_state['question']}")  
            # st.write(f"{st.session_state['response']['choices'][0]['text']}")
            st.markdown(f"{st.session_state['response']['choices'][0]['text']}")
            with st.expander("Question and Answer Context"):
                st.text(st.session_state['full_prompt'].encode().decode())

except URLError as e:
    st.error(
        """
        **This demo requires internet access.**
        Connection error: %s
        """
        % e.reason
    )