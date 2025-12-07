import streamlit as st
import requests
from typing import Optional

# API base URL
API_BASE_URL = "http://localhost:8000"


def main():
    st.set_page_config(
        page_title="SDS Digest",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 SDS Digest - Safety Data Sheet Processor")
    st.markdown("Upload and process Safety Data Sheets to extract structured data, summaries, and answer questions.")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Upload SDS", "View Structured Extract", "View Summary", "Ask Questions"]
    )
    
    if page == "Upload SDS":
        upload_page()
    elif page == "View Structured Extract":
        view_structured_page()
    elif page == "View Summary":
        view_summary_page()
    elif page == "Ask Questions":
        ask_questions_page()


def upload_page():
    st.header("Upload Safety Data Sheet")
    st.markdown("Upload a PDF file containing a Safety Data Sheet for processing.")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Select a Safety Data Sheet PDF file"
    )
    
    if uploaded_file is not None:
        st.info(f"Selected file: {uploaded_file.name}")
        
        if st.button("Upload and Process", type="primary"):
            with st.spinner("Uploading and processing SDS..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(f"{API_BASE_URL}/api/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ {data['message']}")
                        st.info(f"**SDS ID:** `{data['sds_id']}`")
                        st.session_state["current_sds_id"] = data["sds_id"]
                        st.session_state["sds_uploaded"] = True
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"Error uploading file: {str(e)}")


def view_structured_page():
    st.header("View Structured Extract")
    st.markdown("View the structured JSON representation of a processed SDS.")
    
    sds_id = get_sds_id()
    
    if sds_id:
        if st.button("Load Structured Extract", type="primary"):
            with st.spinner("Loading structured extract..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/api/sds/{sds_id}/structured")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success("✅ Structured extract loaded")
                        
                        # Display structured content
                        st.subheader("Structured Content")
                        st.json(data["structured_content"])
                        
                        # Display sections if available
                        if data.get("sections"):
                            st.subheader("Sections")
                            for i, section in enumerate(data["sections"], 1):
                                with st.expander(f"Section {i}: {section.get('section_title', 'Unknown')}"):
                                    st.json(section)
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"Error loading structured extract: {str(e)}")


def view_summary_page():
    st.header("View Summary")
    st.markdown("View a concise summary of the chemical described in the SDS.")
    
    sds_id = get_sds_id()
    
    if sds_id:
        if st.button("Load Summary", type="primary"):
            with st.spinner("Loading summary..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/api/sds/{sds_id}/summary")
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success("✅ Summary loaded")
                        st.markdown("### Summary")
                        st.markdown(data["summary"])
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"Error loading summary: {str(e)}")


def ask_questions_page():
    st.header("Ask Questions")
    st.markdown("Ask questions about the chemical details in the SDS.")
    
    sds_id = get_sds_id()
    
    if sds_id:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Question input
        question = st.chat_input("Ask a question about the SDS...")
        
        if question:
            # Add user question to chat
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            # Get answer from API
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/sds/{sds_id}/ask",
                            json={"question": question}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer = data["answer"]
                            st.markdown(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        else:
                            error_msg = f"Error: {response.json().get('detail', 'Unknown error')}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    except requests.exceptions.ConnectionError:
                        error_msg = "❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})


def get_sds_id() -> Optional[str]:
    """Get SDS ID from session state or user input"""
    if "current_sds_id" in st.session_state:
        st.info(f"Current SDS ID: `{st.session_state['current_sds_id']}`")
        return st.session_state["current_sds_id"]
    else:
        sds_id = st.text_input(
            "Enter SDS ID",
            help="Enter the SDS ID from a previous upload, or upload a new SDS first"
        )
        if sds_id:
            return sds_id
        else:
            st.warning("⚠️ Please upload an SDS first or enter an SDS ID")
            return None


if __name__ == "__main__":
    main()

