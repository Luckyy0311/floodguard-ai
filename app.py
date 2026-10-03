import streamlit as st

from agent.core import FloodAgent


st.set_page_config(
    page_title="FloodGuard AI",
    page_icon="🌊",
    layout="wide"
)


@st.cache_resource(show_spinner=False)
def create_agent():
    return FloodAgent()


agent = create_agent()


def render_answer(result):
    if isinstance(result, str):
        st.markdown(result)
        return

    answer = result.get("answer", "No answer returned.")
    risk_level = result.get("risk_level", "unknown")
    actions = result.get("actions", [])
    sources = result.get("sources", [])
    trace = result.get("trace", [])

    st.markdown(answer)

    col1, col2, col3 = st.columns([1, 1, 1])

    col1.metric("Risk Level", risk_level)

    if isinstance(actions, list) and actions:
        st.subheader("Recommended Actions")
        for action in actions:
            st.markdown(f"- {action}")

    if isinstance(sources, list) and sources:
        st.subheader("Sources")
        for source in sources:
            st.markdown(f"- {source}")

    if trace:
        with st.expander("Agent Tool Trace"):
            st.json(trace)

    st.caption(
        "Disclaimer: This is an AI-assisted decision support tool. "
        "Always follow official emergency instructions."
    )


st.sidebar.title("FloodGuard Settings")

default_location = st.sidebar.text_input(
    "Default Location",
    value="Chennai"
)

st.sidebar.caption(
    "Used when the chat question does not explicitly mention a location."
)

if st.sidebar.button("Rebuild Knowledge Base"):
    count = agent.store.build()
    st.sidebar.success(f"Knowledge base rebuilt with {count} chunks.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Live Risk Check")

if st.sidebar.button("Run Live Risk Check"):
    prompt = (
        f"Assess current flood risk for {default_location}. "
        "Provide risk level and immediate actions."
    )

    with st.spinner("Checking live weather, alerts, and preparedness docs..."):
        result = agent.run(prompt, default_location)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    st.session_state.messages.append({
        "role": "assistant",
        "content": result
    })


st.title("🌊 FloodGuard AI")

st.write(
    "Real-time flood risk assessment using live weather, official alerts, "
    "RAG-based preparedness knowledge, and agentic AI planning."
)


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]

    with st.chat_message(role):
        if role == "assistant" and isinstance(content, dict):
            render_answer(content)
        else:
            st.markdown(content)


prompt = st.chat_input(
    "Ask about flood risk, evacuation, or emergency preparation..."
)

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent is reasoning..."):
            result = agent.run(prompt, default_location)

        render_answer(result)

    st.session_state.messages.append({
        "role": "assistant",
        "content": result
    })