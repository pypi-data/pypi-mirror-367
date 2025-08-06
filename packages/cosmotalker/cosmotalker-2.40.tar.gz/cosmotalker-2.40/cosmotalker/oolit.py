
# main.py
# Entry point for PyLlamaUI, initializes the GUI and connects components

import sys
from .api import api

def oolit(prompt: str = None):
    """
    Sends a prompt to the Ollama API and returns the response.
    If no prompt is provided, it will prompt the user for input.

    Args:
        prompt: The prompt to send to the Ollama API. Optional.

    Returns:
        The response from the Ollama API.
    """
    # Create Ollama API instance
    api_instance = api(base_url="http://localhost:11434")
    
    if prompt is None:
        prompt = input("Enter your prompt : ")
    
    # Send prompt to Ollama and get response
    print("Thinking...")
    response = api_instance.send_prompt(prompt)
    
    return response

if __name__ == '__main__':
    # This block will only execute when the script is run directly
    # For example: python -m cosmotalker.oolit "your prompt here"
    if len(sys.argv) > 1:
        prompt_text = ' '.join(sys.argv[1:])
    else:
        # Provide a default prompt if none is given
        prompt_user = input("Enter your prompt : ")
        prompt_text = prompt_user + "I want it in 2 para only each para contains 5 lines only"
    
    print("Thinking...")
    oolit_response = oolit(prompt_text)
    print(f"Oolit: {oolit_response}")
