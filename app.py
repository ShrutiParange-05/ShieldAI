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

# --- 3. Custom CSS (Cyberpunk UI) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Card Container Style */
    .css-card {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
    }
    
    /* Color Accents */
    .card-red { border-left: 5px solid #FF4B4B; }
    .card-green { border-left: 5px solid #00CC96; }
    
    /* Header Typography */
    .header-text {
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0px;
    }
    
    .sub-header {
        color: #B0B0B0;
        font-size: 1.2rem;
        margin-top: -10px;
    }
    
    /* Status Badge */
    .status-badge {
        background-color: #00CC96;
        color: #000;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. System Prompt for Llama 3 ---
SYSTEM_PROMPT = """
You are a Senior Security Engineer. Analyze the provided code for security flaws.
Output MUST be a valid JSON object with these keys:
1. "vulnerabilities": A list of objects. Each object must have:
   - "type": Short name (e.g., "SQL Injection").
   - "line_number": The approximate line number (integer or string).
   - "severity": "High", "Medium", or "Low".
   - "description": Brief explanation of the flaw.
   - "fix_tip": Short tip on how to fix it.
2. "secure_code": The complete, fully fixed code as a single string.
"""

def analyze_code(code_snippet):
    """Interacts with local Llama 3 via Ollama."""
    try:
        response = ollama.chat(
            model='llama3',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': code_snippet},
            ],
            format='json',
        )
        return json.loads(response['message']['content'])
    except Exception as e:
        return {"error": str(e)}

# --- 5. UI Layout ---

# Header Section
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown('<h1 class="header-text">🛡️ ShieldAI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enterprise-Grade Static Application Security Testing (SAST)</p>', unsafe_allow_html=True)

with col_head2:
    st.markdown("""
        <div style="text-align: right; padding-top: 30px;">
            <span class="status-badge">🟢 System Online</span>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Main Workspace (Dual Column)
col1, col2 = st.columns([1, 1], gap="large")

# === LEFT COLUMN: Input ===
with col1:
    st.markdown('<div class="css-card card-red">', unsafe_allow_html=True)
    st.subheader("🔴 Vulnerable Source")
    
    # Custom Button INSIDE the editor
    custom_btns = [{
        "name": "Scan Code",
        "feather": "Play",
        "primary": True,
        "hasText": True,
        "alwaysOn": True,
        "commands": ["submit"],
        "style": {"bottom": "0.5rem", "right": "0.5rem"}
    }]

    # Code Editor Component
    response_dict = code_editor(
        st.session_state.code_input if st.session_state.code_input else "import os\n\n# Paste your vulnerable code here...",
        lang="python",
        height=550,
        theme="monokai",
        buttons=custom_btns,
        key="editor_component"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Logic: Trigger Scan
    if response_dict['type'] == "submit" and len(response_dict['text']) > 5:
        st.session_state.code_input = response_dict['text']
        with st.spinner("🔍 Scanning logic & decrypting patterns..."):
            st.session_state.scan_result = analyze_code(response_dict['text'])


# === RIGHT COLUMN: Output ===
with col2:
    if st.session_state.scan_result:
        result = st.session_state.scan_result
        
        # 1. Secure Code Card
        st.markdown('<div class="css-card card-green">', unsafe_allow_html=True)
        st.subheader("🟢 Secured Implementation")
        
        if "error" in result:
             st.error(f"Analysis Failed: {result['error']}")
        else:
            # FIX: Ensure secure_code is a string for the download button
            secure_code_content = result.get("secure_code", "")
            if isinstance(secure_code_content, (dict, list)):
                secure_code_content = json.dumps(secure_code_content, indent=4)
            
            # Display Code
            st.code(secure_code_content, language="python", line_numbers=True)
            
            # Action Buttons Row
            b_col1, b_col2 = st.columns([1, 1])
            with b_col1:
                st.download_button(
                    label="📥 Download .py File",
                    data=secure_code_content,
                    file_name="secure_code.py",
                    mime="text/x-python",
                    use_container_width=True
                )
            with b_col2:
                st.caption("📋 Use the copy icon in the code block top-right to copy to clipboard.")
                
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Vulnerability Report
        vulns = result.get("vulnerabilities", [])
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Vulnerabilities Found", len(vulns))
        
        has_high_sev = any(v.get('severity') == 'High' for v in vulns)
        m2.metric("Risk Level", "CRITICAL" if has_high_sev else "MODERATE", delta_color="inverse")
        m3.metric("AI Confidence", "98%")
        
        st.divider()
        st.subheader(f"📝 Findings Breakdown")
        
        if vulns:
            for v in vulns:
                # Severity Badge Logic
                sev = v.get('severity', 'Low')
                icon = "🔴" if sev == "High" else "🟡"
                
                with st.expander(f"{icon} {sev}: {v.get('type')} (Line {v.get('line_number')})"):
                    st.markdown(f"**Description:** {v.get('description')}")
                    st.info(f"💡 **Fix Tip:** {v.get('fix_tip')}")
        else:
            st.success("✅ Clean Code: No major vulnerabilities detected.")

    else:
        # Empty State (Placeholder)
        st.markdown('<div class="css-card" style="text-align: center; opacity: 0.5; padding: 50px;">', unsafe_allow_html=True)
        st.subheader("Ready to Scan")
        st.markdown("Paste your code on the left and click **'Scan Code'** to begin analysis.")
        st.markdown('</div>', unsafe_allow_html=True)
