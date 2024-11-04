import streamlit as st
import fitz
from PIL import Image
from utils.llm_utils import get_llm_response
from utils.prompts import NUMERICAL_ANALYSIS_PROMPT, CRITIQUE_ANALYSIS_PROMPT, PRESENTATION_QA_PROMPT, PRESENTATION_NOTES_PROMPT
import io
import base64

class PresentationAssistant:
    def __init__(self):
        # Initialize session state variables
        if 'presentation_state' not in st.session_state:
            st.session_state.presentation_state = {
                'current_page': 0,
                'pdf_document': None,
                'uploaded_file': None,
                'analysis_results': {},  # Store analysis results per page
                'last_page_analyzed': None,
                'selected_pages': []  # Initialize selected_pages as empty list
            }
        
        # Initialize current_analysis if not exists
        if 'current_analysis' not in st.session_state:
            st.session_state.current_analysis = None

    def render(self):
        #st.title("Presentation Assistant")
        st.markdown("""
            <style>
            /* Column layout containers */
            .left-column {
                width: 100%;
                padding-right: 20px;
            }
            
            /* PDF viewer */
            .stImage {
                max-height: 600px !important;
                width: auto !important;
                margin: 0 auto !important;
                display: block !important;
                border: 1px solid #ddd !important;
                border-radius: 5px !important;
            }
            
            /* Controls container */
            .controls-container {
                width: 100%;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #eee;
            }

            /* Navigation buttons container */
            .nav-buttons {
                display: flex;
                gap: 5px;
                margin-bottom: 10px;
            }
            
            /* Navigation buttons */
            .stButton > button {
                min-width: 40px !important;
                height: 30px !important;
                padding: 0 8px !important;
                font-size: 0.8em !important;
                margin: 0 !important;
            }

            /* Chat input styling */
            .stChatInput {
                margin-top: 10px;
                margin-bottom: 5px;
            }
            
            .stChatInput > div {
                padding: 5px;
            }
            
            /* Make chat input match the container style */
            .stChatInput input {
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.9em;
            }

            /* PDF viewer container */
            .pdf-viewer-container {
                max-height: calc(100vh - 200px) !important;  /* Adjust for header and margins */
                overflow: hidden;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* Image styling */
            .pdf-viewer-container img {
                max-height: 100% !important;
                width: auto !important;
                object-fit: contain !important;
                border: 1px solid #ddd !important;
                border-radius: 5px !important;
            }
            
            /* Adjust stImage container */
            [data-testid="stImage"] {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
                max-height: calc(100vh - 200px) !important;
            }
            
            [data-testid="stImage"] > img {
                max-height: calc(100vh - 200px) !important;
                object-fit: contain !important;
            }

            /* Move entire analysis tools section up */
            [data-testid="stHorizontalBlock"] {
                margin-top: -10px !important;
            }
            </style>
            """, unsafe_allow_html=True)

        # Create three columns with adjusted ratio first
        left_col, spacer_col, right_col = st.columns([1.2, 0.2, 1.2])
        
        # Left column starts here
        with left_col:
            # File upload needs to be first
            with st.expander("Upload PDF"):
                uploaded_file = st.file_uploader(
                    "", 
                    type="pdf", 
                    key="presentation_pdf",
                    on_change=self._handle_file_upload
                )

            # Then handle the PDF display logic
            if st.session_state.presentation_state['pdf_document'] is not None:
                pdf_document = st.session_state.presentation_state['pdf_document']
                current_page = st.session_state.presentation_state['current_page']
                
                st.markdown('<div class="left-column-container">', unsafe_allow_html=True)
                
                # Navigation buttons at the top
                st.markdown("""
                    <style>
                    /* Navigation buttons container */
                    .nav-buttons {
                        display: flex;
                        gap: 3px;
                        margin-bottom: 8px;
                    }
                    
                    /* Navigation buttons */
                    .stButton > button {
                        min-width: 35px !important;
                        height: 25px !important;
                        padding: 0 6px !important;
                        font-size: 0.7em !important;
                        margin: 0 !important;
                        line-height: 1 !important;
                    }
                    
                    /* Page info */
                    .page-info {
                        text-align: center;
                        font-size: 0.7em;
                        color: #666;
                        margin: 3px 0;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # Add Multi-page selection using columns
                col1, col2 = st.columns([0.3, 0.7])  # Adjust ratio as needed
                with col1:
                    multi_page = st.checkbox('Multi Page', value=False)
                with col2:
                    if multi_page:
                        page_range = st.text_input(
                            "Enter page numbers (e.g., 1,2,3 or 1-5)",
                            label_visibility="collapsed",
                            help="Specify individual pages with commas (1,2,3) or a range with hyphen (1-5)"
                        )
                        if page_range:
                            try:
                                selected_pages = set()
                                for part in page_range.split(','):
                                    if '-' in part:
                                        start, end = map(int, part.split('-'))
                                        selected_pages.update(range(start, end + 1))
                                    else:
                                        selected_pages.add(int(part))
                                    # Store selected pages in session state
                                    st.session_state.presentation_state['selected_pages'] = sorted(list(selected_pages))
                            except ValueError:
                                st.error("Invalid page format. Please use numbers separated by commas or ranges with hyphens.")
                            else:
                                # Clear selected pages if input is empty
                                st.session_state.presentation_state['selected_pages'] = []
                        else:
                            # Clear selected pages if multi_page is unchecked
                            st.session_state.presentation_state['selected_pages'] = []
                
                # Navigation buttons in a row
                nav_cols = st.columns([0.8, 0.8, 0.8, 0.8, 1.2, 0.8])  # Adjusted column ratios
                with nav_cols[0]:
                    if st.button("First", key="first", use_container_width=True):
                        st.session_state.presentation_state['current_page'] = 0
                        st.rerun()
                
                with nav_cols[1]:
                    if st.button("Prev", key="prev", use_container_width=True):
                        if st.session_state.presentation_state['current_page'] > 0:
                            st.session_state.presentation_state['current_page'] -= 1
                            st.rerun()
                
                with nav_cols[2]:
                    if st.button("Next", key="next", use_container_width=True):
                        if current_page < pdf_document.page_count - 1:
                            st.session_state.presentation_state['current_page'] += 1
                            st.rerun()
                
                with nav_cols[3]:
                    if st.button("Last", key="last", use_container_width=True):
                        st.session_state.presentation_state['current_page'] = pdf_document.page_count - 1
                        st.rerun()
                
                with nav_cols[4]:
                    goto_page = st.number_input("", min_value=1, max_value=pdf_document.page_count, value=current_page + 1, label_visibility="collapsed")

                with nav_cols[5]:
                    if st.button("Go to", key="goto", use_container_width=True):
                        st.session_state.presentation_state['current_page'] = goto_page - 1
                        st.rerun()

                # Page info below navigation
                st.markdown(f'<div class="page-info">Page {current_page + 1} of {pdf_document.page_count}</div>', 
                          unsafe_allow_html=True)



                # PDF Viewer below navigation
                if pdf_document.page_count > 0:
                    page = pdf_document[current_page]
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # Calculate aspect ratio and resize if needed
                    max_height = 800  # Maximum height in pixels
                    if img.height > max_height:
                        aspect_ratio = img.width / img.height
                        new_height = max_height
                        new_width = int(max_height * aspect_ratio)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    st.markdown('<div class="pdf-viewer-container">', unsafe_allow_html=True)
                    st.image(img, use_column_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Please upload a PDF presentation to begin.")

        # Right column - Analysis Tools
        with right_col:
            if st.session_state.presentation_state['pdf_document'] is not None:
                # Analysis tools dropdown and run button in columns
                col1, col2 = st.columns([0.7, 0.3])  # Adjusted ratio for better alignment
                with col1:
                    st.markdown("""
                        <style>
                        /* Remove label and extra spacing from selectbox */
                        [data-testid="stSelectbox"] > label {
                            display: none;
                        }
                        [data-testid="stSelectbox"] {
                            margin-top: 0 !important;
                            padding-top: 0 !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    analysis_type = st.selectbox(
                        "Select predefined analysis:",
                        ["Select Predefined Analysis...", "Check Numbers", "Critique and Reword", "Prepare Q&A", "Draft Speaker Notes"],
                        key="analysis_dropdown",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown("""
                        <style>
                        /* Align button with dropdown */
                        div[data-testid="column"]:nth-of-type(2) .stButton {
                            margin-top: 3px !important;  /* Fine-tune this value as needed */
                            width: 60px;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    run_analysis = st.button("Run", type="primary")

                # Handle analysis when Run button is clicked
                if run_analysis and analysis_type != "Select Predefined Analysis...":
                    current_page = st.session_state.presentation_state['current_page'] + 1
                    with st.spinner(f"Running {analysis_type} on page {current_page}..."):
                        try:
                            # Image handling for Vision API
                            img_byte_arr = io.BytesIO()
                            img.save(img_byte_arr, format='PNG', optimize=True)
                            img_byte_arr = img_byte_arr.getvalue()
                            img_base64 = base64.b64encode(img_byte_arr).decode()

                            # Create message structure based on analysis type
                            prompt = None
                            if analysis_type == "Check Numbers":
                                prompt = NUMERICAL_ANALYSIS_PROMPT
                            elif analysis_type == "Critique and Reword":
                                prompt = CRITIQUE_ANALYSIS_PROMPT
                            elif analysis_type == "Prepare Q&A":
                                prompt = PRESENTATION_QA_PROMPT
                            elif analysis_type == "Draft Speaker Notes":
                                prompt = PRESENTATION_NOTES_PROMPT

                            if prompt is None:
                                raise ValueError(f"Invalid analysis type: {analysis_type}")

                            messages = [
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": prompt
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/png;base64,{img_base64}"
                                            }
                                        }
                                    ]
                                }
                            ]

                            analysis_result = get_llm_response(messages)
                            st.session_state.current_analysis = {
                                'type': analysis_type,
                                'content': analysis_result
                            }
                        except Exception as e:
                            print(f"\nError occurred: {str(e)}")
                            st.session_state.current_analysis = {
                                'type': 'Error',
                                'content': f"Error in {analysis_type}: {str(e)}"
                            }

                # Add chat input below dropdown
                st.markdown("""
                    <style>
                    /* Dropdown styling */
                    .stSelectbox {
                        margin-bottom: 10px;
                    }
                    
                    /* Chat input styling */
                    .stChatInput {
                        margin-top: 10px;
                        margin-bottom: 5px;
                    }
                    
                    .stChatInput > div {
                        padding: 5px;
                    }
                    
                    .stChatInput input {
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 0.9em;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # Chat input
                user_question = st.chat_input("Ask a specific question about this slide...")
                
                if user_question:
                    # Image handling for Vision API
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG', optimize=True)
                    img_byte_arr = img_byte_arr.getvalue()
                    img_base64 = base64.b64encode(img_byte_arr).decode()

                    # Create message structure exactly as OpenAI expects
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Please analyze this slide and answer the following question: {user_question}"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_base64}"
                                    }
                                }
                            ]
                        }
                    ]

                    # Get LLM response
                    with st.spinner(f"Processing user question on page {current_page}..."):
                        try:
                            analysis_result = get_llm_response(messages)
                            st.session_state.current_analysis = {
                                'type': 'Q&A Response',
                                'content': f"Q: {user_question}\n\nA: {analysis_result}"
                            }
                        except Exception as e:
                            print(f"\nError occurred: {str(e)}")
                            st.session_state.current_analysis = {
                                'type': 'Error',
                                'content': f"Error processing question: {str(e)}"
                            }

                # Response container with adjusted styling
                st.markdown("""
                    <style>
                    .response-container {
                        margin-top: 10px !important;  /* Reduced from 20px */
                        padding: 15px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        background-color: #f8f9fa;
                        min-height: 200px;
                    }
                    
                    .response-header {
                        font-size: 1em;
                        font-weight: bold;
                        margin-bottom: 10px;
                        color: #333;
                    }
                    
                    .response-content {
                        font-size: 0.9em;
                        line-height: 1.5;
                        color: #444;
                    }

                    /* Remove extra spacing between elements */
                    .element-container {
                        margin-bottom: 0 !important;
                    }
                    
                    /* Adjust spacing for buttons */
                    .stButton {
                        margin-bottom: 10px !important;
                    }
                    </style>
                """, unsafe_allow_html=True)


                if st.session_state.current_analysis:
                    st.markdown(f'<div class="response-header">{st.session_state.current_analysis["type"]}</div>', 
                              unsafe_allow_html=True)
                    st.markdown(f'<div class="response-content">{st.session_state.current_analysis["content"]}</div>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown('<div class="response-content">Select an analysis tool above or type a question to see results here.</div>', 
                              unsafe_allow_html=True)
            #else:
                #st.info("Analysis tools will appear here after uploading a PDF.")


    def _handle_file_upload(self):
        """Handle file upload and update session state"""
        if st.session_state.presentation_pdf is not None:
            pdf_bytes = st.session_state.presentation_pdf.getvalue()
            st.session_state.presentation_state['pdf_document'] = fitz.open(stream=pdf_bytes, filetype="pdf")
            st.session_state.presentation_state['current_page'] = 0
            st.session_state.presentation_state['uploaded_file'] = st.session_state.presentation_pdf
