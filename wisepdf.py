import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# Securely access the OpenAI API key from Streamlit's secrets
OpenAI.api_key = "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"

st.title("WISE PDF - Intelligent Book Reader")

# Set up the system message for the AI
messages = [
    {
        "role": "system",
        "content": (
            "You are an AI that reads PDF files or parts of them and provides summaries. "
            "You highlight key points and answer questions only based on the provided text."
        )
    }
]

# Function to handle PDF text extraction
def extract_text_from_pdf(reader, start, end):
    text = ""
    for i in range(start, end):
        page = reader.pages[i]
        page_text = page.extract_text() or ""
        text += page_text
    return text

# Handle file upload and user-defined interval
uploaded_file = st.file_uploader("Upload a PDF book", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    total_pages = len(reader.pages)
    start, end = 0, total_pages
    submitted = False  # Track form submission
    
    # Set up page range selection only if file has more than 40 pages
    if total_pages > 40:
        st.warning(f"The file has {total_pages} pages. Only 40 pages can be processed at once.")
        with st.form("interval_selection"):
            slider_range = st.slider("Select page range (Max 40 pages)", 0, total_pages, (0, min(40, total_pages)))
            start, end = slider_range
            
            # Show error message if the selected range is greater than 40 pages
            if (end - start) > 40:
                st.error("Selected range exceeds 40 pages. Please select a range of up to 40 pages.")
                submitted = False  # Prevent form submission on invalid range
            else:
                submitted = st.form_submit_button("Read Selected Pages")
    else:
        # Automatically set to True if total pages are within limit and no form needed
        submitted = True

    # Process the PDF if the selected range is within the limit and form is submitted
    if submitted and (end - start) <= 40:
        extracted_text = extract_text_from_pdf(reader, start, end)
        if extracted_text:
            messages.append({"role": "user", "content": extracted_text})
    elif submitted:
        st.error("Selected range exceeds the allowed limit of 40 pages. Adjust the range and resubmit.")

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display stored messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input for user questions
user_input = st.chat_input("Ask a question about the book")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Append user prompt to messages for API request
    messages.append({"role": "user", "content": user_input})

    # Call OpenAI API to generate response
    try:
        client = OpenAI()
        chat = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        assistant_reply = chat.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_reply})

        # Display and store the assistant's response
        with st.chat_message("WISE PDF"):
            st.markdown(assistant_reply)
        st.session_state.messages.append({"role": "WISE PDF", "content": assistant_reply})
    except Exception as e:
        st.error(f"An error occurred: {e}")