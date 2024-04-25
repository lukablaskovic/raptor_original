import os
import streamlit as st
import fitz

# Set OpenAI API key via sidebar
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.error("Please provide your OpenAI API key.")
    st.stop()

os.environ['OPENAI_API_KEY'] = openai_api_key

from raptor import RetrievalAugmentation

st.sidebar.title("File Upload")
uploaded_file = st.sidebar.file_uploader("Upload your document:", type=['txt', 'pdf'])

st.title("🦖 RAPTOR Document Search!")

"""
This is demo of RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval.
GPT-3 Turbo is used as the underlying summarization and question-answering model.
"""

def process_document(uploaded_file):
    if uploaded_file.type == "application/pdf":
        # Open and read the PDF file
        doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
        text = "".join(page.get_text() for page in doc)
    else:
        # Read the uploaded text file
        text = str(uploaded_file.getvalue(), 'utf-8')
    return text

if uploaded_file:
    filename = uploaded_file.name
    base_filename = os.path.splitext(filename)[0]
    SAVE_PATH = f"demo/{base_filename}" 
    if os.path.exists(SAVE_PATH):
        # Load existing RAPTOR structure
        RA = RetrievalAugmentation(tree=SAVE_PATH)
        st.info("Loaded saved RAPTOR structure: f{SAVE_PATH}.")
    else:
        # Process new document and create new RAPTOR structure
        text = process_document(uploaded_file)
        RA = RetrievalAugmentation()
        RA.add_documents(text)
        RA.save(SAVE_PATH)
        st.success("Document uploaded and processed for retrieval!")

# CHATBOT
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi, I'm RAPTOR! 🦖 What can I do for you today?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask me a question about the document..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    if uploaded_file and 'RA' in locals():
        try:
            answer = RA.answer_question(question=prompt)
            print(answer)
            if answer:
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.chat_message("assistant").write(answer)
            else:
                st.session_state.messages.append({"role": "assistant", "content": "I couldn't find an answer to that question."})
                st.chat_message("assistant").write("I couldn't find an answer to that question.")
                
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Please upload a document to continue."})
    