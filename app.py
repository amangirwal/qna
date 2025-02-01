import streamlit as st
import os
import sqlite3

# Database Path
DB_PATH = "qna.db"
UPLOAD_PATH = "uploads"
os.makedirs(UPLOAD_PATH, exist_ok=True)

# Admin Password (Change as needed)
ADMIN_PASSWORD = "computer"
# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            media TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Sidebar for Admin Login
st.sidebar.title("Admin Panel")
admin_password = st.sidebar.text_input("Enter Admin Password:", type="password")
is_admin = admin_password == ADMIN_PASSWORD

# Sidebar Navigation
st.sidebar.title("DAA Questions")
options = ["Ask a Question", "View Questions"]
selection = st.sidebar.radio("Navigation", options)

if selection == "Ask a Question":
    st.title("Ask a Question")
    question_text = st.text_area("Enter your question:")
    uploaded_files = st.file_uploader("Upload media files:", accept_multiple_files=True)
    
    if st.button("Submit"):
        file_paths = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(UPLOAD_PATH, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                file_paths.append(file_path)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO questions (text, media) VALUES (?, ?)", (question_text, ",".join(file_paths) if file_paths else None))
        conn.commit()
        conn.close()
        st.success("Question submitted successfully!")

elif selection == "View Questions":
    st.title("All Questions")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    
    for question in questions:
        q_id, q_text, q_media = question
        st.subheader(f"Question: {q_text if q_text else 'No text provided'}")
        
        if q_media:
            media_files = q_media.split(",")
            for media_file in media_files:
                file_ext = os.path.splitext(media_file)[-1]
                if file_ext in ['.png', '.jpg', '.jpeg']:
                    st.image(media_file)
                elif file_ext in ['.mp4', '.webm']:
                    st.video(media_file)
                else:
                    st.download_button("Download Attachment", open(media_file, 'rb'), media_file.split('/')[-1])
        
        cursor.execute("SELECT * FROM answers WHERE question_id = ?", (q_id,))
        answers = cursor.fetchall()
        if answers:
            st.write("**Answers:**")
            for ans in answers:
                ans_id, _, ans_text = ans
                st.code(ans_text, language="text")
                if is_admin:
                    if st.button(f"Delete Answer {ans_id}", key=f"delete_ans_{ans_id}"):
                        cursor.execute("DELETE FROM answers WHERE id = ?", (ans_id,))
                        conn.commit()
                        st.rerun()
        else:
            st.write("*No answers yet.*")
        
        answer_text = st.text_area(f"Your Answer for Q{q_id}", key=q_id)
        if st.button(f"Submit Answer for Q{q_id}", key=f"submit_{q_id}"):
            if answer_text.strip():
                cursor.execute("INSERT INTO answers (question_id, text) VALUES (?, ?)", (q_id, answer_text))
                conn.commit()
                st.success("Answer submitted successfully!")
                st.rerun()
            else:
                st.error("Please enter a valid answer.")
        
        if is_admin:
            if st.button(f"Delete Question {q_id}", key=f"delete_q_{q_id}"):
                cursor.execute("DELETE FROM answers WHERE question_id = ?", (q_id,))
                cursor.execute("DELETE FROM questions WHERE id = ?", (q_id,))
                conn.commit()
                st.rerun()
    
    conn.close()
