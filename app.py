import streamlit as st
from groq import Groq

st.set_page_config(page_title="Groq Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 Groq AI Chatbot")
st.caption("Powered by Groq's free API + Streamlit")

# ---------------------------------------------------
# 1. Get the API key (from Streamlit secrets OR sidebar input)
# ---------------------------------------------------
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Enter your Groq API Key", type="password")
        st.markdown("[Get a free key here](https://console.groq.com/keys)")

if not api_key:
    st.info("👈 Please add your Groq API key in the sidebar (or in secrets.toml) to start chatting.")
    st.stop()

client = Groq(api_key=api_key)

# ---------------------------------------------------
# 2. Model + settings (sidebar)
# ---------------------------------------------------
with st.sidebar:
    st.header("Model Settings")
    model = st.selectbox(
        "Model",
        [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
            "groq/compound-mini",
	    "groq/compound",
        ],
        index=0,
    )
    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful, friendly assistant.",
        height=100,
    )
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)

    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------
# 3. Chat history in session state
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------
# 4. Chat input + response streaming
# ---------------------------------------------------
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"⚠️ Error: {e}"
            placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
