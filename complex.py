import streamlit as st
import time

# --------------------------
# Rule-based Chatbot with More Features
# --------------------------

def chatbot_response(user_message):
    user_message = user_message.lower().strip()

    # Greeting
    if user_message in ["hi", "hello", "hey", "start"]:
        if "user_name" in st.session_state and st.session_state.user_name:
            return f"👋 Welcome back, {st.session_state.user_name}! How can I help you today?"
        return "👋 Hello! I’m your TESDA Assistant. What’s your name?"

    # Capture name if not stored yet
    if "user_name" not in st.session_state or not st.session_state.user_name:
        st.session_state.user_name = user_message.capitalize()
        return f"✅ Nice to meet you, {st.session_state.user_name}! How can I assist you today? \n\n1️⃣ Create Account \n2️⃣ View Courses \n3️⃣ FAQs \n4️⃣ Talk to Agent"

    # Main options
    if user_message in ["1", "create account"]:
        return "📝 You can create an account here: [TESDA Signup](https://e-tesda.gov.ph/login/signup.php)"

    elif user_message in ["2", "courses", "view courses"]:
        return "📦 Explore available courses here: [TESDA Courses](https://e-tesda.gov.ph/course)"

    elif user_message in ["3", "faq", "faqs"]:
        return "❓ FAQ Options: \n- requirements \n- duration \n- certification"

    elif user_message in ["4", "talk to agent", "agent"]:
        return "📞 Okay, I’m connecting you to our human support staff."

    # FAQs
    elif "requirements" in user_message:
        return "📝 TESDA courses usually require: Valid ID, Birth Certificate, and 1x1 photo."

    elif "duration" in user_message:
        return "⏳ Most TESDA short courses last 20–40 hours, while full programs may take months."

    elif "certification" in user_message:
        return "🎓 After completing a course, you’ll receive a TESDA National Certificate (NC)."

    # Small talk
    elif user_message in ["thank you", "thanks"]:
        return "😊 You’re welcome! Glad to assist."

    elif user_message in ["bye", "goodbye", "exit"]:
        return "👋 Goodbye! Hope to see you again soon."

    elif "who are you" in user_message:
        return "🤖 I’m a simple TESDA rule-based chatbot here to guide you."

    # Fallback
    else:
        return "❓ Sorry, I didn’t get that. Please choose: \n1️⃣ Create Account \n2️⃣ View Courses \n3️⃣ FAQs \n4️⃣ Talk to Agent"

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="Enhanced Rule-Based Chatbot", page_icon="🤖", layout="wide")

# --------------------------
# Sidebar for info
# --------------------------
with st.sidebar:
    st.title("ℹ️ About this Chatbot")
    st.write("This is an **enhanced rule-based chatbot** built with Streamlit. It supports:")
    st.markdown("""
    - 👋 Greetings & remembers your name  
    - 📝 Account creation link  
    - 📦 Courses information  
    - ❓ FAQs (requirements, duration, certification)  
    - 📞 Connect to a human agent  
    - 💬 Small talk (thanks, bye, etc.)  
    """)
    st.success("💡 Tip: Type 'start' to begin.")

# --------------------------
# Main Title
# --------------------------
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🤖 Enhanced Rule-Based Chatbot</h1>", unsafe_allow_html=True)
st.write("Interact with the chatbot by clicking a button or typing your message.")

# --------------------------
# Conversation History
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Reset chat
if st.button("🔄 Reset Chat"):
    with st.spinner("Clearing chat..."):
        time.sleep(1)
    st.session_state.messages = []
    st.session_state.user_name = ""
    st.rerun()

# --------------------------
# Display Chat Bubbles
# --------------------------
for role, msg in st.session_state.messages:
    if role == "You":
        st.markdown(
            f"<div style='background-color:#DCF8C6; padding:10px; border-radius:15px; margin:5px; text-align:right;'>"
            f"🧑 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background-color:#E6E6FA; padding:10px; border-radius:15px; margin:5px; text-align:left;'>"
            f"🤖 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )

# --------------------------
# Input Section
# --------------------------
st.markdown("### ✍️ Type your message or use quick actions:")

user_input = st.text_input("Type your message here:", "")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📝 Create Account"):
        user_input = "create account"

with col2:
    if st.button("📦 Courses"):
        user_input = "courses"

with col3:
    if st.button("❓ FAQs"):
        user_input = "faq"

with col4:
    if st.button("📞 Talk to Agent"):
        user_input = "talk to agent"

# --------------------------
# Process Input
# --------------------------
if user_input:
    # Append user message
    st.session_state.messages.append(("You", user_input))

    # Simulate typing
    with st.spinner("Bot is typing..."):
        time.sleep(1.2)

    # Bot reply
    bot_reply = chatbot_response(user_input)
    st.session_state.messages.append(("Bot", bot_reply))

    # Refresh UI
    st.rerun()
