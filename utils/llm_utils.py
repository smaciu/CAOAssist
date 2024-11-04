import os
from openai import OpenAI
import anthropic
import streamlit as st

@st.cache_data(ttl=3600)  # Cache LLM responses for 1 hour
def get_cached_llm_response(prompt: str, model: str, temperature: float) -> str:
    if st.session_state.provider == "OpenAI":
        client = OpenAI()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                stream=False  # Disable streaming for cached responses
            )
            content = response.choices[0].message.content
            return content, response.usage.total_tokens
        except Exception as e:
            st.error(f"Error getting OpenAI response: {str(e)}")
            return "Sorry, there was an error processing your request.", 0
    
    elif st.session_state.provider == "Anthropic":
        client = anthropic.Anthropic()
        try:
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text, len(prompt.split())  # Approximate token count
        except Exception as e:
            st.error(f"Error getting Anthropic response: {str(e)}")
            return "Sorry, there was an error processing your request.", 0

def format_messages_for_provider(messages, provider):
    """
    Format messages according to provider's requirements
    """
    if isinstance(messages, str):
        if provider == "OpenAI":
            return [{"role": "user", "content": messages}]
        else:  # Anthropic
            return [{
                "role": "user",
                "content": [{"type": "text", "text": messages}]
            }]
    
    # Handle structured messages (including images)
    if provider == "OpenAI":
        # OpenAI expects image_url format
        return messages
    else:  # Anthropic
        formatted_messages = []
        for msg in messages:
            content = []
            if isinstance(msg["content"], list):
                for item in msg["content"]:
                    if item.get("type") == "text":
                        content.append(item)
                    elif item.get("type") == "image_url":
                        # Convert OpenAI image format to Anthropic format
                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": item["image_url"]["url"].split("base64,")[1]
                            }
                        })
            else:
                content = [{"type": "text", "text": msg["content"]}]
            
            formatted_messages.append({
                "role": msg["role"],
                "content": content
            })
        return formatted_messages

def get_llm_response(messages):
    try:
        if st.session_state.provider == "OpenAI":
            client = OpenAI()
            formatted_messages = format_messages_for_provider(messages, "OpenAI")
            response = client.chat.completions.create(
                model=st.session_state.model,
                messages=formatted_messages,
                max_tokens=4096,
                temperature=st.session_state.temperature
            )
            return response.choices[0].message.content
                
        elif st.session_state.provider == "Anthropic":
            client = anthropic.Anthropic()
            formatted_messages = format_messages_for_provider(messages, "Anthropic")
            response = client.messages.create(
                model=st.session_state.model,
                max_tokens=4096,
                temperature=st.session_state.temperature,
                messages=formatted_messages
            )
            return response.content[0].text
                
    except Exception as e:
        print(f"\nAPI Error details: {str(e)}")
        raise Exception(f"Error getting {st.session_state.provider} response: {str(e)}")
