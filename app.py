import streamlit as st
from components.presentation_assistant import PresentationAssistant
from components import policy, legal, hr, calendar, email, coding, ask, simplify   
from utils.config import *
import os

# Set page to wide mode

st.set_page_config(
        page_title="CAO Assistant",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )

def add_custom_css():
    css_file = os.path.join(os.path.dirname(__file__), "styles", "main.css")
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def set_page(page):
    st.session_state.page = page
    
def main():
    # Initialize session state for page if it doesn't exist
    if 'page' not in st.session_state:
        st.session_state.page = 'ask'  # Set default page
        
    presentation_assistant = PresentationAssistant()
    initialize_session_state()
    sidebar()
    add_custom_css()

    st.markdown('<div class="header-menu">', unsafe_allow_html=True)
    buttons = [
        ("📝 Decks", 'decks'),
        ("📜 Policy", 'policy'),
        ("🧑‍⚖️ Legal", 'legal'),
        ("🧩 Talent", 'hr'),
        ("📅 Diary", 'calendar'),
        ("📧 Email", 'email'),
        ("💻 Coding", 'coding'),
        ("🧩 Simplify", 'simplify'),
        ("🤔 Any Q&A", 'ask')
    ]

    cols = st.columns(len(buttons))
    for col, (label, page) in zip(cols, buttons):
        with col:
            is_active = st.session_state.page == page
            button_key = f"{page}_{'active' if is_active else 'inactive'}"
            st.button(
                label,
                on_click=set_page,
                args=(page,),
                key=button_key,
                type="primary" if is_active else "secondary"
            )
    st.markdown('</div>', unsafe_allow_html=True)


    # Page navigation logic
    if 'page' not in st.session_state:
        st.session_state.page = 'ask'

    if st.session_state.page == 'decks':
        presentation_assistant.render()
    elif st.session_state.page == 'policy':
        policy.show_policy()    
    elif st.session_state.page == 'legal':
        legal.show_legal()
    elif st.session_state.page == 'hr':
        hr.show_hr()
    elif st.session_state.page == 'calendar':
        calendar.show_calendar()
    elif st.session_state.page == 'email':
        email.show_email()  
    elif st.session_state.page == 'coding':
        coding.show_coding()
    elif st.session_state.page == 'simplify':
        simplify.show_simplify()
    elif st.session_state.page == 'ask':
        ask.show_ask()  


if __name__ == "__main__":
    main()
