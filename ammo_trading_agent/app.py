# app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

from ammo_agent import AmmoAgent
from config import APP_TITLE
from utils.helpers import format_currency
from utils.constants import DEFAULT_SYMBOL

# --- Page Configuration ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Custom CSS ---
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {file_name}. Using default styles.")

# Construct path to CSS file to be robust for local and cloud deployment
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_FILE = os.path.join(APP_DIR, "assets", "style.css")
load_css(CSS_FILE)

# --- Main Application ---

# --- Header ---
# st.image("assets/logo.png", width=100) # Uncomment when you add logo.png
st.title(APP_TITLE)
st.markdown("An AI-powered agent for market analysis and trading recommendations.")

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("Settings")
    symbol = st.text_input("Stock Symbol", value=DEFAULT_SYMBOL).upper()
    time_frame = st.selectbox(
        "Time Frame",
        ("Daily", "Weekly", "Intraday (60min)"),
        index=0  # Default to Daily
    )
    portfolio_value = st.number_input("Portfolio Value ($)", min_value=1000.0, value=100000.0, step=1000.0)

    analyze_button = st.button("Analyze Market", use_container_width=True)

# --- Initialize Agent in Session State ---
if "agent" not in st.session_state:
    st.session_state.agent = AmmoAgent(portfolio_value=portfolio_value)
if "results" not in st.session_state:
    st.session_state.results = None

# --- Main Dashboard ---
if analyze_button:
    with st.spinner(f"AMMO Agent is analyzing {symbol}..."):
        # Update agent with the latest portfolio value from sidebar
        st.session_state.agent.risk_manager.portfolio_value = portfolio_value
        st.session_state.results = st.session_state.agent.run_analysis(symbol, time_frame)

# --- Display Results ---
if st.session_state.results:
    results = st.session_state.results

    if "error" in results:
        st.error(results["error"])
    else:
        # --- Summary Header ---
        st.header(f"Analysis for {results['symbol']}")

        recommendation = results['recommendation']
        signal = recommendation['signal']
        reason = recommendation['reason']
        should_trade = recommendation['should_trade']

        rec_color = "red" if "SELL" in signal else "green" if "BUY" in signal else "orange"

        st.markdown(f"### **Recommendation: <span style='color:{rec_color};'>{signal}</span>**", unsafe_allow_html=True)

        # --- Satisfaction Note / Reason ---
        st.info(f"**Trade Rationale:** {reason}")

        # --- Key Metrics ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Latest Price", format_currency(results['latest_price']))
        col2.metric("Market Personality", results['market_personality'])
        col3.metric("Sentiment Score", f"{results['sentiment']['sentiment_score']:.2f}")

        # --- Price Chart ---
        st.subheader("Price History")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=results['price_data'].index,
            open=results['price_data']['open'],
            high=results['price_data']['high'],
            low=results['price_data']['low'],
            close=results['price_data']['close'],
            name='Price'
        ))
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            title=f"{results['symbol']} {time_frame} Price",
            xaxis_title="Date",
            yaxis_title="Price (USD)"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- Detailed Analysis Tabs ---
        tab1, tab2, tab3 = st.tabs(["Risk Assessment", "Sentiment Details", "Raw Data"])

        with tab1:
            st.subheader("Trade Execution Plan")
            risk = results['risk_assessment']

            if should_trade:
                st.write(f"**Portfolio Value:** {format_currency(risk['portfolio_value'])}")
                st.write(f"**Suggested Position Size:** {risk['position_size']} shares")
                st.write(f"**Suggested Stop-Loss Price:** {format_currency(risk['stop_loss_price'])}")
                st.write(f"**Suggested Target Price:** {format_currency(risk['target_price'])}")
                st.write(f"**Risk/Reward Ratio:** {risk['risk_reward_ratio']}")
                st.info("This is a simplified risk assessment based on a 2% portfolio risk per trade.")
            else:
                st.success("No trade is recommended, so no risk parameters have been calculated.")

        with tab2:
            st.subheader("Sentiment Analysis Details")
            st.write(results['sentiment']['summary'])

        with tab3:
            st.subheader("Raw Price Data")
            st.dataframe(results['price_data'].tail(10))

else:
    st.info("Enter a stock symbol in the sidebar and click 'Analyze Market' to begin.")