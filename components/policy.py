import streamlit as st
import tempfile
import os
import json
from pathlib import Path
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

class PolicyAssistant:
    def __init__(self):
        self.base_path = Path("data/vectorstore")
        self.metadata_path = self.base_path / "document_metadata.json"
        self.vectorstore_path = self.base_path / "vectorstore"
        
        # Create directories if they don't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components first
        self.llm = ChatOpenAI(temperature=0)
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        
        # Then initialize state and load documents
        self.initialize_session_state()
        self.load_existing_documents()

    def load_existing_documents(self):
        """Load existing documents and vectorstore from disk"""
        try:
            # Load document metadata
            if self.metadata_path.exists():
                with open(self.metadata_path, 'r') as f:
                    st.session_state.document_objects = json.load(f)
            
            # Load vectorstore if it exists
            if self.vectorstore_path.exists():
                st.session_state.vectorstore = FAISS.load_local(
                    str(self.vectorstore_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                
        except Exception as e:
            st.error(f"Error loading existing documents: {str(e)}")
            st.session_state.document_objects = {}
            st.session_state.vectorstore = None

    def save_documents_metadata(self):
        """Save document metadata to disk"""
        try:
            # Save only the metadata, not the full documents
            metadata = {
                filename: {
                    'filename': filename,
                    'num_chunks': len(docs)
                }
                for filename, docs in st.session_state.document_objects.items()
            }
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f)
        except Exception as e:
            st.error(f"Error saving document metadata: {str(e)}")

    def save_vectorstore(self):
        """Save vectorstore to disk"""
        try:
            if st.session_state.vectorstore:
                st.session_state.vectorstore.save_local(
                    str(self.vectorstore_path),
                    allow_dangerous_deserialization=True
                )
        except Exception as e:
            st.error(f"Error saving vectorstore: {str(e)}")

    def handle_document_upload(self, files):
        """Handle document upload and processing"""
        if not files:
            return
            
        for file in files:
            try:
                # Check if document already exists
                if file.name in st.session_state.document_objects:
                    st.warning(f"Document {file.name} already exists. Skipping...")
                    continue

                with tempfile.NamedTemporaryFile(delete=False, suffix=file.name) as tmp_file:
                    tmp_file.write(file.getvalue())
                    file_path = tmp_file.name

                # Load document based on file type
                loader = None
                if file.name.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                elif file.name.endswith('.txt'):
                    loader = TextLoader(file_path)
                elif file.name.endswith('.docx'):
                    loader = Docx2txtLoader(file_path)
                else:
                    st.error(f"Unsupported file type: {file.name}")
                    continue

                documents = loader.load()
                split_docs = self.text_splitter.split_documents(documents)
                
                # Store the actual documents
                st.session_state.document_objects[file.name] = split_docs
                
                # Update vectorstore
                if st.session_state.vectorstore is None:
                    st.session_state.vectorstore = FAISS.from_documents(
                        split_docs,
                        self.embeddings
                    )
                else:
                    st.session_state.vectorstore.add_documents(split_docs)
                
                # Save to disk
                self.save_documents_metadata()
                self.save_vectorstore()
                
                os.unlink(file_path)
                st.success(f"Successfully processed and saved {file.name}")
                
            except Exception as e:
                st.error(f"Error processing {file.name}: {str(e)}")

    @staticmethod
    def initialize_session_state():
        defaults = {
            "selected_documents": [],
            "functionality": "Select Predefined Question...",
            "user_query": "",
            "chat_history": [],
            "vectorstore": None,
            "document_objects": {},
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def process_documents(self, selected_docs):
        """Process documents and update vectorstore"""
        try:
            all_docs = []
            for doc in selected_docs:
                if doc in st.session_state.document_objects:
                    all_docs.extend(st.session_state.document_objects[doc])
            
            if all_docs:
                st.session_state.vectorstore = FAISS.from_documents(
                    all_docs,
                    self.embeddings
                )
                return True
            return False
        except Exception as e:
            st.error(f"Error processing documents: {str(e)}")
            return False

    def get_available_documents(self):
        """Get list of available documents"""
        return list(st.session_state.document_objects.keys())

    def chat_with_documents(self, query, documents):
        """Process chat query with selected documents"""
        if not documents:
            st.error("Please select some documents first!")
            return

        if not st.session_state.vectorstore:
            st.error("No vectorstore available. Please upload documents first.")
            return

        qa_chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            st.session_state.vectorstore.as_retriever(),
            return_source_documents=True
        )

        result = qa_chain({
            "question": query, 
            "chat_history": st.session_state.chat_history
        })

        st.session_state.chat_history.append((query, result["answer"]))
        return result["answer"]

    def handle_document_selection(self, documents):
        selected = st.multiselect(
            "Select documents to query",
            documents,
            key="doc_selector",
            default=st.session_state.selected_documents
        )
        
        st.session_state.selected_documents = selected
        
        # If documents are selected, use the existing vectorstore
        if selected and st.session_state.vectorstore:
            # No need to reprocess documents as they're already in the vectorstore
            return True

    def handle_functionality_selection(self):
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.session_state.functionality = st.selectbox(
                "Select predefined question...",
                ["Select Predefined Question...", "Summary", "Q&A", "Examples"],
                key="functionality_dropdown",
                label_visibility="collapsed"
            )
        with col2:
            return st.button("Run", type="primary", key="run_analysis_btn")

    def run_analysis(self):
        if st.session_state.functionality == "Summary":
            self.generate_summary()
        elif st.session_state.functionality == "Q&A":
            self.handle_qa()
        elif st.session_state.functionality == "Examples":
            self.show_examples()

    def show(self):
        col1, col2, col3 = st.columns([1, 0.2, 1.5])
        
        with col1:
            with st.expander("Upload New Document"):
                uploaded_file = st.file_uploader(
                    "Choose a file",
                    type=["pdf", "txt", "docx"],
                    accept_multiple_files=True,
                    key="file_uploader"
                )
                if uploaded_file:
                    self.handle_document_upload(uploaded_file)
            
            documents = self.get_available_documents()
            self.handle_document_selection(documents)
            
            if st.session_state.selected_documents:
                st.write("Selected documents:")
                for doc in st.session_state.selected_documents:
                    st.write(f"- {doc}")
        
        with col2:
            st.empty()
        
        with col3:
            run_analysis = self.handle_functionality_selection()
            
            if run_analysis:
                self.run_analysis()
            
            user_query = st.chat_input("Enter your question...", key="chat_input")
            if user_query:
                if not st.session_state.selected_documents:
                    st.error("Please select at least one document first!")
                else:
                    st.session_state.user_query = user_query
                    with st.spinner("Running..."):
                        try:
                            response = self.chat_with_documents(
                                user_query,
                                st.session_state.selected_documents
                            )
                            if response:
                                st.write("Answer:", response)
                            else:
                                st.error("No response received from chat function")
                        except Exception as e:
                            st.error(f"Error processing query: {str(e)}")

def show_policy():
    policy_assistant = PolicyAssistant()
    policy_assistant.show()
    
