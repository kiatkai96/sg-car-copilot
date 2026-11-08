"""The web page you and visitors will use.   Run with:  streamlit run app.py"""
import streamlit as st

from src.calculator import total_cost_of_ownership
from src.config import DATA_AS_OF
from src.llm import answer_question

from src.config import DB_DIR

# If the search index doesn't exist yet (e.g. first launch after publishing online),
# build it automatically from the files in the data folder.
if not DB_DIR.exists():
    from src.ingest import main as build_index
    build_index()

st.set_page_config(page_title="SG Car Copilot", page_icon="🚗")
st.title("🚗 SG Car Copilot")
st.caption(f"Ask about buying and owning a car in Singapore. Data as of: {DATA_AS_OF}. "
           "Always double-check official sources (LTA / OneMotoring) before big decisions.")

tab_ask, tab_calc = st.tabs(["Ask a question", "Cost calculator"])

# ---------- Tab 1: ask questions ----------
with tab_ask:
    examples = [
        "What is a COE and how long does it last?",
        "How does the PARF rebate work?",
        "What was the Category A COE premium in my latest data?",
        "Which cars in your list are SUVs?",
    ]
    st.write("Try one:")
    cols = st.columns(2)
    clicked = None
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex{i}"):
            clicked = ex

    question = st.text_input("Your question", value=clicked or "")
    if question:
        with st.spinner("Searching my notes..."):
            try:
                answer, chunks = answer_question(question)
            except Exception as e:  # show friendly error instead of a crash
                st.error(f"Something went wrong: {e}")
                st.stop()
        st.markdown(answer)
        with st.expander("Sources used (what the AI was shown)"):
            for i, c in enumerate(chunks, 1):
                st.markdown(f"**[{i}] {c['source']}**  _(distance {c['distance']:.2f})_")
                st.text(c["text"])

# ---------- Tab 2: calculator ----------
with tab_calc:
    st.write("Type in your own numbers. The calculator just does the sums.")
    c1, c2 = st.columns(2)
    price = c1.number_input("Purchase price, incl. COE (S$)", 0, 2_000_000, 120_000, step=1000)
    resale = c2.number_input("Expected resale / scrap value (S$)", 0, 2_000_000, 40_000, step=1000)
    years = c1.number_input("Years you'll keep it", 1, 20, 10)
    tax = c2.number_input("Road tax per year (S$)", 0, 20_000, 1_000, step=50)
    ins = c1.number_input("Insurance per year (S$)", 0, 20_000, 1_500, step=100)
    fuel = c2.number_input("Fuel per year (S$)", 0, 20_000, 2_400, step=100)
    park = c1.number_input("Parking per year (S$)", 0, 20_000, 1_200, step=100)
    maint = c2.number_input("Maintenance per year (S$)", 0, 20_000, 1_000, step=100)

    r = total_cost_of_ownership(price, years, resale, tax, ins, fuel, park, maint)
    st.metric("Total cost over the period", f"S${r['total_cost']:,.0f}")
    m1, m2 = st.columns(2)
    m1.metric("Per year", f"S${r['per_year']:,.0f}")
    m2.metric("Per month", f"S${r['per_month']:,.0f}")
    st.caption(f"Loss in value: S${r['depreciation_total']:,.0f}  |  "
               f"Running costs: S${r['running_costs_total']:,.0f}")
    st.caption("The default numbers above are placeholders, not real quotes.")
