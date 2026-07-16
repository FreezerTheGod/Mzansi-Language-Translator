# Mzansi Translator 🇿🇦
I built this Streamlit app to make translating between South Africa's local languages quick and free. It's a simple web app that lets you pick a source and target language from all 9 of our official languages and translates your text in a couple of seconds. The app is coded in Python using Streamlit for the interface, connected to Hugging Face's Inference API for the actual translation.

<img width="1272" height="885" alt="Screenshot_2026-07-16_18-51-25" src="https://github.com/user-attachments/assets/310646a3-e945-44ae-b6bc-03f656572c68" />


## 🔥 What It Does
- **Language Selection:** Pick any "from" and "to" language out of English, isiZulu, isiXhosa, Afrikaans, Sepedi, Sesotho, Setswana, Xitsonga, and Siswati using two dropdowns.
- **Text Input:** Type or paste the text you want translated into a text area.
- **Translate Button:** Sends your text to the model and displays the clean, translated result, no extra notes or explanations, just the translation.
- **Custom Styling:** A warm, poster-inspired theme with a South African flag stripe, custom fonts (Anton + Montserrat), and a dark charcoal/gold color palette built entirely with custom CSS injected into Streamlit.

---

## 🧠 What I Learned Doing This
Instead of just wiring up an API call and calling it done, I wanted to actually understand how each piece worked. Here is what I learned:

### 🔑 Choosing `InferenceClient` over the router endpoint
For an earlier project I called Hugging Face's hosted models through the raw router URL with `requests`, building the payload and headers manually:

```python
HF_TOKEN = st.secrets["HF_TOKEN"]
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

payload = {
    "inputs": text_input,
    "parameters": {"max_length": max_len, "min_length": min_len},
}
response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
response.raise_for_status()
result = response.json()
summary = result[0]["summary_text"]
```

For this project, I ran into trouble getting that same route to reliably fetch the model I wanted, requests to it kept breaching or failing outright. So instead I switched to `huggingface_hub`'s `InferenceClient`, which handles the routing, headers, and endpoint resolution internally instead of me having to hardcode a URL:

```python
client = InferenceClient(api_key=HF_TOKEN)

def translate_text(text, src_lang, tgt_lang):
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
```

Using `client.chat.completions.create()` meant I could talk to `Qwen2.5-7B-Instruct` the same way I'd talk to any chat model, passing a `messages` list instead of a raw `inputs` string, which turned out to be a much more stable connection for what I was building.

- **Prompt engineering for translation:** How to write a system prompt that forces the model (`Qwen2.5-7B-Instruct`) to output *only* the translated text, with no greetings, explanations, or quotation marks wrapped around it.
- **Streamlit secrets management:** How to keep my API key out of the codebase using `st.secrets["HF_TOKEN"]` instead of hardcoding it.
- **Styling Streamlit with raw CSS:** Streamlit doesn't give you much control out of the box, so I learned how to target its internal `data-testid` elements (text areas, buttons, alerts, the header bar) with `st.markdown(unsafe_allow_html=True)` to fully restyle the app.

---

## 🛠️ The Tech Stack
- **Python** (Core logic)
- **Streamlit** (Web app framework / UI)
- **Hugging Face Hub** (`InferenceClient` for calling the translation model)
- **Qwen2.5-7B-Instruct** (The LLM doing the actual translating)

---

## 🎨 Design Credit
The visual design was inspired by [Andrej designSats on Dribbble](https://dribbble.com/AndrejDesignSats).

---

## 💻 How to Run It Yourself

### 1. Clone the repository
```bash
git clone https://github.com/FreezerTheGod/mzansi-translator.git
cd mzansi-translator
```

### 2. Install dependencies
```bash
pip install streamlit huggingface_hub
```

### 3. Get a Hugging Face API token
1. Go to [Hugging Face](https://huggingface.co/settings/tokens) and log in (or create a free account).
2. Generate a new **Access Token** with at least read/inference permissions.

### 4. Add your token as a secret
Create a folder called `.streamlit` in your project root, then inside it create a file called `secrets.toml`:
```toml
HF_TOKEN = "your_token_here"
```

### 5. Run the app
```bash
streamlit run app.py
```
If it worked, your browser will open automatically to `localhost:8501` and you'll see the Mzansi Translator interface. 🎉
