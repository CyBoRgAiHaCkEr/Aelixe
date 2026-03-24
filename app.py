import streamlit as st
import sqlite3
import time
from groq import Groq

# --- 1. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('aelixe_memory.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 timestamp TEXT, 
                 engine TEXT, 
                 sender TEXT, 
                 message TEXT)''')
    conn.commit()
    conn.close()

def save_log(engine, sender, message):
    conn = sqlite3.connect('aelixe_memory.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, engine, sender, message) VALUES (?, ?, ?, ?)",
              (time.strftime('%Y-%m-%d %H:%M:%S'), engine, sender, message))
    conn.commit()
    conn.close()

def load_logs(limit=100): # Reduced limit for performance
    conn = sqlite3.connect('aelixe_memory.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT timestamp, sender, message FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    data = c.fetchall()
    conn.close()
    return data[::-1]

init_db()

# --- 2. CORE CONFIG ---
st.set_page_config(page_title="Aelixe | Archive Mode", layout="wide")

# Securely get API Key
api_key = st.secrets.get("GROQ_API_KEY")
if not api_key:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

client = Groq(api_key=api_key)

# Note: Ensure these model strings are correct per Groq's current documentation
MODELS = {
    "Llama 4 Scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    "Groq Compound": "groq/compound"
}

# --- 3. ROBOTIC UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
    html, body, [class*="st-"] { font-family: 'JetBrains Mono', monospace !important; background-color: #050505; color: #00ffcc; }
    .terminal-entry { border-left: 3px solid #00ffcc; padding: 10px; margin: 10px 0; background: #111; white-space: pre-wrap; }
    .meta { color: #008b8b; font-size: 0.8rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    # st.image("ilo.jpg") # Ensure this file is in your GitHub repo!
    active_engine = st.selectbox("CORE ENGINE", list(MODELS.keys()))
    st.write("OPERATOR: Shrishti")
    if st.button("🗑️ WIPE DATABASE"):
        conn = sqlite3.connect('aelixe_memory.db')
        conn.cursor().execute("DELETE FROM logs")
        conn.commit()
        conn.close()
        st.rerun()

# --- 5. MAIN LOGIC ---
st.title("🛡️ Aelixe // Deep Memory Terminal")

# Displaying Logs
logs = load_logs()
for ts, sender, msg in logs:
    st.markdown(f"""
    <div class="terminal-entry">
        <div class="meta">[{ts}] {sender} >></div>
        {msg}
    </div>
    """, unsafe_allow_html=True)

# Input
if prompt := st.chat_input("Say Whatever You want 🫠"):
    # 1. Save User Message
    save_log(active_engine, "Shrishti", prompt)
    
    # 2. Get AI Response
    try:
        resp = client.chat.completions.create(
            model=MODELS[active_engine],
            messages=[
                {"role": "system", "content": "You are Aelixe, a casual, witty, and helpful AI. You help Shrishti answer all her questions. Keep it simple."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_msg = resp.choices[0].message.content
        save_log(active_engine, "Aelixe", ai_msg)
    except Exception as e:
        save_log(active_engine, "SYSTEM", f"UPLINK ERROR: {str(e)}")
    
    st.rerun()
