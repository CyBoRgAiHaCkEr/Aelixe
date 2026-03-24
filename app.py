import streamlit as st
import sqlite3
import time
from groq import Groq

# --- 1. DATABASE SYSTEM (PERMANENT STORAGE) ---
def init_db():
    conn = sqlite3.connect('aelixe_memory.db')
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
    conn = sqlite3.connect('aelixe_memory.db')
    c = conn.cursor()
    c.execute("INSERT INTO logs (timestamp, engine, sender, message) VALUES (?, ?, ?, ?)",
              (time.strftime('%Y-%m-%d %H:%M:%S'), engine, sender, message))
    conn.commit()
    conn.close()

def load_logs(limit=15000):
    conn = sqlite3.connect('aelixe_memory.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, sender, message FROM logs ORDER BY id DESC LIMIT ?", (limit,))
    data = c.fetchall()
    conn.close()
    return data[::-1]

# Initialize DB on startup
init_db()

# --- 2. CORE CONFIG ---
st.set_page_config(page_title="Aelixe | Archive Mode", layout="wide")
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "YOUR_KEY"))

MODELS = {
    "Llama 4 Scout": "meta-llama/llama-4-scout-17b-16e-instruct",
    "GPT OSS 120B": "openai/gpt-oss-120b"
}

# --- 3. ROBOTIC UI ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');
    html, body, [class*="st-"] { font-family: 'JetBrains Mono', monospace !important; background-color: #050505; color: #00ffcc; }
    .terminal-entry { border-left: 3px solid #00ffcc; padding: 10px; margin: 10px 0; background: #000; white-space: pre-wrap; word-wrap: break-word; }
    .meta { color: #555; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("ilo.jpg", use_container_width=True)
    active_engine = st.selectbox("CORE ENGINE", list(MODELS.keys()))
    st.write(f"OPERATOR: Shrishti")
    if st.button("🗑️ WIPE DATABASE"):
        conn = sqlite3.connect('aelixe_memory.db')
        conn.cursor().execute("DELETE FROM logs")
        conn.commit()
        conn.close()
        st.rerun()

# --- 5. MAIN LOGIC ---
st.title("🛡️ Aelixe // Deep Memory Terminal")

# Analysis Function
def run_analysis(prompt):
    save_log(active_engine, "Aelixe", prompt)
    try:
        resp = client.chat.completions.create(
            model=MODELS[active_engine],
            messages=[{"role": "system", "content": "You are Aelixe,A Casual,Witty Helpful Ai.You help Shrishti answer all her questions.Keep it Simple."},
                      {"role": "user", "content": prompt}]
        )
        save_log(active_engine, "Aelixe", resp.choices[0].message.content)
    except Exception as e:
        save_log(active_engine, "SYSTEM", f"UPLINK ERROR: {str(e)}")

# Displaying Logs (Scrollable)
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
    run_analysis(prompt)
    st.rerun()
