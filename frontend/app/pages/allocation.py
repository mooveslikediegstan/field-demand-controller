# frontend/app/pages/allocation.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import api_client as api


def show():
    st.title("Alocação de Técnicos")

    tab_alocar, tab_desalocar = st.tabs(["Alocar", "Desalocar"])

    # ── ALOCAR ────────────────────────────────────────────────────────────────
    with tab_alocar:
        st.subheader("Alocar Técnico em Demanda")

        demand_id     = st.number_input("ID da Demanda", min_value=1, step=1, key="alocar_demand")
        technician_id = st.number_input("ID do Técnico", min_value=1, step=1, key="alocar_tech")

        if st.button("Alocar"):
            try:
                result = api.allocate_technician(int(demand_id), int(technician_id))
                st.success(f"Técnico #{result['technician_id']} alocado na demanda #{result['demand_id']}!")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── DESALOCAR ─────────────────────────────────────────────────────────────
    with tab_desalocar:
        st.subheader("Desalocar Técnico de Demanda")

        demand_id     = st.number_input("ID da Demanda", min_value=1, step=1, key="desalocar_demand")
        technician_id = st.number_input("ID do Técnico", min_value=1, step=1, key="desalocar_tech")

        if st.button("Desalocar"):
            try:
                result = api.deallocate_technician(int(demand_id), int(technician_id))
                st.success(f"Técnico desalocado. Status da demanda: {result['status']}")
            except Exception as e:
                st.error(f"Erro: {e}")