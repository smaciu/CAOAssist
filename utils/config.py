import streamlit as st
import os

def initialize_session_state():
    # Global settings
    if 'provider' not in st.session_state:
        st.session_state.provider = "OpenAI"
    if 'model' not in st.session_state:
        st.session_state.model = "gpt-4o"  
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    if 'streaming' not in st.session_state:
        st.session_state.streaming = True
    if 'token_usage' not in st.session_state:
        st.session_state.token_usage = 0

def get_available_models(provider):
    models = {
        "OpenAI": {
            "gpt-4o-preview": "gpt-4o-preview",
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini",
            "gpt-4-turbo": "gpt-4-turbo",
            "gpt-3.5-turbo": "gpt-3.5-turbo"
        },
        "Anthropic": {
            "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229": "claude-3-opus-20240229",
            "claude-3-haiku-20240307": "claude-3-haiku-20240307"
        }
    }
    return models.get(provider, {})

def sidebar():
    with st.sidebar:
        st.title("Configuration")
        
        # Provider selection
        provider = st.selectbox(
            "Select Provider",
            ["OpenAI", "Anthropic"],
            index=0 if st.session_state.provider == "OpenAI" else 1,
            key="provider_select",
            help="Choose the AI provider for responses"
        )
        
        # Model selection based on provider
        available_models = get_available_models(provider)
        model_options = list(available_models.keys())
        model_display_names = list(available_models.values())
        current_model_index = model_options.index(st.session_state.model) if st.session_state.model in model_options else 0
        
        selected_display_name = st.selectbox(
            "Select Model",
            options=model_display_names,
            index=current_model_index,
            key="model_select",
            help="Choose the AI model for processing"
        )
        
        # Map display name back to model ID (they're now the same)
        model = selected_display_name
        
        # Temperature slider with tooltip
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Higher values make output more random, lower values more deterministic"
        )
        
        # Streaming toggle with tooltip
        streaming = st.toggle(
            "Enable Streaming",
            value=st.session_state.streaming,
            help="Toggle real-time response streaming"
        )
        
        # Update session state
        if provider != st.session_state.provider:
            st.session_state.provider = provider
            st.session_state.model = model_options[0]
            st.rerun()
        if model != st.session_state.model:
            st.session_state.model = model
        if temperature != st.session_state.temperature:
            st.session_state.temperature = temperature
        if streaming != st.session_state.streaming:
            st.session_state.streaming = streaming
            
        # Token usage metric with tooltip
        st.metric(
            "Token Usage",
            f"{st.session_state.token_usage:,}",
            help="Total tokens used across all operations"
        )