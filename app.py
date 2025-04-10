import streamlit as st
import hashlib
import os
import base64
from cryptography.fernet import Fernet
from datetime import datetime

# Generate or reuse Fernet key
if not os.path.exists("fernet.key"):
    with open("fernet.key", "wb") as f:
        f.write(Fernet.generate_key())
with open("fernet.key", "rb") as f:
    KEY = f.read()
cipher = Fernet(KEY)

# Session State
if "users" not in st.session_state:
    st.session_state.users = {}
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- Password Hashing with PBKDF2 ---
def hash_passkey(passkey, salt=b'streamlit_salt'):
    return hashlib.pbkdf2_hmac('sha256', passkey.encode(), salt, 100000).hex()

# --- Encrypt / Decrypt ---
def encrypt_data(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text):
    return cipher.decrypt(encrypted_text.encode()).decode()

# --- Store / Retrieve ---
def store_user_data(username, text, passkey):
    hashed = hash_passkey(passkey)
    encrypted = encrypt_data(text)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if username not in st.session_state.users:
        st.session_state.users[username] = {"records": [], "failed_attempts": 0}

    st.session_state.users[username]["records"].append({
        "encrypted_text": encrypted,
        "passkey_hash": hashed,
        "timestamp": timestamp
    })
    return encrypted

def retrieve_user_data(username, encrypted_text, passkey):
    if username not in st.session_state.users:
        return None, "User not found"

    user = st.session_state.users[username]
    hashed = hash_passkey(passkey)

    for record in user["records"]:
        if record["encrypted_text"] == encrypted_text:
            if record["passkey_hash"] == hashed:
                user["failed_attempts"] = 0
                return decrypt_data(encrypted_text), None
            else:
                user["failed_attempts"] += 1
                return None, "Incorrect passkey"
    return None, "Encrypted data not found"

def login(username, password):
    if username == "admin" and password == "admin123":
        st.session_state.current_user = username
        return True
    return False

# --- Custom CSS ---
def apply_custom_style():
    st.markdown("""
    <style>
    /* 🎨 Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Sacramento&family=Roboto:wght@400&family=Poppins:wght@300;400&display=swap');

    html, body, [class*="css"] {
        background-color: #0a0a0a !important;
        color: #eeeeee !important;
        font-family: 'Roboto', sans-serif !important;
        padding: 0;  /* Ensure no unwanted padding in body */
        margin: 0;  /* Ensure no unwanted margin in body */
        overflow-x: hidden; /* Prevent horizontal scrolling */
    }

    /* Title & Headers */
    h1, h2, h3, h4, h5 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #fff;
    }

    /* Gradient Text Style */
    .gradient-text {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.5em; /* Adjusted size */
        font-weight: 600;
        background: linear-gradient(90deg, #ff6ec4, #7873f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glowText 3s ease-in-out infinite alternate; /* Slower animation */
        margin: 20px auto;  /* Center the text with auto margin */
        padding: 5px 15px;  /* Padding around text */
        display: block; /* Ensure it behaves like block element */
        text-align: center; /* Center the text inside the block */
        white-space: nowrap; /* Keep text on one line */
        max-width: 90vw;  /* Limit the width of text to 90% of the viewport */
        word-wrap: break-word; /* Prevent overflow */
        overflow: hidden; /* Hide any content that overflows */
    }

    /* Text Glow Animation (Reduced Glow) */
    @keyframes glowText {
        0% { text-shadow: 0 0 3px #ff6ec4, 0 0 5px #ff6ec4, 0 0 7px #ff6ec4; }
        100% { text-shadow: 0 0 5px #7873f5, 0 0 10px #7873f5, 0 0 15px #7873f5; }
    }

    /* Button Style */
    .stButton button {
        background: linear-gradient(90deg, #ff6ec4, #7873f5);
        border: none;
        color: white;
        font-weight: 700;
        padding: 1em 2em;
        border-radius: 25px;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.1);
    }

    /* Input Fields */
    .stTextInput > div > div > input, .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #444 !important;
        border-radius: 10px;
    }

    .stTextInput input {
        padding: 0.75rem;
        font-size: 1.1rem;
    }

    .stTextArea textarea {
        padding: 0.75rem;
        font-size: 1.1rem;
    }

    /* Paragraphs and Captions */
    .stMarkdown, .stCaption, .css-1v0mbdj p {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 300;
        line-height: 1.6;
        color: #f1f1f1;
    }

    /* Fancy Footer */
    footer {
        text-align: center;
        font-family: 'Sacramento', cursive;
        font-size: 1.4em;
        color: #f1f1f1;
        margin-top: 2em;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"] {
        background-color: #000000 !important;
        color: #e0e0e0 !important;
        font-family: 'Poppins', sans-serif;
    }

    .gradient-text {
        font-weight: 600;
        background: linear-gradient(90deg, #ff6ec4, #7873f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stTextInput > div > div > input,
    .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #444 !important;
    }

    .stButton button {
        background: linear-gradient(90deg, #ff6ec4, #7873f5);
        border: none;
        color: white;
        font-weight: 600;
        padding: 0.5em 1em;
        border-radius: 10px;
    }

    .stButton button:hover {
        transform: scale(1.03);
        background: linear-gradient(90deg, #7873f5, #ff6ec4);
    }

    </style>
    """, unsafe_allow_html=True)


# --- Apply Style ---
apply_custom_style()

# --- Title ---
st.markdown('<h1 class="gradient-text">🛡️ Secure Data Encryption System</h1>', unsafe_allow_html=True)
st.caption("✨ Stylish • Secure • Streamlit-Based")

# --- Menu ---
menu = ["🏠 Home", "📥 Store Data", "🔓 Retrieve Data", "🔐 Login"]
choice = st.sidebar.selectbox("📁 Menu", menu)

# --- Home ---
if choice == "🏠 Home":
    st.markdown("## Welcome, **Laiqa** 👋")
    st.write("Use the sidebar to **store** or **retrieve** your encrypted data.")
    if st.session_state.current_user:
        st.success(f"✅ Logged in as `{st.session_state.current_user}`")

# --- Store Data ---
elif choice == "📥 Store Data":
    st.markdown("## 📝 Store Your Secret Data")
    username = st.text_input("Username")
    text = st.text_area("Enter Data to Encrypt")
    passkey = st.text_input("Passkey", type="password")

    if st.button("Encrypt & Save"):
        if username and text and passkey:
            encrypted = store_user_data(username, text, passkey)
            st.success("✅ Data stored successfully!")
            st.code(encrypted, language='text')
        else:
            st.error("⚠️ Please fill all fields.")

# --- Retrieve Data ---
elif choice == "🔓 Retrieve Data":
    st.markdown("## 🔍 Retrieve Your Data")
    username = st.text_input("Username")
    encrypted_text = st.text_area("Paste Encrypted Text")
    passkey = st.text_input("Passkey", type="password")

    if st.button("Decrypt"):
        if username and encrypted_text and passkey:
            if username in st.session_state.users and st.session_state.users[username]["failed_attempts"] >= 3:
                st.warning("🔒 Too many failed attempts! Login required.")
                st.stop()

            decrypted, error = retrieve_user_data(username, encrypted_text, passkey)

            if decrypted:
                st.success("✅ Decrypted Data:")
                st.code(decrypted)
            else:
                remaining = 3 - st.session_state.users.get(username, {}).get("failed_attempts", 0)
                st.error(f"❌ {error} | Attempts left: {remaining}")
        else:
            st.error("⚠️ Please fill all fields.")

# --- Login ---
elif choice == "🔐 Login":
    st.markdown("## 🔐 Admin Login (to reset lockout)")
    username = st.text_input("Admin Username", value="admin")
    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        if login(username, password):
            for u in st.session_state.users:
                st.session_state.users[u]["failed_attempts"] = 0
            st.success("✅ Reauthorized. Attempts reset.")
            st.balloons()
        else:
            st.error("❌ Invalid credentials!")

# --- Footer ---
st.markdown("---")
st.caption("Created with 💖 by Laiqa | Streamlit 2025 | Stylish Secure App")
