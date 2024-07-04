import os
from PyPDF2 import PdfReader
import streamlit as st
import google.generativeai as genai

GEMINI_API_KEY=st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=GEMINI_API_KEY)



def get_pdf_text(pdf_docs):
    
    
    text_dict = {}

    for pdf in pdf_docs:
        try: 
            text=''

            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                try:
                    

                    text += page.extract_text()
                except Exception as e:
                    st.sidebar.error(e)
                
            text_dict[pdf.name]=text
        except Exception as e:
            st.sidebar.error(f"cannot upload {pdf} : {e}")
        
    return text_dict

def get_conversational_res(context, question, chat_hist):
    """Generate a response from the conversational AI model."""
    generation_config = {
        "temperature": 0.4,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    prompt = f"""
    You are a professional chatbot. Understand the below *CONTEXT* and answer the queries asked by the users.

    ## Instructions:
    - Keep the result simple and well-structured. Use headings and subheadings and points to make it readable.
    - You can include tables and other methods to make the user comfortable in reading and acquiring knowledge.
    - Try to be professional, do not mention or include any instructions provided to you.
    - Response sholud be concise and to the point.
    - Respond in a friendly way while user greets you.(like: [how are you, hii, thank you])

    ## CONTEXT: '''\n {context}?\n'''
    """
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=prompt,
    )

    chat_session = model.start_chat(
        history=chat_hist
    )
    
    
    response = chat_session.send_message(question)
    chat_hist.append({"role": "user", "parts": [question]})
    chat_hist.append({"role": "model", "parts": [response.text]})
    return response.text

def clear_chat_history():
    """Clear the chat history."""
    st.session_state.messages = [
        {"role": "assistant", "content": "Please upload your PDFs and feel free to ask any questions you have."}
    ]

def main():
    
    st.set_page_config(
        page_title="Doc Genius",
        page_icon="📚"
    )

    chat_hist = []

    
    with st.sidebar:
        st.markdown("""
        <div style="display: block; font-size: 25px; font-weight: bold; padding: 5px 10px; border: 4px double #0077cc; color: #ff9900; text-align: center; border-radius: 10px; background-color: rgba(255, 255, 255, 0.5); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);">
            Doc Genius
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        
        pdf_docs = st.file_uploader(
            "Upload your PDF Files",type='pdf', accept_multiple_files=True)
        
        if st.button("Submit & Process"):
            chat_hist = []
            if len(pdf_docs)!=0:
                with st.spinner("Processing..."):
                    raw_text=get_pdf_text(pdf_docs)
                    st.session_state.raw_text = raw_text
                    st.success("Done")
            else:
                st.warning("Upload atleast one pdf.")

    # raw_text=get_pdf_text(pdf_docs)
    st.subheader("Doc Genius", divider='rainbow')
    
    st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
    try:
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello, how may I help you? 😊"}
            ]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = get_conversational_res(st.session_state.raw_text , prompt, chat_hist)
                    st.write(response)
                    
            
            if response:
                message = {"role": "assistant", "content": response}
                st.session_state.messages.append(message)
    except Exception as e:
        st.error(e)

if __name__ == "__main__":
    main()
