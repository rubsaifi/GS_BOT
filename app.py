# """
# Goal Optimization Assistant — Full Working Version
# Run: streamlit run app.py
# """
# import streamlit as st
# import pandas as pd
# import os
# from dotenv import load_dotenv
# from utils.rag_engine import load_data, create_vector_db, search
# from utils.llm_groq import ask_goalbot_rag

# # ── Load env ──────────────────────────────────────────────
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# # ── Load Excel Data ───────────────────────────────────────
# kpi_df, scoring_df = load_data()  # ✅ correctly unpacks 2 DataFrames

# # ── Create combined DF + Vector DB ────────────────────────
# df = pd.concat([kpi_df, scoring_df], axis=0, ignore_index=True)
# index, embeddings = create_vector_db(df)

# # ── Page Config ──────────────────────────────────────────
# st.set_page_config(page_title="Goal Optimization Bot 🎯", layout="wide")

# # ── Custom CSS ───────────────────────────────────────────
# st.markdown("""
# <style>
#     .main-header {
#         background: linear-gradient(135deg, #0f172a, #1e3a8a);
#         color: white;
#         padding: 25px;
#         border-radius: 12px;
#         text-align: center;
#         margin-bottom: 20px;
#     }

#     .chat-user {
#         background: #e0f2fe;
#         padding: 12px;
#         border-radius: 10px;
#         margin: 8px 0;
#         border-left: 5px solid #0284c7;
#     }

#     .chat-bot {
#         background: #ecfdf5;
#         padding: 12px;
#         border-radius: 10px;
#         margin: 8px 0;
#         border-left: 5px solid #059669;
#     }

#     .sidebar-box {
#         background: #f8fafc;
#         padding: 10px;
#         border-radius: 10px;
#         margin-bottom: 10px;
#     }

#     .stButton > button {
#         border-radius: 10px;
#         width: 100%;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ── Session State ─────────────────────────────────────────
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # ── Sidebar ──────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("## ⚙️ Dashboard")
#     st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
#     st.write(f"📊 KPI Rows: {len(kpi_df)}")
#     st.write(f"📈 Scoring Rows: {len(scoring_df)}")
#     st.markdown('</div>', unsafe_allow_html=True)

#     if st.button("🗑️ Clear Chat"):
#         st.session_state.chat_history = []
#         st.rerun()  # ✅ replaced deprecated st.experimental_rerun()

# # ── Header ───────────────────────────────────────────────
# st.markdown("""
# <div class="main-header">
#     <h1>🎯 Goal Optimization Assistant</h1>
#     <p>AI Assistant for SR_BSOM Goal Sheet</p>
# </div>
# """, unsafe_allow_html=True)

# # ── Quick Action Buttons ──────────────────────────────────
# st.markdown("### ⚡ Quick Actions")
# col1, col2, col3, col4 = st.columns(4)
# quick_questions = [
#     "How to score 100?",
#     "What needs to be improved?",
#     "Key focus parameters?",
#     "Any negative scoring?"
# ]
# cols = [col1, col2, col3, col4]

# for i, q in enumerate(quick_questions):
#     if cols[i].button(q):
#         st.session_state.chat_history.append({"role": "user", "content": q})

#         with st.spinner("🤖 Thinking..."):
#             context_chunks = search(q, df, index)
#             response = ask_goalbot_rag(
#                 question=q,
#                 context_chunks=context_chunks,
#                 api_key=GROQ_API_KEY
#             )
#         st.session_state.chat_history.append({"role": "assistant", "content": response})
#         st.rerun()  # ✅ replaced deprecated st.experimental_rerun()

# # ── Chat Display ─────────────────────────────────────────
# st.markdown("### 💬 Chat")
# for msg in st.session_state.chat_history:
#     if msg["role"] == "user":
#         st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
#     else:
#         st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

# # ── Chat Input ───────────────────────────────────────────
# user_input = st.chat_input("Ask anything about your goal sheet...")

# if user_input:
#     st.session_state.chat_history.append({"role": "user", "content": user_input})

#     with st.chat_message("assistant"):
#         with st.spinner("🤖 Thinking..."):
#             context_chunks = search(user_input, df, index)
#             response = ask_goalbot_rag(
#                 question=user_input,
#                 context_chunks=context_chunks,
#                 api_key=GROQ_API_KEY
#             )
#             st.markdown(response)

#     st.session_state.chat_history.append({"role": "assistant", "content": response})



"""
Goal Optimization Assistant — Multi Role Version
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from utils.rag_engine import load_data, create_vector_db, search, ROLE_FILES
from utils.llm_groq import ask_goalbot_rag

# ── Load env ──────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Page Config ───────────────────────────────────────────
st.set_page_config(page_title="GoalBot 🎯", layout="wide")

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    .role-card {
        background: #f0f9ff;
        border: 2px solid #0284c7;
        border-radius: 14px;
        padding: 25px;
        text-align: center;
        cursor: pointer;
        transition: 0.2s;
        margin: 8px;
    }
    .role-card:hover {
        background: #e0f2fe;
    }
    .role-selected {
        background: #0284c7;
        color: white;
        border-radius: 14px;
        padding: 25px;
        text-align: center;
        margin: 8px;
    }
    .chat-user {
        background: #e0f2fe;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 5px solid #0284c7;
    }
    .chat-bot {
        background: #ecfdf5;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 5px solid #059669;
    }
    .sidebar-box {
        background: #f8fafc;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# ══════════════════════════════════════════════════════════
# SCREEN 1 — Role Selection
# ══════════════════════════════════════════════════════════
if st.session_state.selected_role is None:

    st.markdown("""
    <div class="main-header">
        <h1>🎯 Goal Optimization Assistant</h1>
        <p>Please select your role to get started</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 👤 Who are you?")
    st.markdown("Select your role below to load your personalized Goal Sheet Assistant.")
    st.markdown("---")

    roles = {
        "TSE": {
            "icon": "🧑‍💼",
            "label": "TSE",
            "desc": "Territory Sales Executive",
            "key": "ABSOM_TSE"
        },
        "BSOM": {
            "icon": "📋",
            "label": "BSOM",
            "desc": "Branch Service Operations Manager",
            "key": "BSOM"
        },
        "ABSOM": {
            "icon": "📊",
            "label": "ABSOM",
            "desc": "Area Branch Service Operations Manager",
            "key": "ABSOM_TSE"
        },
        "SR_BSOM": {
            "icon": "🏆",
            "label": "SR. BSOM",
            "desc": "Senior Branch Service Operations Manager",
            "key": "SR_BSOM"
        }
    }

    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]

    for i, (role_id, role_info) in enumerate(roles.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="role-card">
                <h1>{role_info['icon']}</h1>
                <h3>{role_info['label']}</h3>
                <p style="color:#64748b; font-size:13px">{role_info['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Select {role_info['label']}", key=f"btn_{role_id}"):
                st.session_state.selected_role = role_info["key"]
                st.session_state.chat_history = []
                st.session_state.data_loaded = False
                st.rerun()

# ══════════════════════════════════════════════════════════
# SCREEN 2 — Chat Interface
# ══════════════════════════════════════════════════════════
else:
    role = st.session_state.selected_role

    # ── Load data once per role ───────────────────────────
    if not st.session_state.data_loaded:
        with st.spinner(f"⏳ Loading {role} Goal Sheet data..."):
            kpi_df, scoring_df = load_data(role)
            df = pd.concat([kpi_df, scoring_df], axis=0, ignore_index=True)
            index, embeddings = create_vector_db(df)

            st.session_state.kpi_df = kpi_df
            st.session_state.scoring_df = scoring_df
            st.session_state.df = df
            st.session_state.index = index
            st.session_state.data_loaded = True
        st.rerun()

    # ── Restore from session ──────────────────────────────
    kpi_df = st.session_state.kpi_df
    scoring_df = st.session_state.scoring_df
    df = st.session_state.df
    index = st.session_state.index

    # ── Sidebar ───────────────────────────────────────────
    with st.sidebar:
        st.markdown("## ⚙️ Dashboard")

        st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
        st.markdown(f"**🎭 Role:** `{role}`")
        st.write(f"📊 KPI Rows: {len(kpi_df)}")
        st.write(f"📈 Scoring Rows: {len(scoring_df)}")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🔄 Switch Role"):
            st.session_state.selected_role = None
            st.session_state.data_loaded = False
            st.session_state.chat_history = []
            st.rerun()

        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # ── Header ────────────────────────────────────────────
    st.markdown(f"""
    <div class="main-header">
        <h1>🎯 Goal Optimization Assistant</h1>
        <p>AI Assistant for <strong>{role}</strong> Goal Sheet</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick Action Buttons ──────────────────────────────
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    quick_questions = [
        "How to score 100?",
        "What needs to be improved?",
        "Key focus parameters?",
        "Any negative scoring?"
    ]
    cols = [col1, col2, col3, col4]

    for i, q in enumerate(quick_questions):
        if cols[i].button(q):
            st.session_state.chat_history.append({"role": "user", "content": q})
            with st.spinner("🤖 Thinking..."):
                context_chunks = search(q, df, index)
                response = ask_goalbot_rag(
                    question=q,
                    context_chunks=context_chunks,
                    api_key=GROQ_API_KEY,
                    role=role
                )
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

    # ── Chat Display ──────────────────────────────────────
    st.markdown("### 💬 Chat")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # ── Chat Input ────────────────────────────────────────
    user_input = st.chat_input(f"Ask anything about your {role} goal sheet...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                context_chunks = search(user_input, df, index)
                response = ask_goalbot_rag(
                    question=user_input,
                    context_chunks=context_chunks,
                    api_key=GROQ_API_KEY,
                    role=role
                )
                st.markdown(response)

        st.session_state.chat_history.append({"role": "assistant", "content": response})