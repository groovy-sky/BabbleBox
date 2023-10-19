import openai
import os
import json
import sys
import uuid
from termcolor import colored

openai.api_key = os.getenv('OPENAI_API_KEY')
if openai.api_key is None:
    sys.exit("Fatal Error: OPENAI_API_KEY environment variable is not set.")

openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com')
openai.api_version = os.getenv('OPENAI_API_VERSION', 'v1')
model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
CONVERSATIONS_DIR = os.getenv('CONVERSATIONS_DIR', 'conversations')
openai.api_type = "azure"

parameters = {
    'max_tokens': 150,
    'temperature': 0.6,
    'top_p': 1,
    'frequency_penalty': 0.0,
    'presence_penalty': 0.0,
}

def load_conversations():
    conversations = []
    for file in os.listdir(CONVERSATIONS_DIR):
        if file.endswith(".json") and not file.endswith("_metadata.json"):
            with open(os.path.join(CONVERSATIONS_DIR, file), 'r') as f:
                conversations.append(json.load(f))
    return conversations

def save_conversation(conversation):
    filename = os.path.join(CONVERSATIONS_DIR, f"{uuid.uuid4().hex}")
    with open(f"{filename}.json", 'w') as f:
        json.dump(conversation, f)
    with open(f"{filename}_metadata.json", 'w') as f:
        json.dump(parameters, f)

def continue_conversation(conversation):
    while True:
        message = input(colored("You (type 'quit' to stop conversation or 'q' to quit program): ", "blue"))
        if message.lower() == 'quit':
            return
        elif message.lower() == 'q':
            sys.exit(0)
        conversation['messages'].append({"role": "system", "content": "You start a new session."})
        conversation['messages'].append({"role": "user", "content": message})
        response = openai.ChatCompletion.create(
            engine="gpt4",
            model=model, 
            messages=conversation['messages'],
            max_tokens=parameters['max_tokens'],
            temperature=parameters['temperature'],
            top_p=parameters['top_p'],
            frequency_penalty=parameters['frequency_penalty'],
            presence_penalty=parameters['presence_penalty']
        )
        print(colored(f"AI (used tokens: {response['usage']['total_tokens']}): ", "green"), response['choices'][0]['message']['content'])
        save_conversation(conversation)

def start_new_conversation():
    system_message = input("Enter a system message: ")
    conversation = {
        'messages': [
            {"role": "system", "content": system_message},
        ]
    }
    continue_conversation(conversation)

def main():
    if not os.path.exists(CONVERSATIONS_DIR):
        os.makedirs(CONVERSATIONS_DIR)
    while True:
        conversations = load_conversations()
        print("0: Start new conversation")
        for i, conversation in enumerate(conversations, start=1):
            print(f"{i}: Continue conversation from {conversation['messages'][-1]['content']}")
        try:
            choice = input(colored("Choose a conversation (or type 'q' to quit): ", "red"))
            if choice.lower() == 'q':
                sys.exit(0)
            choice = int(choice)
            if choice < 0 or choice > len(conversations):
                print("Invalid choice. Please choose a valid conversation number.")
            elif choice == 0:
                start_new_conversation()
            else:
                continue_conversation(conversations[choice-1])
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()
