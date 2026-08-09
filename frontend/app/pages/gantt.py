# frontend/app/pages/gantt.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import api_client as api


def show():
    st.title("Gantt — Planejamento do Técnico")

    technician_id = st.number_input("ID do Técnico", min_value=1, step=1, key="gantt_tech_id")

    if st.button("Carregar Planejamento"):
        try:
            gantt = api.get_gantt(int(technician_id))
            st.session_state["gantt"] = gantt
        except Exception as e:
            st.error(f"Erro: {e}")

    if "gantt" not in st.session_state or not st.session_state["gantt"]:
        return

    gantt = st.session_state["gantt"]

    st.subheader("Planejamento")
    for item in gantt:
        st.write(
            f"📋 **{item['demand_title']}** — "
            f"{item['start_date']} até {item['finish_date']}"
        )