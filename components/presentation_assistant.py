import streamlit as st
import fitz
from PIL import Image
from utils.llm_utils import get_llm_response
from utils.prompts import NUMERICAL_ANALYSIS_PROMPT, CRITIQUE_ANALYSIS_PROMPT, PRESENTATION_QA_PROMPT, PRESENTATION_NOTES_PROMPT, PRESENTATION_WHAT_IS_NOT_OBVIOUS_PROMPT, PRESENTATION_SUMMARIZE_PROMPT
import io
import base64
from styles.presentation_styles import PresentationStyles

class PresentationAssistant:
    def __init__(self):
        # Initialize session state variables with a more persistent structure
        if 'presentation_state' not in st.session_state:
            st.session_state.presentation_state = {
                'current_page': 0,
                'pdf_document': None,
                'uploaded_file': None,
                'analysis_results': {},
                'last_page_analyzed': None,
                'selected_pages': [],
                'pdf_bytes': None  # Initialize pdf_bytes to None
            }
        else:
            # Ensure all expected keys exist in presentation_state
            expected_keys = {
                'current_page': 0,
                'pdf_document': None,
                'uploaded_file': None,
                'analysis_results': {},
                'last_page_analyzed': None,
                'selected_pages': [],
                'pdf_bytes': None
            }
            for key, default_value in expected_keys.items():
                if key not in st.session_state.presentation_state:
                    st.session_state.presentation_state[key] = default_value
        
        # Initialize current_analysis if not exists
        if 'current_analysis' not in st.session_state:
            st.session_state.current_analysis = None

        # Apply styles once during initialization
        st.markdown(f"<style>{PresentationStyles.get_all_styles()}</style>", unsafe_allow_html=True)

    def _encode_image_base64(self, img):
        """Helper method to encode PIL Image to base64 string"""
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode()

    def create_message_with_image(self, text, image_base64):
        """
        Create a generic message structure that can be formatted for either provider
        """
        return [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_base64}"
                    }
                }
            ]
        }]

    def render(self):
        # At the start of render, ensure PDF document is loaded if bytes exist
        if (st.session_state.presentation_state['pdf_bytes'] is not None and 
            st.session_state.presentation_state['pdf_document'] is None):
            st.session_state.presentation_state['pdf_document'] = fitz.open(
                stream=st.session_state.presentation_state['pdf_bytes'], 
                filetype="pdf"
            )
            # Restore the previous page number when reloading document
            current_page = st.session_state.presentation_state['current_page']
            if current_page >= 0:
                st.session_state.presentation_state['current_page'] = current_page

        # Create three columns with adjusted ratio first
        left_col, spacer_col, right_col = st.columns([1.2, 0.2, 1.2])
        
        # Left column starts here
        with left_col:
            # File upload needs to be first
            with st.expander("Upload PDF"):
                uploaded_file = st.file_uploader(
                    "", 
                    type="pdf", 
                    key="presentation_pdf"
                )
                
                # Handle file upload
                if uploaded_file is not None:
                    pdf_bytes = uploaded_file.getvalue()
                    st.session_state.presentation_state['pdf_bytes'] = pdf_bytes
                    st.session_state.presentation_state['pdf_document'] = fitz.open(
                        stream=pdf_bytes, 
                        filetype="pdf"
                    )
                    
                    # Only reset page to 0 if it's a new file upload
                    if st.session_state.presentation_state['uploaded_file'] != uploaded_file:
                        st.session_state.presentation_state['current_page'] = 0
                        
                    st.session_state.presentation_state['uploaded_file'] = uploaded_file

            # Then handle the PDF display logic
            if st.session_state.presentation_state['pdf_document'] is not None:
                pdf_document = st.session_state.presentation_state['pdf_document']
                current_page = st.session_state.presentation_state['current_page']
                
                st.markdown('<div class="left-column-container">', unsafe_allow_html=True)
                
                # Add Multi-page selection using columns
                col1, col2 = st.columns([0.3, 0.7])
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
                nav_cols = st.columns([0.8, 0.8, 0.8, 0.8, 1.2, 0.8])
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
                col1, col2 = st.columns([0.7, 0.3])
                with col1:
                    analysis_type = st.selectbox(
                        "Select predefined analysis:",
                        ["Select Predefined Analysis...", 
                         "Summarize", 
                         "Check Numbers", 
                         "Critique and Reword", 
                         "Prepare Q&A", 
                         "Draft Speaker Notes",
                         "What is not obvious?"],
                        key="analysis_dropdown",
                        label_visibility="collapsed"
                    )
                with col2:
                    run_analysis = st.button("Run", type="primary")

                # Handle analysis when Run button is clicked
                if run_analysis and analysis_type != "Select Predefined Analysis...":
                    # Get the actual displayed page number (add 1 since current_page is 0-based)
                    displayed_page = st.session_state.presentation_state['current_page'] + 1
                    with st.spinner(f"Running {analysis_type} on page {displayed_page}..."):
                        try:
                            # Image handling for Vision API
                            img_base64 = self._encode_image_base64(img)

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
                            elif analysis_type == "What is not obvious?":
                                prompt = PRESENTATION_WHAT_IS_NOT_OBVIOUS_PROMPT
                            elif analysis_type == "Summarize":
                                prompt = PRESENTATION_SUMMARIZE_PROMPT
    
                            if prompt is None:
                                raise ValueError(f"Invalid analysis type: {analysis_type}")

                            messages = self.create_message_with_image(prompt, img_base64)
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

                # Handle chat input
                user_question = st.chat_input("Or ask a quick question...", key="chat_input")
                
                if user_question:
                    displayed_page = st.session_state.presentation_state['current_page'] + 1
                    with st.spinner(f"Processing user question on page {displayed_page}..."):
                        try:
                            # Image handling for Vision API
                            img_base64 = self._encode_image_base64(img)

                            # Create message structure exactly as OpenAI expects
                            messages = self.create_message_with_image(
                                f"Please analyze this slide and answer the following question: {user_question}",
                                img_base64
                            )

                            # Get LLM response
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
        # Initialize presentation_pdf in session state if not present
        if 'presentation_pdf' not in st.session_state:
            st.session_state.presentation_pdf = None
            
        if st.session_state.presentation_pdf is not None:
            # Store current page before resetting
            current_page = st.session_state.presentation_state.get('current_page', 0)
            
            pdf_bytes = st.session_state.presentation_pdf.getvalue()
            st.session_state.presentation_state['pdf_bytes'] = pdf_bytes
            st.session_state.presentation_state['pdf_document'] = fitz.open(
                stream=pdf_bytes, 
                filetype="pdf"
            )
            
            # Only reset page to 0 if it's a new file upload
            if st.session_state.presentation_state['uploaded_file'] != st.session_state.presentation_pdf:
                st.session_state.presentation_state['current_page'] = 0
            else:
                # Restore the previous page number
                st.session_state.presentation_state['current_page'] = current_page
                
            st.session_state.presentation_state['uploaded_file'] = st.session_state.presentation_pdf

