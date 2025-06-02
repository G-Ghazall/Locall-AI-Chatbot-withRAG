import streamlit as st 
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever
import pandas as pd
from datetime import datetime
import re

def format_documents(docs):
    formatted = []
    for doc in docs:
        content = doc.page_content.strip()
        source = doc.metadata.get("source", "unknown source")
        formatted.append(f"[From {source}]\n{content}")
    return "\n\n".join(formatted)

experts_df = pd.read_excel("experts-info.xlsx")
experts = {}
for _, row in experts_df.iterrows():
    raw_topics = str(row["Topic"]).split(",") if not pd.isna(row["Topic"]) else []
    for topic in raw_topics:
        topic_key = topic.strip().lower()
        experts[topic_key] = {
            "name": str(row["Name"]).strip() if not pd.isna(row["Name"]) else "N/A",
            "role": str(row["Role"]).strip() if not pd.isna(row["Role"]) else "N/A",
            "email": str(row["Email"]).strip() if not pd.isna(row["Email"]) else "N/A"
        }

experts_list = "\n".join([
    f"- {v['name']} ({v['role']}), email: {v['email']} — topic: {k.title()}"
    for k, v in experts.items()
])

topic_keywords = {
    # You can add keywords for simple topic detection for example:
    "ethics": ["ethics", "bribery", "inclusion", "code of conduct"],
    "technical support": ["support", "helpdesk", "issue", "it", "problem"]
}

current_time = datetime.now().strftime("%A, %B %d, %Y at %H:%M")

model = OllamaLLM(model="llama3.1")
template = """
You are an expert assistant helping employees at a company by answering questions about the company and its policies, tools, and projects.

Your task is to answer the question based on the information provided.
First, read the information and then answer the question.

If you need more information, ask for more.
If you don’t know the answer, say "I don't have information about this from company data".

The current date and time is: {time} 
Do not mention the date or time unless the user specifically asks about the date, time, day, or schedule.

Here is the company info: {info}

Recent chat context (if relevant):{chat_context}

Experts available and their contact and emails: {experts_list}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

st.set_page_config(page_title="Privat Chatbot", page_icon="🤖", layout="wide")

st.image("logo1.png",  width=240)

st.markdown("<h4 style='font-size:20px;'>Ask your Question here!</h4>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "memory" not in st.session_state:
    st.session_state.memory = []
    
chat_col, side_col = st.columns([2, 1])

with chat_col:
    question = st.chat_input("Ask your question about the company...")

    if question:
        lower_q = question.strip().lower()
        greetings = ["hi", "hello", "hej", "hey", "good morning", "good evening", "good afternoon"]

        if any(re.fullmatch(greet, lower_q) for greet in greetings):
            response = "Hi! 👋 Hope you're having a great day. I'm here to help you with anything about the company."
        else:
            with st.spinner("Thinking..."):
                docs = retriever.invoke(question)
                info = format_documents(docs)

                chat_context = ""
                for q, a in st.session_state.memory[-2:]:
                    chat_context += f"Previous question: {q}\nPrevious answer: {a}\n\n"


                response = chain.invoke({
                    "info": info,
                    "question": question,
                    "time": current_time,
                    "experts_list": experts_list,
                    "chat_context": chat_context.strip()
                })

                matched_topic = None
                for topic, keywords in topic_keywords.items():
                    if any(keyword in lower_q for keyword in keywords):
                        matched_topic = topic
                        break

                if matched_topic and matched_topic in experts:
                    expert = experts[matched_topic]
                    response += (
                        f"\n\n📇 You can also contact **{expert['name']}**, {expert['role']} for further help:\n"
                        f"📧 {expert['email']}"
                    )

        st.session_state.chat_history.append(("You", question))
        st.session_state.chat_history.append(("Bot", response))

        st.session_state.memory.append((question, response))
        if len(st.session_state.memory) > 2:
            st.session_state.memory.pop(0)

    for role, message in reversed(st.session_state.chat_history):
        with st.chat_message(role.lower()):
            if role == "You":
                st.markdown(
                    f"""
                    <div style='border:1px solid #888; padding:8px; border-radius:6px; background-color:rgba(255,255,255,0.0); font-size: 17px;'>
                        {message}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(message)

with side_col:
    st.markdown("<h5 style='font-size:18px;'>Sample Topics Covered</h5>", unsafe_allow_html=True)
    
    # you can add the 'Topics include' here such as:
    st.markdown("""
    - IT Support & Onboarding  
    - Ethics & Conduct Policy   
    """)

    st.markdown("---")
    st.markdown("<h5 style='font-size:18px;'>Chat History</h5>", unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []

    for role, message in reversed(st.session_state.chat_history):
        label = "You" if role == "You" else "Bot"
        st.markdown(f"**{label}:** {message[:80]}{'...' if len(message) > 80 else ''}")

