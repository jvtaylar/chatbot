import streamlit as st
import time

# --------------------------
# Simple rule-based chatbot function
# --------------------------
def chatbot_response(user_message):
    user_message = user_message.lower().strip()

    if user_message in ["hi", "hello", "hey", "start"]:
        return "👋 Hello! How can I help you today?"

    elif "create account" in user_message or user_message == "1":
        return "📝 You can create an account here: [TESDA Signup](https://e-tesda.gov.ph/login/signup.php)"

    elif "courses" in user_message or user_message == "2":
        return "📦 Sure! Explore the available courses here: [TESDA Courses](https://e-tesda.gov.ph/course)"

    elif "talk to agent" in user_message or user_message == "3":
        return "📞 Okay, I’m connecting you to our human support staff."

    else:
        return "❓ Sorry, I didn’t understand that. Please choose an option below."

# --------------------------
# Streamlit Page Config
# --------------------------
st.set_page_config(page_title="Simple Chatbot", page_icon="🤖", layout="wide")

# --------------------------
# Sidebar for info
# --------------------------
with st.sidebar:
    st.title("ℹ️ About this Chatbot")
    st.write("This is a simple **rule-based chatbot** built with Streamlit. You can:")
    st.markdown("""
    - 👋 Greet the bot  
    - 📝 Create an account  
    - 📦 View courses  
    - 📞 Talk to a human agent  
    """)
    st.success("💡 Tip: Use the quick buttons for faster interaction!")

# --------------------------
# Main Title
# --------------------------
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🤖 Rule-Based Chatbot</h1>", unsafe_allow_html=True)
st.write("Interact with the chatbot by clicking a button or typing your message.")

# --------------------------
# Conversation History
# --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Reset chat button with animation
if st.button("🔄 Reset Chat"):
    with st.spinner("Clearing chat..."):
        time.sleep(1)
    st.session_state.messages = []

# --------------------------
# Input Section
# --------------------------
st.markdown("### ✍️ Type your message or use quick actions:")

user_input = st.text_input("Type your message here:", key="user_input")

col1, col2, col3 = st.columns(3)

if col1.button("📝 Create Account"):
    user_input = "create account"

if col2.button("📦 Courses"):
    user_input = "courses"

if col3.button("📞 Talk to Agent"):
    user_input = "talk to agent"

# --------------------------
# Process User Input
# --------------------------
if user_input:
    # Append user message
    st.session_state.messages.append(("You", user_input))

    # Simulate typing effect
    with st.spinner("Bot is typing..."):
        time.sleep(1.0)

    # Get bot reply
    bot_reply = chatbot_response(user_input)
    st.session_state.messages.append(("Bot", bot_reply))

    # Clear text input after processing
    st.session_state.user_input = ""

# --------------------------
# Display Chat Conversation with Bubbles
# --------------------------
for role, msg in st.session_state.messages:
    if role == "You":
        st.markdown(
            f"<div style='background-color:#DCF8C6; padding:10px; border-radius:15px; "
            f"margin:5px; text-align:right;'>"
            f"🧑 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div style='background-color:#E6E6FA; padding:10px; border-radius:15px; "
            f"margin:5px; text-align:left;'>"
            f"🤖 <b>{role}:</b> {msg}</div>",
            unsafe_allow_html=True,
        )
