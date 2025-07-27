import streamlit as st
import ollama
from prompts import generate_prompt
import io
import re
import time

st.set_page_config(page_title="Email Tone Improver", layout="centered")
st.write("#### ✨ Because how you say it matters.")
st.title("Email Tone Improver")

st.markdown("""
<style>
.tone-container {
    display: flex;
    flex-wrap: wrap;
    gap: 12px 20px;
    padding: 10px 0;
    margin-bottom: 16px;
}
.tone-option {
    display: flex;
    align-items: center;
    gap: 6px;
}

.message-container {
    background-color: #2b2933;
    padding: 16px;
    border-radius: 12px;
    margin: 16px 0;
    position: relative;
    border: 1px solid #3c4043;
}

.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #3c4043;
}

.message-label {
    font-weight: 600;
    font-size: 16px;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 8px;
}

.copy-btn {
    background: #3a3f4b;
    border: 1px solid #5c6370;
    border-radius: 6px;
    padding: 6px 12px;
    color: white;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s ease;
}

.copy-btn:hover {
    background: #4a5568;
    border-color: #718096;
}

.message-content {
    color: white;
    font-size: 15px;
    line-height: 1.5;
    white-space: pre-wrap;
    margin: 0;
}

.tone-tag-container {
    background-color: #0e1117;
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid #30363d;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
    margin-bottom: 16px;
}

.tone-tag {
    background-color: #21262d;
    color: white;
    padding: 6px 10px;
    border-radius: 12px;
    font-size: 13px;
    border: 1px solid #3c4043;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    margin: 20px 0;
}

.loading-text {
    color: white;
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    text-align: center;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.success-message {
    background-color: #1e4d4d;
    color: #4fd1c7;
    padding: 12px 16px;
    border-radius: 8px;
    margin: 16px 0;
    border-left: 4px solid #4fd1c7;
}

.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #3c4043, transparent);
    margin: 24px 0;
}
</style>

<script>
function copyToClipboard(text, buttonId) {
    navigator.clipboard.writeText(text).then(function() {
        const button = document.getElementById(buttonId);
        const originalText = button.innerHTML;
        button.innerHTML = "✓ Copied!";
        button.style.background = "#22c55e";
        setTimeout(function() {
            button.innerHTML = originalText;
            button.style.background = "#3a3f4b";
        }, 2000);
    });
}
</script>
""", unsafe_allow_html=True)

user_input = st.text_area("Enter your email or message:", height=100, placeholder="Type your email here...")

all_tones = [
    "Professional", "Friendly", "Apologetic", "Assertive", "Casual",
    "Empathetic", "Encouraging", "Formal", "Witty", "Motivational",
    "Sympathetic", "Grateful", "Persuasive", "Respectful", "Neutral"
]

if "selected_tones" not in st.session_state:
    st.session_state.selected_tones = ["Professional", "Friendly"]

cols = st.columns(4)
new_selected = []

for i, tone in enumerate(all_tones):
    col = cols[i % 4]
    with col:
        checked = st.checkbox(tone, value=(tone in st.session_state.selected_tones), key=tone)
        if checked:
            new_selected.append(tone)

st.session_state.selected_tones = new_selected

if new_selected:
    tone_tags = "".join([f'<div class="tone-tag">{tone}</div>' for tone in new_selected])
    st.markdown(f'<div class="tone-tag-container">{tone_tags}</div>', unsafe_allow_html=True)

strength = st.slider("Tone Strength", min_value=1, max_value=5, value=3, 
                    help="1 = Subtle, 3 = Moderate, 5 = Strong")

st.markdown("**💡 Tip:** Select multiple tones to see different versions of your email and choose the one that fits your needs best!")

def clean_ai_response(response_text):
    patterns_to_remove = [
        r"Sure,?\s*here(?:'s| is) the rewritten email in a \w+ tone:?\s*",
        r"Here(?:'s| is) the rewritten (?:email|message) in a \w+ tone:?\s*",
        r"I'll rewrite (?:this|the) (?:email|message) in a \w+ tone:?\s*",
        r"Here(?:'s| is) the (?:email|message) rewritten in a \w+ tone:?\s*",
        r"The rewritten (?:email|message) in a \w+ tone is:?\s*",
        r"^.*?tone:?\s*[\"']?",
        r"[\"']?\s*$", 
    ]
    
    cleaned_text = response_text.strip()
    
    for pattern in patterns_to_remove:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
    
    cleaned_text = cleaned_text.strip('"\'')
    
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text.strip())
    
    return cleaned_text

def display_message_box(label, content, is_original=False):
    icon = "🔒" if is_original else "✨"
    button_id = f"copy_btn_{hash(content) % 10000}"
    
    message_html = f"""
    <div class="message-container">
        <div class="message-header">
            <div class="message-label">
                {icon} {label}
            </div>
            <div class="copy-btn" id="{button_id}" onclick="copyToClipboard(`{content.replace('`', '\\`').replace('\\', '\\\\').replace('"', '\\"')}`, '{button_id}')">
                📋 Copy
            </div>
        </div>
        <div class="message-content">{content}</div>
    </div>
    """
    
    st.markdown(message_html, unsafe_allow_html=True)
    return content

if st.button("🔁 Rewrite Email in Selected Tones", type="primary"):
    if user_input.strip() and new_selected:
        loading_messages = [
            "🎯 Analyzing your message tone...",
            "✨ Crafting perfect improvements...",
            "🔄 Enhancing your email style...",
            "💫 Polishing your communication...",
            "🎨 Fine-tuning the language..."
        ]
        
        loading_placeholder = st.empty()
        loading_placeholder.markdown(f"""
        <div class="loading-container">
            <div class="loading-text">{loading_messages[0]}</div>
            <div class="spinner"></div>
        </div>
        """, unsafe_allow_html=True)
        
        output_blocks = []
        
        for i, selected_tone in enumerate(new_selected):
            if i < len(loading_messages):
                loading_placeholder.markdown(f"""
                <div class="loading-container">
                    <div class="loading-text">{loading_messages[i]}</div>
                    <div class="spinner"></div>
                </div>
                """, unsafe_allow_html=True)
            
            try:
                prompt = generate_prompt(selected_tone, user_input)
                response = ollama.chat(
                    model='gemma:2b',
                    messages=[{"role": "user", "content": prompt}]
                )
                
                raw_response = response['message']['content']
                cleaned_response = clean_ai_response(raw_response)
                
                output_blocks.append((selected_tone, cleaned_response))
                
            except Exception as e:
                output_blocks.append((selected_tone, f"Error generating {selected_tone} tone: {str(e)}"))
        
        loading_placeholder.empty()
        
        st.markdown("""
        <div class="success-message">
            🎉 Successfully enhanced your email in all selected tones!
        </div>
        """, unsafe_allow_html=True)
        
        display_message_box("Original Message", user_input, is_original=True)
        
        combined_text = f"Original Message:\n{user_input}\n\n"
        combined_text += "="*50 + "\n\n"
        
        for tone_title, improved_content in output_blocks:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            label = f"{tone_title} Tone - Improved Version"
            display_message_box(label, improved_content)
            
            filename = f"{tone_title.lower()}_improved_email.txt"
            st.download_button(
                label=f"📥 Download {tone_title} Version",
                data=improved_content,
                file_name=filename,
                mime="text/plain",
                key=f"download_{tone_title}",
                help=f"Download the {tone_title.lower()} version of your email"
            )
            
            combined_text += f"{tone_title} Tone:\n{improved_content}\n\n"
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📂 Download All Versions",
                data=combined_text.encode('utf-8'),
                file_name="all_improved_email_versions.txt",
                mime="text/plain",
                help="Download all improved versions in a single file",
                type="primary"
            )
            
    elif not user_input.strip():
        st.warning("⚠️ Please enter your email message first.")
    else:
        st.warning("⚠️ Please select at least one tone to improve your email.")

st.markdown("---")
