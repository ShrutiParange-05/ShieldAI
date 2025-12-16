import streamlit as st
import ollama
import json
from code_editor import code_editor

# --- 1. Page Configuration (Must be first) ---
st.set_page_config(
    page_title="ShieldAI - Enterprise Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Session State ---
if "scan_result" not in st.session_state:
    st.session_state.scan_result = None
if "code_input" not in st.session_state:
    st.session_state.code_input = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 3. Advanced Custom CSS ---
st.markdown("""
<style>
    /* 🌑 DARK THEME BACKGROUND */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #1a1a2e 0%, #050505 60%);
    }

    /* 🃏 GLASS CARDS */
    .css-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .css-card:hover {
        border-color: rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* 🔴 RED ACCENT (Vulnerable) */
    .border-red { border-left: 4px solid #ff4b4b; }
    
    /* 🟢 GREEN ACCENT (Secure) */
    .border-green { border-left: 4px solid #00cc96; }

    /* ⚡ TITLE GRADIENT */
    .gradient-text {
        font-weight: 800;
        font-size: 3rem;
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        background: -webkit-linear-gradient(to right, #00c6ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    .subtitle {
        color: #888;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 30px;
    }

    /* 🛡️ VULNERABILITY ITEM ROW */
    .vuln-row {
        background-color: #111;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
    }
    .vuln-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .vuln-title {
        font-weight: 700;
        color: #fff;
        font-size: 1.05rem;
    }
    .vuln-badge {
        font-size: 0.75rem;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-high { background-color: rgba(255, 75, 75, 0.2); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .badge-medium { background-color: rgba(255, 165, 0, 0.2); color: orange; border: 1px solid orange; }
    .badge-low { background-color: rgba(0, 204, 150, 0.2); color: #00cc96; border: 1px solid #00cc96; }

    .line-number {
        font-family: monospace;
        background-color: #222;
        color: #aaa;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85rem;
        margin-left: 10px;
    }

</style>
""", unsafe_allow_html=True)

# --- 4. Logic Functions ---
SYSTEM_PROMPT_SCAN = """
You are a Senior Security Engineer. Analyze the provided code for security flaws.
Output MUST be a valid JSON object with these keys:
1. "vulnerabilities": A list of objects. Each object must have:
   - "type": Short name (e.g., "SQL Injection").
   - "line_number": The approximate line number (integer).
   - "severity": "High", "Medium", or "Low".
   - "description": Brief explanation.
   - "fix_tip": Short tip on how to fix it.
2. "secure_code": The complete, fully fixed code as a single string.
"""

def analyze_code(code_snippet):
    try:
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT_SCAN},
                {'role': 'user', 'content': code_snippet},
            ],
            format='json',
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        return {"error": str(e)}

def chat_with_code(user_query, code_context):
    chat_system_prompt = f"""
    You are an expert Secure Coding Tutor. 
    The user is asking questions about this code:
    ```
    {code_context}
    ```
    Answer concisely.
    """
    try:
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': chat_system_prompt},
                {'role': 'user', 'content': user_query},
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# --- 5. Header Section ---
col_head1, col_head2 = st.columns([2, 1])
with col_head1:
    st.markdown('<div class="gradient-text">🛡️ ShieldAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Next-Gen Static Application Security Testing (SAST)</div>', unsafe_allow_html=True)

with col_head2:
    # Status Indicator
    st.markdown("""
        <div style="text-align: right; padding-top: 20px;">
            <div style="display: inline-flex; align-items: center; background: rgba(0, 204, 150, 0.1); border: 1px solid #00cc96; padding: 8px 16px; border-radius: 30px;">
                <span style="height: 8px; width: 8px; background-color: #00cc96; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #00cc96;"></span>
                <span style="color: #00cc96; font-weight: 600; font-size: 0.9rem;">Engine Online</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- 6. Main Workspace ---
col1, col2 = st.columns([1, 1], gap="medium")

# === LEFT COLUMN: INPUT ===
with col1:
    st.markdown('<div class="css-card border-red">', unsafe_allow_html=True)
    st.subheader("🔴 Source Code (Vulnerable)")
    
    custom_btns = [{
        "name": "Scan Code",
        "feather": "Play",
        "primary": True,
        "hasText": True,
        "alwaysOn": True,
        "commands": ["submit"],
        "style": {"bottom": "0.5rem", "right": "0.5rem"}
    }]

    response_dict = code_editor(
        st.session_state.code_input if st.session_state.code_input else "import os\n\n# Paste your python code here...",
        lang="python",
        height=500,
        theme="monokai",
        buttons=custom_btns,
        key="editor_component"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if response_dict['type'] == "submit" and len(response_dict['text']) > 5:
        st.session_state.code_input = response_dict['text']
        st.session_state.chat_history = [] 
        with st.spinner("🚀 Initializing Neural Scan..."):
            st.session_state.scan_result = analyze_code(response_dict['text'])

# === RIGHT COLUMN: OUTPUT ===
with col2:
    if st.session_state.scan_result:
        result = st.session_state.scan_result
        
        # 1. Secure Code Display
        st.markdown('<div class="css-card border-green">', unsafe_allow_html=True)
        st.subheader("🟢 Remediated Code")
        
        if "error" in result:
             st.error(f"Analysis Failed: {result['error']}")
        else:
            secure_code_content = result.get("secure_code", "")
            if isinstance(secure_code_content, (dict, list)):
                secure_code_content = json.dumps(secure_code_content, indent=4)

            st.code(secure_code_content, language="python", line_numbers=True)
            
            # Action Buttons (Download & Tutor)
            b_col1, b_col2 = st.columns([1, 1])
            with b_col1:
                st.download_button(
                    label="📥 Download Fix",
                    data=secure_code_content,
                    file_name="secure_code.py",
                    mime="text/x-python",
                    use_container_width=True
                )
            with b_col2:
                # POPOVER TUTOR
                with st.popover("💬 Ask AI Tutor", use_container_width=True):
                    st.markdown("### 🤖 Security Tutor")
                    chat_container = st.container(height=300)
                    for message in st.session_state.chat_history:
                        with chat_container.chat_message(message["role"]):
                            st.markdown(message["content"])

                    if prompt := st.chat_input("Ask a question..."):
                        st.session_state.chat_history.append({"role": "user", "content": prompt})
                        with chat_container.chat_message("user"):
                            st.markdown(prompt)

                        with chat_container.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                answer = chat_with_code(prompt, st.session_state.code_input)
                                st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})

        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Vulnerability Feed (Below Code)
        vulns = result.get("vulnerabilities", [])
        if vulns:
            st.markdown(f"### 🛡️ Detected Threats ({len(vulns)})")
            
            for v in vulns:
                # Determine Badge Color
                severity = v.get('severity', 'Low').lower()
                badge_class = "badge-low"
                if severity == "high": badge_class = "badge-high"
                elif severity == "medium": badge_class = "badge-medium"
                
                # Render Vulnerability Item
                st.markdown(f"""
                <div class="vuln-row">
                    <div class="vuln-header">
                        <span class="vuln-title">{v.get('type')}</span>
                        <div>
                            <span class="line-number">Line {v.get('line_number')}</span>
                            <span class="vuln-badge {badge_class}">{v.get('severity')}</span>
                        </div>
                    </div>
                    <p style="color: #ccc; font-size: 0.9rem; margin-bottom: 8px;">{v.get('description')}</p>
                    <div style="font-size: 0.85rem; color: #00cc96;">
                        <strong>💡 Fix:</strong> {v.get('fix_tip')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
