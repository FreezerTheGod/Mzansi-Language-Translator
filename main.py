import streamlit as st
from huggingface_hub import InferenceClient

# Setting the page title, icon, and layout for the Streamlit app
st.set_page_config(page_title="Mzansi Translator 🇿🇦", page_icon="🇿🇦", layout="centered")

# Custom CSS styling for the app, including fonts, colors, and layout
st.markdown(
    """
    <style>
    /* Pull in a bold poster-style font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Anton&family=Montserrat:wght@400;600&display=swap');

    /* Striped "flag" bar across the very top of the page, like the
       diagonal pattern in your reference image */
    .top-stripe {
        height: 14px;
        width: 100%;
        background: repeating-linear-gradient(
            45deg,
            #FFB612 0px, #FFB612 20px,
            #007A4D 20px, #007A4D 40px,
            #002395 40px, #002395 60px,
            #DE3831 60px, #DE3831 80px,
            #F2E9D8 80px, #F2E9D8 100px
        );
        margin-bottom: 1.5rem;
        border-radius: 4px;
    }

    /* Overall app background: dark charcoal/brown, like the mountain photo overlay */
    .stApp {
        background-color: #211c19;
        color: #f2e9d8;
    }

    /* Streamlit's default header bar (the strip that holds the "Deploy"
       button and the ⋮ menu) is white by default. Instead of hiding it,
       we recolor it to match the page background so it blends in, and
       recolor its icons/text to match the poster-subtitle color. */
    header[data-testid="stHeader"] {
        background-color: #211c19;
    }
    header[data-testid="stHeader"] svg,
    header[data-testid="stHeader"] span,
    header[data-testid="stHeader"] button {
        color: #cbb98f !important;
        fill: #cbb98f !important;
    }

    .block-container {
        padding-top: 4.5rem;
    }

    /* Big poster-style title */
    .poster-title {
        font-family: 'Anton', sans-serif;
        font-size: 3rem;
        text-transform: uppercase;
        text-align: center;
        color: #f2e9d8;
        letter-spacing: 2px;
        line-height: 1.1;
        margin-bottom: 0;
    }
    .poster-title span {
        color: #e0a940; /* gold accent word */
    }

    .poster-subtitle {
        font-family: 'Montserrat', sans-serif;
        text-align: center;
        color: #cbb98f;
        margin-top: 0.5rem;
        margin-bottom: 2rem;
        font-size: 0.95rem;
        letter-spacing: 1px;
    }

    /* Body text / labels */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }

    /* Dropdowns and text area: warm coffee-brown boxes with gold border,
       nicely rounded corners */
    .stSelectbox div[data-baseweb="select"],
    [data-testid="stTextArea"] textarea {
        background-color: #3a2a20 !important;
        color: #f2e9d8 !important;
        border: 1px solid #e0a940 !important;
        border-radius: 14px !important;
    }

    /* The textarea's typed/placeholder text specifically — targeted
       directly so Streamlit's default blue text color can't win */
    [data-testid="stTextArea"] textarea,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #f2e9d8 !important;
        -webkit-text-fill-color: #f2e9d8 !important;
    }
    [data-testid="stTextArea"] textarea::placeholder {
        color: #a89a83 !important;
        -webkit-text-fill-color: #a89a83 !important;
    }

    /* Labels above inputs */
    label {
        color: #e0a940 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 1px;
    }

    /* The Translate button: bold gold, poster-style */
    .stButton button {
        font-family: 'Anton', sans-serif;
        background-color: #e0a940;
        color: #211c19;
        border: none;
        border-radius: 14px;
        padding: 0.6rem 1.5rem;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        width: 100%;
        transition: 0.2s ease;
    }
    .stButton button:hover {
        background-color: #f2c667;
        color: #211c19;
    }

    /* The translated result box */
    .stAlert {
        background-color: #3a2a20 !important;
        border: 1px solid #e0a940 !important;
        border-radius: 14px !important;
    }
    .stAlert p,
    .stAlert div,
    [data-testid="stAlertContentInfo"] p,
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
        color: #cbb98f !important;
    }

    /* Footer credit line at the very bottom of the page */
    .footer-credit {
        text-align: center;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.8rem;
        color: #a89a83;
        margin-top: 1rem;
        letter-spacing: 0.5px;
    }
    .footer-credit a {
        color: #e0a940;
        text-decoration: none;
    }
    .footer-credit a:hover {
        text-decoration: underline;
    }
    </style>

    <div class="top-stripe"></div>
    """,
    unsafe_allow_html=True,
)


# Set of supported South African languages for translation
LANGUAGES = [
    "English",
    "isiZulu",
    "isiXhosa",
    "Afrikaans",
    "Sepedi (Northern Sotho)",
    "Sesotho (Southern Sotho)",
    "Setswana",
    "Xitsonga",
    "Siswati"
]

# The Hugging Face API token
HF_TOKEN = st.secrets["HF_TOKEN"]

# Initialize the Hugging Face InferenceClient with the provided API token
client = InferenceClient(api_key=HF_TOKEN)

# Method to translate text from a source language to a target language using the Hugging Face model
def translate_text(text, src_lang, tgt_lang):
    # Prepare the messages for the chat completion request, instructing the model to translate the text
    messages = [
        {
            "role": "system",
            "content": (
                f"You are a helpful South African language translator. "
                f"Translate the text from {src_lang} to {tgt_lang}. "
                f"Output ONLY the final translated text. Do not include any greeting, "
                f"explanation, introductory text, notes, or quotation marks. "
                f"Just output the pure translation."
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]
    # Make the chat completion request to the Hugging Face model and return the translated text 
    try:
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=messages,
            max_tokens=300,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# Custom title using our poster-title CSS class instead of st.title()
st.markdown(
    '<div class="poster-title">Mzansi <span>Translator</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="poster-subtitle">FREE LOCAL LANGUAGE TRANSLATION &nbsp;·&nbsp; POWERED BY HUGGING FACE 🇿🇦</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
with col1:
    src_lang = st.selectbox("Translate from:", LANGUAGES, index=0)
with col2:
    tgt_lang = st.selectbox("Translate to:", LANGUAGES, index=1)

text_to_translate = st.text_area(
    "Enter text to translate:",
    height=150,
    placeholder="How are you today, my friend?"
)

if st.button("Translate", type="primary"):
    if text_to_translate.strip() == "":
        st.warning("Please enter some text to translate.")
    else:
        with st.spinner(f"Translating to {tgt_lang}..."):
            translated_text = translate_text(text_to_translate, src_lang, tgt_lang)

            st.subheader("Translation:")
            st.info(translated_text)

# Bottom stripe to bookend the page, matching the top
st.markdown('<div class="top-stripe"></div>', unsafe_allow_html=True)

# Footer credit
st.markdown(
    '<div class="footer-credit">Design inspiration from '
    '<a href="https://dribbble.com/AndrejDesignSats" target="_blank">'
    'Andrej designSats | Dribbble</a></div>',
    unsafe_allow_html=True,
)