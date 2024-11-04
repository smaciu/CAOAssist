import streamlit as st
from agents import process_question  # Import the process_question function

def show_ask():
    st.title("Ask me Anything")

    # Initialize session state for user question and answer
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ''
    if 'answer' not in st.session_state:
        st.session_state.answer = ''

    # Add prompt window for user questions
    user_question = st.chat_input("What would you like to know?")
    
    if user_question:
        st.session_state.user_question = user_question
        st.write(f"You asked: {st.session_state.user_question}")
        
        # Process the user's question using the agent
        st.session_state.answer = process_question(st.session_state.user_question)
    
    # Display the response from the agent
    if st.session_state.answer:
        st.write(f"Answer: {st.session_state.answer}")
