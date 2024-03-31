import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from uuid import uuid4

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks import collect_runs
from langsmith import Client
from langchain.callbacks.tracers.langchain import wait_for_all_tracers

client = Client()
    
def add_feedback(score):
    runs = client.list_runs(
        project_name="smith-project",
        run_type="chain",
    )

    current_run_id = list(runs)[0].id

    client.create_feedback(
        run_id=current_run_id,
        key="user-feedback",
        score=score,
        comment="the user's feedback"
    )

def add_positive_feedback():
    add_feedback(score=1)
    st.toast("Thanks for your feedback!")

def add_negative_feedback():
    add_feedback(score=0)
    st.toast("Thanks for your feedback!")

st.title("Echo bot")

if "llm" not in st.session_state:
    st.session_state["llm"] = ChatAnthropic(model="claude-3-haiku-20240307")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

llm = st.session_state["llm"]
output_parser = StrOutputParser()
prompt = ChatPromptTemplate.from_messages([
    ("system", "you are a helpful assistant. Please respond to the user's request"),
    ("user", "Question: {question}")
])
chain = prompt | llm | output_parser

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

feedback = None

if (question := st.chat_input("What is up?")):
    with st.chat_message("user"):
        st.markdown(question)
    
    st.session_state.messages.append({"role": "user", "content": question})
    response = chain.invoke({"question": question})

    with st.chat_message("assistant"):
        st.markdown(response)
        _, col1, col2 = st.columns([0.8, 0.1, 0.1])
        col1.button("👍", on_click=add_positive_feedback)
        col2.button("👎", on_click=add_negative_feedback)

    st.session_state.messages.append({"role": "assistant", "content": response})
