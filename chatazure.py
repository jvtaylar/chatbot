# import streamlit as st
# import openai
# import os

# # --- Azure OpenAI Configuration ---
# openai.api_type = "azure"
# openai.api_base = os.getenv("https://mykey-taylar.openai.azure.com/")
# openai.api_version = "2023-05-15"
# openai.api_key = os.getenv("2BgEjqFAUmro4SVK2oRkkzfbRBRxRkWjF3v9DOspo0ututcy3aleJQQJ99BIACYeBjFXJ3w3AAABACOGk4df")
# DEPLOYMENT_NAME = os.getenv("Mykey-taylar")  # Your Azure deployment name

# # --- Streamlit UI ---
# st.set_page_config(page_title="Copilot-Style Chatbot", page_icon="🤖")
# st.title("🤖 Copilot-Style AI Chatbot")
# st.write("Custom AI assistant powered by Azure OpenAI. Use the buttons or type your questions.")

# # --- Preset options for quick prompts ---
# preset_options = [
#     "Summarize this text.",
#     "Explain a technical concept in simple terms.",
#     "Generate a code snippet in Python.",
#     "Draft an email to a client.",
#     "Provide a motivational quote."
# ]

# # --- Conversation history ---
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "system", "content": "You are a helpful AI assistant, like Microsoft Copilot. Always provide clear, concise, and actionable responses."}
#     ]

# # Display past messages
# for msg in st.session_state.messages:
#     if msg["role"] == "user":
#         st.markdown(f"**🧑 You:** {msg['content']}")
#     elif msg["role"] == "assistant":
#         st.markdown(f"**🤖 Bot:** {msg['content']}")

# # --- Preset buttons ---
# st.write("### Quick Actions:")
# cols = st.columns(len(preset_options))
# for i, option in enumerate(preset_options):
#     if cols[i].button(option):
#         user_input = option
#         st.session_state.messages.append({"role": "user", "content": user_input})

#         try:
#             response = openai.ChatCompletion.create(
#                 deployment_id=DEPLOYMENT_NAME,  # Correct for Azure
#                 messages=st.session_state.messages,
#                 temperature=0.7,
#                 max_tokens=500
#             )
#             reply = response.choices[0].message["content"].strip()
#         except Exception as e:
#             reply = f"⚠️ Error: {e}"

#         st.session_state.messages.append({"role": "assistant", "content": reply})
#         st.rerun()

# # --- User text input ---
# user_input = st.text_input("Or type your question here:")

# if st.button("Send") and user_input.strip():
#     st.session_state.messages.append({"role": "user", "content": user_input})

#     try:
#         response = openai.ChatCompletion.create(
#             deployment_id=DEPLOYMENT_NAME,  # Correct for Azure
#             messages=st.session_state.messages,
#             temperature=0.7,
#             max_tokens=500
#         )
#         reply = response.choices[0].message["content"].strip()
#     except Exception as e:
#         reply = f"⚠️ Error: {e}"

#     st.session_state.messages.append({"role": "assistant", "content": reply})
#     st.rerun()

# # --- Reset Chat ---
# if st.button("🔄 Reset Chat"):
#     st.session_state.messages = [
#         {"role": "system", "content": "You are a helpful AI assistant, like Microsoft Copilot. Always provide clear, concise, and actionable responses."}
#     ]
#     st.rerun()

import streamlit as st
import openai
import os

# --- Azure OpenAI Configuration ---
openai.api_type = "azure"
openai.api_base = os.getenv("https://mykey-taylar.openai.azure.com/")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("2BgEjqFAUmro4SVK2oRkkzfbRBRxRkWjF3v9DOspo0ututcy3aleJQQJ99BIACYeBjFXJ3w3AAABACOGk4df")
DEPLOYMENT_NAME = os.getenv("Azure subscription 1")  # Your Azure deployment name

# --- Streamlit UI ---
st.set_page_config(page_title="Copilot-Style Chatbot", page_icon="🤖")
st.title("🤖 Copilot-Style AI Chatbot")
st.write("Custom AI assistant powered by Azure OpenAI. Use the buttons or type your questions.")

# --- Preset options for quick prompts ---
preset_options = [
    "Summarize this text.",
    "Explain a technical concept in simple terms.",
    "Generate a code snippet in Python.",
    "Draft an email to a client.",
    "Provide a motivational quote."
]

# --- Conversation history ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant, like Microsoft Copilot. Always provide clear, concise, and actionable responses."}
    ]

# Display past messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Bot:** {msg['content']}")

# --- Preset buttons ---
st.write("### Quick Actions:")
cols = st.columns(len(preset_options))
for i, option in enumerate(preset_options):
    if cols[i].button(option):
        user_input = option
        st.session_state.messages.append({"role": "user", "content": user_input})

        try:
            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_NAME,  # Correct for Azure
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=500
            )
            reply = response.choices[0].message["content"].strip()
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# --- User text input ---
user_input = st.text_input("Or type your question here:")

if st.button("Send") and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            deployment_id=DEPLOYMENT_NAME,  # Correct for Azure
            messages=st.session_state.messages,
            temperature=0.7,
            max_tokens=500
        )
        reply = response.choices[0].message["content"].strip()
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

# --- Reset Chat ---
if st.button("🔄 Reset Chat"):
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful AI assistant, like Microsoft Copilot. Always provide clear, concise, and actionable responses."}
    ]
    st.rerun()

