import streamlit as st

# Simple rule-based chatbot function
def chatbot_response(user_message):
    user_message = user_message.lower().strip()

    if user_message in ["hi", "hello", "hey", "start"]:
        return "👋 Hello! How can I help you today?"

    elif "store hours" in user_message or user_message == "1":
        return "🕘 We're open 9 AM – 9 PM, Monday to Saturday."

    elif "track order" in user_message or user_message == "2":
        return "📦 Sure! What's your order number?"

    elif "talk to agent" in user_message or user_message == "3":
        return "📞 Okay, I’m forwarding you to our human support staff."

    else:
        return "❓ Sorry, I didn’t understand that. Please choose an option."

# Streamlit UI
st.set_page_config(page_title="Simple Chatbot", page_icon="🤖")

st.title("🤖 Rule-Based Chatbot with Buttons")
st.write("Click a button or type your message below to chat with the bot.")

# Keep conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation
for role, msg in st.session_state.messages:
    if role == "You":
        st.markdown(f"**🧑 {role}:** {msg}")
    else:
        st.markdown(f"**🤖 {role}:** {msg}")

# Input section
user_input = st.text_input("Type your message:", "")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🕘 Store Hours"):
        user_input = "Store Hours"

with col2:
    if st.button("📦 Track Order"):
        user_input = "Track Order"

with col3:
    if st.button("📞 Talk to Agent"):
        user_input = "Talk to Agent"

# Process input
if user_input:
    # Append user message
    st.session_state.messages.append(("You", user_input))

    # Get bot reply
    bot_reply = chatbot_response(user_input)
    st.session_state.messages.append(("Bot", bot_reply))

    # Clear input box
    st.experimental_rerun()
