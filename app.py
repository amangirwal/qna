import streamlit as st
import os
import pandas as pd
from database import (
    init_db, add_question, get_questions, add_answer, get_answers
)

# Initialize the database
init_db()

# File upload path
UPLOAD_PATH = "uploads"
os.makedirs(UPLOAD_PATH, exist_ok=True)

# Page configuration
st.set_page_config(page_title="DAA Questions", layout="wide")

# Sidebar navigation
st.sidebar.title("DAA questions")
options = ["Ask a Question", "View Questions"]
selection = st.sidebar.radio("Navigation", options)

if selection == "Ask a Question":
    st.title("Ask a Question")

    # Question Input (optional)
    question_text = st.text_area("Enter your question ():")
    uploaded_files = st.file_uploader("Upload media files ():", accept_multiple_files=True)

    if st.button("Submit"):
        file_paths = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(UPLOAD_PATH, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                file_paths.append(file_path)
        
        # Add question to the database (even if no text is provided)
        add_question(question_text, ",".join(file_paths) if file_paths else None)
        st.success("Question submitted successfully!")

elif selection == "View Questions":
    st.title("All Questions")
    questions = get_questions()

    for question in questions:
        st.subheader(f"Question: {question['text'] if question['text'] else 'No text provided'}")
        
        # Display media if exists
        if question['media']:
            media_files = question['media'].split(",")
            for media_file in media_files:
                file_ext = os.path.splitext(media_file)[-1]
                if file_ext in ['.png', '.jpg', '.jpeg']:
                    st.image(media_file)
                elif file_ext in ['.mp4', '.webm']:
                    st.video(media_file)
                else:
                    st.download_button("Download Attachment", open(media_file, 'rb'), media_file.split('/')[-1])

        # Show answers
        answers = get_answers(question['id'])
        if answers:
            st.write("**Answers:**")
            for answer in answers:
                # Toggle answer visibility
                if st.button(f"View Answer for Q{question['id']}-A{answer['id']}", key=f"view_{question['id']}_{answer['id']}"):
                    st.code(answer['text'], language="text")
        else:
            st.write("*No answers yet.*")

        # Answer input
        answer_text = st.text_area(f"Your Answer for Q{question['id']}", key=question['id'])
        if st.button(f"Submit Answer for Q{question['id']}", key=f"submit_{question['id']}"):
            if answer_text.strip():
                add_answer(question['id'], answer_text)
                st.success("Answer submitted successfully!")
            else:
                st.error("Please enter a valid answer.")