import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import re
import requests
import json

# ── Paths ──────────────────────────────────────────────────────────────────────
# pages/12_chatbot.py → pages → dashboard → AI_Real_Estate_system
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEANED_DATA    = os.path.join(BASE_DIR, "data", "processed", "cleaned_df.csv")
MODEL_PATH      = os.path.join(BASE_DIR, "models", "best_model.pkl")

# ── Load Dataset (cleaned training data as default fallback) ──────────────────
@st.cache_data(show_spinner=False)
def load_dataset(path):
    return pd.read_csv(path)

@st.cache_resource(show_spinner=False)
def load_model():
    return joblib.load(MODEL_PATH)

# Priority: analyzer upload → cleaned training data → nothing
def get_active_dataframe():
    """Returns (df, source_label) — uses uploaded analyzer CSV or falls back to training data."""
    # Check if analyzer page stored an uploaded df in session
    if "analyzer_df" in st.session_state and st.session_state["analyzer_df"] is not None:
        return st.session_state["analyzer_df"], "uploaded CSV"
    # Fall back to training dataset
    if os.path.exists(CLEANED_DATA):
        return load_dataset(CLEANED_DATA), "training dataset"
    return None, None

df, DATA_SOURCE = get_active_dataframe()
DATA_LOADED = df is not None

try:
    model = load_model()
except Exception:
    model = None

# ── City Stats ─────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def compute_city_stats(dataframe):
    stats = {}
    # Try known price column names first
    price_col = next((c for c in ["Price_in_Lakhs", "price_in_lakhs", "Price", "price",
                                   "price_lakhs", "Price_Lakhs"]
                      if c in dataframe.columns), None)
    # Fallback: any numeric column
    if price_col is None:
        num_cols = dataframe.select_dtypes(include=["float64", "float32", "int64"]).columns.tolist()
        if not num_cols:
            return {}
        price_col = num_cols[0]
    city_col = next((c for c in ["City", "city"] if c in dataframe.columns), None)
    if city_col is None:
        return {}
    for city, grp in dataframe.groupby(city_col):
        stats[str(city).lower()] = {
            "city":         str(city),
            "avg_price":    round(grp[price_col].mean(), 2),
            "median_price": round(grp[price_col].median(), 2),
            "min_price":    round(grp[price_col].min(), 2),
            "max_price":    round(grp[price_col].max(), 2),
            "count":        len(grp),
        }
    return stats

def get_price_col(dataframe):
    col = next((c for c in ["Price_in_Lakhs", "price_in_lakhs", "Price", "price",
                              "price_lakhs", "Price_Lakhs"]
                if c in dataframe.columns), None)
    if col is None:
        num_cols = dataframe.select_dtypes(include=["float64", "float32", "int64"]).columns.tolist()
        col = num_cols[0] if num_cols else None
    return col

if DATA_LOADED:
    CITY_STATS  = compute_city_stats(df)
    price_col   = get_price_col(df)
    city_col    = next((c for c in ["City", "city"] if c in df.columns), None)
    TOTAL_PROPS = len(df)
    NUM_CITIES  = df[city_col].nunique() if city_col else "N/A"
    AVG_PRICE   = round(df[price_col].mean(), 2) if price_col else 0
    TOP_CITIES  = df[city_col].value_counts().head(5).index.tolist() if city_col else []
else:
    CITY_STATS  = {}
    TOTAL_PROPS = 0
    NUM_CITIES  = "N/A"
    AVG_PRICE   = 0
    TOP_CITIES  = []

# ── System Prompt (injected into every AI provider) ───────────────────────────
SYSTEM_PROMPT = f"""You are PropBot, an expert AI Real Estate Investment Advisor built into an Indian property intelligence platform.

Platform facts:
- Dataset: {TOTAL_PROPS:,} real Indian properties across {NUM_CITIES} cities (source: {DATA_SOURCE})
- Average listed price: ₹{AVG_PRICE} Lakhs
- Top cities by listings: {', '.join(str(c) for c in TOP_CITIES)}
- ML Models used: XGBoost, CatBoost, LightGBM, Random Forest, Gradient Boosting
- Features analyzed: BHK, Size (sqft), City, Property Age, Floor, Furnished Status, Transport, Parking, Security, Amenities, Availability Status

Your behavior:
1. Always answer in Indian real estate context — use Lakhs/Crores, mention Indian cities.
2. For investment questions give structured advice: Price Estimate → Risk Level → BUY/HOLD/SELL → Reasoning.
3. Keep responses concise (3-5 sentences) unless a detailed breakdown is asked.
4. If asked outside real estate, politely redirect.
5. Never fabricate specific prices — use ranges and qualifiers.
6. End investment advice with: "This is AI-generated analysis, not financial advice."
"""

# ── AI Provider Caller ─────────────────────────────────────────────────────────
def call_ai(provider: str, api_key: str, history: list, user_input: str) -> str:
    """
    Unified AI caller. Supports:
      - gemini    → Google Gemini (gemini-1.5-flash)
      - openai    → OpenAI (gpt-4o-mini)
      - groq      → Groq (llama-3.3-70b-versatile) — free tier
      - mistral   → Mistral AI (mistral-small-latest)
      - cohere    → Cohere (command-r)
      - claude    → Anthropic Claude (claude-haiku-4-5-20251001)
    """
    # Build conversation history (last 10 turns to save tokens)
    recent = history[-10:] if len(history) > 10 else history

    try:
        # ── Gemini ──────────────────────────────────────────────────────────
        if provider == "gemini":
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            # Build contents list from history
            contents = []
            for m in recent:
                contents.append({
                    "role": "user" if m["role"] == "user" else "model",
                    "parts": [{"text": m["content"]}]
                })

            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                contents=contents
            )
            return response.text

        # ── OpenAI ──────────────────────────────────────────────────────────
        elif provider == "openai":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in recent:
                messages.append({"role": m["role"], "content": m["content"]})
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini", "messages": messages, "max_tokens": 600},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        # ── Groq (Free tier — Llama 3.3) ────────────────────────────────────
        elif provider == "groq":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in recent:
                messages.append({"role": m["role"], "content": m["content"]})
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile",
                      "messages": messages, "max_tokens": 600},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        # ── Mistral ─────────────────────────────────────────────────────────
        elif provider == "mistral":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in recent:
                messages.append({"role": m["role"], "content": m["content"]})
            resp = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json={"model": "mistral-small-latest",
                      "messages": messages, "max_tokens": 600},
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        # ── Cohere ──────────────────────────────────────────────────────────
        elif provider == "cohere":
            chat_history = []
            for m in recent[:-1]:
                chat_history.append({
                    "role": "USER" if m["role"] == "user" else "CHATBOT",
                    "message": m["content"]
                })
            resp = requests.post(
                "https://api.cohere.com/v1/chat",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json={
                    "model": "command-r",
                    "message": user_input,
                    "chat_history": chat_history,
                    "preamble": SYSTEM_PROMPT,
                    "max_tokens": 600
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["text"]

        # ── Anthropic Claude ─────────────────────────────────────────────────
        elif provider == "claude":
            messages = []
            for m in recent:
                messages.append({"role": m["role"], "content": m["content"]})
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": api_key,
                         "anthropic-version": "2023-06-01",
                         "Content-Type": "application/json"},
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 600,
                    "system": SYSTEM_PROMPT,
                    "messages": messages
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]

        else:
            return "⚠️ Unknown provider selected."

    except requests.exceptions.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        if code == 401:
            return f"❌ **Invalid API key** for {provider.title()}. Please check the key in the sidebar."
        elif code == 429:
            return f"⏳ **Rate limit hit** for {provider.title()}. Wait a moment and try again."
        else:
            return f"⚠️ **{provider.title()} API error {code}:** {str(e)}"
    except Exception as e:
        return f"⚠️ **Error calling {provider.title()}:** `{str(e)}`"

# ── Intent Detection ───────────────────────────────────────────────────────────
INTENT_PATTERNS = {
    "city_query":           [r"\b(best city|top city|which city|good city|invest.*city|city.*invest)\b",
                              r"\b(mumbai|delhi|bangalore|bengaluru|hyderabad|chennai|pune|kolkata|ahmedabad|jaipur|lucknow|surat|noida|gurugram|gurgaon|kochi)\b"],
    "price_query":          [r"\b(price|cost|worth|value|how much|rate)\b",
                              r"\b(lakhs?|crores?|rupees?|₹)\b"],
    "risk_query":           [r"\b(risk|safe|dangerous|risky|safety)\b"],
    "recommendation_query": [r"\b(buy|sell|hold|should i|invest|recommend|advice|worth it)\b"],
    "bhk_query":            [r"\b([1-5]\s*bhk|bedroom|1bhk|2bhk|3bhk|4bhk)\b"],
    "greeting":             [r"^(hi|hello|hey|good morning|good afternoon|good evening|namaste|hola)[\s!.,]*$"],
    "help":                 [r"\b(help|what can you|capabilities|features|what do you|how do you)\b"],
    "data_query":           [r"\b(dataset|data|how many|records|properties|listings)\b"],
}

def detect_intents(text: str) -> list:
    text_lower = text.lower().strip()
    found = []
    for intent, patterns in INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text_lower):
                found.append(intent)
                break
    return found or ["general"]

def extract_city(text: str) -> str | None:
    text_lower = text.lower()
    # also handle common aliases
    aliases = {"bengaluru": "bangalore", "gurugram": "gurgaon"}
    for alias, canonical in aliases.items():
        if alias in text_lower:
            text_lower = text_lower.replace(alias, canonical)
    for city_key in CITY_STATS:
        if city_key in text_lower:
            return city_key
    return None

def extract_bhk(text: str) -> int | None:
    m = re.search(r"([1-5])\s*bhk", text.lower())
    return int(m.group(1)) if m else None

# ── Rule-based Responses ───────────────────────────────────────────────────────
def rule_based_response(user_input: str) -> str | None:
    intents  = detect_intents(user_input)
    city_key = extract_city(user_input)
    bhk      = extract_bhk(user_input)

    if "greeting" in intents:
        return (
            "👋 **Namaste! I'm PropBot**, your AI real estate advisor.\n\n"
            "I can help you with:\n"
            "- 🏙️ City-wise investment analysis\n"
            "- 💰 Property price ranges\n"
            "- 📊 Buy / Hold / Sell recommendations\n"
            "- ⚠️ Risk assessment\n\n"
            f"I'm currently analyzing **{TOTAL_PROPS:,} properties** from our **{DATA_SOURCE}**.\n\n"
            "Try: *\"Is Bangalore good for investment?\"* or *\"Should I buy a 2BHK in Pune?\"*"
        )

    if "help" in intents:
        return (
            "🤖 **PropBot can answer:**\n\n"
            "- *Which city has the best ROI?*\n"
            "- *Is a 3BHK in Bangalore worth buying?*\n"
            "- *What's the average price in Hyderabad?*\n"
            "- *How risky is an under-construction property?*\n"
            "- *How many properties are in the dataset?*\n\n"
            "For deeper analysis, add an AI API key in the sidebar."
        )

    if "data_query" in intents and DATA_LOADED:
        return (
            f"### 📦 Dataset Info\n\n"
            f"- **Source:** {DATA_SOURCE}\n"
            f"- **Total Properties:** {TOTAL_PROPS:,}\n"
            f"- **Cities Covered:** {NUM_CITIES}\n"
            f"- **Average Price:** ₹{AVG_PRICE} Lakhs\n"
            f"- **Top Markets:** {', '.join(str(c) for c in TOP_CITIES)}\n"
        )

    if city_key and DATA_LOADED:
        stats    = CITY_STATS[city_key]
        bhk_note = f" for a {bhk}BHK" if bhk else ""

        if stats["avg_price"] < 60:
            signal, reason = "**BUY 🟢**", "affordable market with strong entry-level opportunities"
        elif stats["avg_price"] < 120:
            signal, reason = "**BUY/HOLD 🟡**", "mid-range pricing — solid for long-term appreciation"
        elif stats["avg_price"] < 200:
            signal, reason = "**HOLD 🟡**", "moderately premium — evaluate ROI carefully"
        else:
            signal, reason = "**HOLD/SELL 🔴**", "premium pricing — high entry cost, verify ROI before committing"

        return (
            f"### 🏙️ {stats['city']} — Investment Snapshot{bhk_note}\n\n"
            f"| Metric | Value |\n"
            f"|--------|-------|\n"
            f"| Avg Price | ₹{stats['avg_price']} Lakhs |\n"
            f"| Median Price | ₹{stats['median_price']} Lakhs |\n"
            f"| Price Range | ₹{stats['min_price']}L – ₹{stats['max_price']}L |\n"
            f"| Listings in Dataset | {stats['count']:,} |\n\n"
            f"**Signal:** {signal}\n\n"
            f"> {stats['city']} is a {reason}.\n\n"
            f"*This is AI-generated analysis, not financial advice.*"
        )

    if "price_query" in intents and not city_key and DATA_LOADED:
        return (
            f"### 💰 Pan-India Price Overview\n\n"
            f"Based on **{TOTAL_PROPS:,} properties** ({DATA_SOURCE}):\n\n"
            f"- 📊 **Average Price:** ₹{AVG_PRICE} Lakhs\n"
            f"- 🏙️ **Cities:** {NUM_CITIES}\n"
            f"- 🔝 **Most Active:** {', '.join(str(c) for c in TOP_CITIES[:3])}\n\n"
            f"Mention a city for specific data — e.g. *\"price in Bangalore\"*."
        )

    if "risk_query" in intents and not city_key:
        return (
            "### ⚠️ Property Risk Factors\n\n"
            "| Factor | Low Risk ✅ | High Risk ❌ |\n"
            "|--------|------------|-------------|\n"
            "| Property Age | < 5 years | > 20 years |\n"
            "| Availability | Ready-to-Move | Under Construction |\n"
            "| Floor | Lower floors | Top floor, old building |\n"
            "| Infrastructure | High growth area | Stagnant locality |\n"
            "| Transport | High accessibility | Low accessibility |\n\n"
            "Use the **⚠️ Risk Analysis** page for a specific risk score.\n\n"
            "*Always verify legal documents before investing.*"
        )

    return None  # no rule matched → go to AI

# ── Sidebar ────────────────────────────────────────────────────────────────────
if "api_keys" not in st.session_state:
    st.session_state.api_keys = {}

if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = "groq"
    
with st.sidebar:
    st.markdown("## 🤖 PropBot Settings")
    st.markdown("---")

    # Dataset status
    if DATA_LOADED:
        st.success(f"✅ Dataset: **{DATA_SOURCE}**\n\n{TOTAL_PROPS:,} properties loaded")
    else:
        st.error("❌ No dataset found. Expected `data/processed/cleaned_df.csv`.")

    st.markdown("---")

    # Provider selector
    provider = st.selectbox(
            "🧠 AI Provider",
            options=["gemini", "openai", "groq", "mistral", "cohere", "claude"],
            index=["gemini", "openai", "groq", "mistral", "cohere", "claude"].index(
            st.session_state.selected_provider
        ),
        format_func=lambda x: {
            "gemini":  "🔵 Google Gemini (gemini-2.0-flash-lite)",
            "openai":  "🟢 OpenAI (gpt-4o-mini)",
            "groq":    "🟠 Groq — FREE (Llama 3.3 70B)",
            "mistral": "🔷 Mistral AI (mistral-small)",
            "cohere":  "🟣 Cohere (command-r)",
            "claude":  "🟤 Anthropic Claude (haiku)",
        }[x],
        help="Select whichever provider you have an API key for."
    )

    st.session_state.selected_provider = provider


    api_links = {
        "gemini":  "https://aistudio.google.com",
        "openai":  "https://platform.openai.com/api-keys",
        "groq":    "https://console.groq.com/keys",
        "mistral": "https://console.mistral.ai",
        "cohere":  "https://dashboard.cohere.com/api-keys",
        "claude":  "https://console.anthropic.com",
    }

    api_key = st.text_input(
        f"API Key for {provider.title()}",
        value=st.session_state.api_keys.get(provider, ""),
        type="password",
        placeholder="Paste your API key here...",
        help=f"Get key → {api_links[provider]}"
    )

    st.session_state.api_keys[provider] = api_key

    if api_key:
        st.success(f"✅ Key set for {provider.title()}")
        st.caption(f"[Get / manage key]({api_links[provider]})")
    else:
        st.info(f"💡 No key? Rule-based answers still work.\n\n[Get free key →]({api_links[provider]})")

    st.markdown("---")

    # Install hint
    install_hints = {
        "gemini":  "`pip install google-genai`",
        "openai":  "`pip install openai`  *(or use requests — already works)*",
        "groq":    "No extra install needed ✅",
        "mistral": "No extra install needed ✅",
        "cohere":  "No extra install needed ✅",
        "claude":  "No extra install needed ✅",
    }
    st.caption(f"**Install:** {install_hints[provider]}")

    st.markdown("---")

    # Quick questions
    st.markdown("### 💬 Quick Questions")
    quick_qs = [
        "Which city is best for investment?",
        "Is Mumbai overpriced?",
        "Should I buy under-construction property?",
        "What's the risk of old properties?",
        "Show me dataset stats",
    ]
    for q in quick_qs:
        if st.button(q, use_container_width=True, key=f"q_{q[:15]}"):
            st.session_state["quick_input"] = q

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state["messages"]  = []
        st.session_state["ai_history"] = []
        st.rerun()

    st.caption("PropBot uses rule-based analysis + your chosen AI provider.\nNot financial advice.")

# ── Main UI ────────────────────────────────────────────────────────────────────
st.title("🤖 PropBot — AI Real Estate Chat Assistant")
st.markdown("""
<div class='re-card' style='border-color:#1A2F5A;padding:12px 20px;margin-bottom:8px'>
    <div style='display:flex;align-items:center;gap:10px'>
        <span style='font-size:18px'>←</span>
        <div>
            <span style='font-size:13px;color:#60A5FA;font-weight:600'>PropBot settings are in the sidebar</span>
            <span style='font-size:12px;color:#6B6F87;margin-left:8px'>Scroll down in the left panel to select Ai model and set api key</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
st.caption(
    f"Powered by **{provider.title()}** · "
    f"Dataset: **{DATA_SOURCE}** ({TOTAL_PROPS:,} properties) · "
    "Ask anything about Indian real estate."
)
st.markdown("---")

# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": (
                "👋 **Namaste! I'm PropBot.**\n\n"
                f"I'm analyzing **{TOTAL_PROPS:,} properties** from our **{DATA_SOURCE}** "
                f"across **{NUM_CITIES} Indian cities**.\n\n"
                "**Try asking:**\n"
                "- *\"Is Bangalore good for investment?\"*\n"
                "- *\"What's the average price in Hyderabad?\"*\n"
                "- *\"Should I buy a 2BHK in Pune?\"*\n"
                "- *\"Which city has best ROI?\"*"
            )
        }
    ]

if "ai_history" not in st.session_state:
    st.session_state["ai_history"] = []

# ── Render Chat ────────────────────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "🧑"):
        st.markdown(msg["content"])

# ── Input ──────────────────────────────────────────────────────────────────────
user_text = None
if "quick_input" in st.session_state and st.session_state["quick_input"]:
    user_text = st.session_state.pop("quick_input")

typed = st.chat_input("Ask about any Indian city, property type, investment strategy...")
if typed:
    user_text = typed

# ── Process ────────────────────────────────────────────────────────────────────
if user_text:
    st.session_state["messages"].append({"role": "user", "content": user_text})
    st.session_state["ai_history"].append({"role": "user", "content": user_text})

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_text)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner(f"PropBot thinking via {provider.title()}..."):

            # Rule-based first
            response = rule_based_response(user_text)

            # Fall through to AI provider
            if response is None:
                if api_key:
                    response = call_ai(
                        provider, api_key,
                        st.session_state["ai_history"],
                        user_text
                    )
                else:
                    response = (
                        f"🔑 **No API key set for {provider.title()}.**\n\n"
                        "I couldn't find a rule-based answer for that specific question.\n\n"
                        "**Options:**\n"
                        f"1. Add a **{provider.title()} API key** in the sidebar\n"
                        "2. Switch to **Groq** in the sidebar — it's free\n"
                        "3. Ask a city-specific question like *\"Tell me about Pune\"*"
                    )

        st.markdown(response)

    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.session_state["ai_history"].append({"role": "assistant", "content": response})

    # Keep history lean
    if len(st.session_state["ai_history"]) > 20:
        st.session_state["ai_history"] = st.session_state["ai_history"][-20:]