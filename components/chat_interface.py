import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI

def chat_with_documents(query, selected_docs):
    if 'vectorstore' not in st.session_state:
        st.error("Please upload some documents first!")
        return
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    vectorstore = st.session_state.vectorstore
    
    # Initialize ChatOpenAI and ConversationalRetrievalChain
    llm = ChatOpenAI(temperature=0)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vectorstore.as_retriever(),
        return_source_documents=True
    )
    
    # Get response
    result = qa_chain({"question": query, "chat_history": st.session_state.chat_history})
    
    # Update chat history
    st.session_state.chat_history.append((query, result["answer"]))
    
    # Display response
    st.write("Answer:", result["answer"]) 