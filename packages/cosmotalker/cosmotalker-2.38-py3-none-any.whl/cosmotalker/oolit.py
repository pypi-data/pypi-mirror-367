# main.py
# Entry point for PyLlamaUI, initializes the GUI and connects components

import sys
from api import OllamaAPI

def oolit():
    # Create Ollama API instance
    api = OllamaAPI(base_url="http://localhost:11434")
    
    # Get prompt from command-line arguments
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
    else:
        # Provide a default prompt if none is given
        prompt_user = input("Enter your prompt : ")
        prompt = prompt_user + "I want it in 2 para only each para contains 5 lines only"
    
    # Send prompt to Ollama and get response
    print("Thinking...")
    response = api.send_prompt(prompt)
    
    # Print the response
    print(f"Oolit: {response}")

oolit()
