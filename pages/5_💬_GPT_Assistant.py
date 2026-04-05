import streamlit as st
import markdown
import weasyprint
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# =========================
# PAGE CONFIG (MUST BE FIRST)
# =========================
st.set_page_config(
    page_title="ChatGPT Assistant",
    page_icon="🤖"
)

#st.title("🤖 ChatGPT Assistant")

# =========================
# INIT SESSION
# =========================
if "chatgpt_messages" not in st.session_state:
    st.session_state.chatgpt_messages = []

if "llm" not in st.session_state:
    st.session_state.llm = ChatOpenAI(model="gpt-4o-mini")

# =========================
# PDF CREATION
# =========================
def create_pdf(text, filename):
    html = markdown.markdown(text)
    weasyprint.HTML(string=html).write_pdf(filename)

# =========================
# WELCOME MESSAGE
# =========================
if len(st.session_state.chatgpt_messages) == 0:
    st.markdown("""
    ## 👋 Welcome to ChatGPT Assistant

    I'm here to help you with anything!

    💡 You can ask me:
    - Technical questions  
    - Coding help  
    - Research explanations  
    - Project ideas  

    👉 Start typing below to begin!
    """)

# =========================
# CHAT DISPLAY
# =========================
for msg in st.session_state.chatgpt_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# USER INPUT
# =========================
query = st.chat_input("Ask anything...")

if query:
    st.session_state.chatgpt_messages.append({"role": "user", "content": query})

    st.toast("🤖 Thinking...", icon="💡")

    st.chat_message("user").write(query)

    # =========================
    # BUILD CONTEXT (WITH LIMIT)
    # =========================
    MAX_HISTORY = 10  # 🔥 Optional memory limit

    messages = []
    for msg in st.session_state.chatgpt_messages[-MAX_HISTORY:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))

    # =========================
    # LLM CALL WITH CONTEXT
    # =========================
    response = st.session_state.llm.invoke(messages)

    st.chat_message("assistant").write(response.content)

    st.session_state.chatgpt_messages.append(
        {"role": "assistant", "content": response.content}
    )

# =========================
# ACTION BUTTONS (ONLY IF CHAT EXISTS)
# =========================
if len(st.session_state.chatgpt_messages) > 0:

    st.divider()
    col1, col2 = st.columns(2)

    # CLEAR CHAT
    with col1:
        if st.button("🧹 Clear Chat", use_container_width=True):

            if len(st.session_state.chatgpt_messages) == 0:
                st.toast("⚠️ No chat to clear!", icon="🚫")
            else:
                st.session_state.chatgpt_messages = []
                st.toast("🗑️ Chat cleared!", icon="✅")
                st.rerun()

    # DOWNLOAD CHAT
    with col2:
        if st.button("📥 Download Chat", use_container_width=True):

            if len(st.session_state.chatgpt_messages) == 0:
                st.toast("⚠️ No chat available!", icon="🚫")
                st.stop()

            st.toast("📄 Generating PDF...", icon="⏳")

            text = ""
            q_no = 1

            for msg in st.session_state.chatgpt_messages:
                if msg["role"] == "user":
                    text += f"**Q{q_no}. {msg['content']}**\n\n"
                else:
                    text += f"**Answer:** {msg['content']}\n\n"
                    q_no += 1

            create_pdf(text, "chatgpt_chat.pdf")

            st.toast("✅ Ready!", icon="📥")

            with open("chatgpt_chat.pdf", "rb") as f:
                st.download_button(
                    "Download PDF",
                    f,
                    "chatgpt_chat.pdf",
                    use_container_width=True
                )
