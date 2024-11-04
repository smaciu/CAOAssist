class PresentationStyles:
    @staticmethod
    def get_base_styles():
        return """
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
            }
        """
    
    @staticmethod
    def get_navigation_styles():
        return """
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
            }
        """
    
    @staticmethod
    def get_pdf_viewer_styles():
        return """
            /* PDF viewer container */
            .pdf-viewer-container {
                max-height: calc(100vh - 200px) !important;
                overflow: hidden;
                display: flex;
                justify-content: center;
            }
        """

    @staticmethod
    def get_input_styles():
        return """
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
        """

    @staticmethod
    def get_response_styles():
        return """
            .response-container {
                margin-top: 10px !important;
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

            .element-container {
                margin-bottom: 0 !important;
            }
            
            .stButton {
                margin-bottom: 10px !important;
            }
        """

    @staticmethod
    def get_all_styles():
        """Combine all styles into one string"""
        styles = [
            PresentationStyles.get_base_styles(),
            PresentationStyles.get_navigation_styles(),
            PresentationStyles.get_pdf_viewer_styles(),
            PresentationStyles.get_input_styles(),
            PresentationStyles.get_response_styles()
        ]
        return "\n".join(styles) 