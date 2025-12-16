import streamlit as st
import ollama
import json
from code_editor import code_editor

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="ShieldAI - Secure Code Reviewer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. Session State Management ---
if "scan_result" not in st.session_state:
    st.session_state.scan_result = None
if "code_input" not in st.session_state:
    st.session_state.code_input = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 3. Custom CSS (Cyberpunk UI) ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .css-card {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    .card-red { border-left: 5px solid #FF4B4B; }
    .card-green { border-left: 5px solid #00CC96; }
    .card-blue { border-left: 5px solid #29B5E8; } /* New Chat Card Style */
    
    .header-text {
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
    }
    .sub-header { color: #B0B0B0; font-size: 1.2rem; margin-top: -10px; }
    .status-badge {
        background-color: #00CC96;
        color: #000;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. Logic Functions ---

SYSTEM_PROMPT_SCAN = """
You are a Senior Security Engineer. Analyze the provided code for security flaws.
Output MUST be a valid JSON object with these keys:
1. "vulnerabilities": A list of objects. Each object must have:
   - "type": Short name (e.g., "SQL Injection").
   - "line_number": The approximate line number.
   - "severity": "High", "Medium", or "Low".
   - "description": Brief explanation.
   - "fix_tip": Short tip on how to fix it.
2. "secure_code": The complete, fully fixed code as a single string.
"""

def analyze_code(code_snippet):
    """Scans code and returns JSON report."""
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
    """Chat function that knows about the code."""
    # We inject the code context into the system prompt for the chat
    chat_system_prompt = f"""
    You are an expert Secure Coding Tutor. 
    The user is asking questions about the following piece of code:
    
    ```
    {code_context}
    ```
    
    Answer their questions clearly and concisely. Explain security concepts if asked.
    """
    
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': chat_system_prompt},
                {'role': 'user', 'content': user_query},
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# --- 5. UI Layout ---

# Header
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<h1 class="header-text">🛡️ ShieldAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Secure Code Reviewer</p>', unsafe_allow_html=True)
with col_head2:
    st.markdown('<div style="text-align: right; padding-top: 30px;"><span class="status-badge">🟢 System Online</span></div>', unsafe_allow_html=True)
st.divider()

# Main Workspace
col1, col2 = st.columns([1, 1], gap="large")

# === LEFT: Input ===
with col1:
    st.markdown('<div class="css-card card-red">', unsafe_allow_html=True)
    st.subheader("🔴 Vulnerable Source")
    
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
        st.session_state.code_input if st.session_state.code_input else "import os\n\n# Paste code here...",
        lang="python",
        height=500,
        theme="monokai",
        buttons=custom_btns,
        key="editor_component"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if response_dict['type'] == "submit" and len(response_dict['text']) > 5:
        st.session_state.code_input = response_dict['text']
        # Clear old chat when new code is scanned
        st.session_state.chat_history = [] 
        with st.spinner("🔍 Scanning logic & decrypting patterns..."):
            st.session_state.scan_result = analyze_code(response_dict['text'])

# === RIGHT: Output & Chat ===
with col2:
    if st.session_state.scan_result:
        result = st.session_state.scan_result
        
        # --- 1. Secure Code Card ---
        st.markdown('<div class="css-card card-green">', unsafe_allow_html=True)
        st.subheader("🟢 Secured Implementation")
        
        if "error" in result:
             st.error(f"Analysis Failed: {result['error']}")
        else:
            secure_code_content = result.get("secure_code", "")
            if isinstance(secure_code_content, (dict, list)):
                secure_code_content = json.dumps(secure_code_content, indent=4)
            
            st.code(secure_code_content, language="python", line_numbers=True)
            
            # Download & Copy
            b_col1, b_col2 = st.columns([1, 1])
            with b_col1:
                st.download_button(
                    label="📥 Download .py",
                    data=secure_code_content,
                    file_name="secure_code.py",
                    mime="text/x-python",
                    use_container_width=True
                )
            with b_col2:
                st.caption("Tip: Use the copy icon ↗️ on the code block.")
                
        st.markdown('</div>', unsafe_allow_html=True)

        # --- 2. Chat with Code (New Feature) ---
        st.markdown('<div class="css-card card-blue">', unsafe_allow_html=True)
        st.subheader("🤖 Security Tutor")
        st.caption("Ask questions about the vulnerabilities or the fix.")

        # Display Chat History
        chat_container = st.container(height=300)
        for message in st.session_state.chat_history:
            with chat_container.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ask a question (e.g., 'Why is os.system dangerous?')"):
            # 1. Add User Message
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with chat_container.chat_message("user"):
                st.markdown(prompt)

            # 2. Get AI Response
            with chat_container.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Pass the *original* vulnerable code as context so it knows what you are talking about
                    answer = chat_with_code(prompt, st.session_state.code_input)
                    st.markdown(answer)
            
            # 3. Add AI Message to History
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Empty State
        st.markdown('<div class="css-card" style="text-align: center; opacity: 0.5; padding: 50px;">', unsafe_allow_html=True)
        st.subheader("Ready to Scan")
        st.markdown("Paste code on the left and click **'Scan Code'** to begin.")
        st.markdown('</div>', unsafe_allow_html=True)
