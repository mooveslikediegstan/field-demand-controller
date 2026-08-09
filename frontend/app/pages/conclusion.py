# frontend/app/pages/conclusion.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import api_client as api


def show():
    st.title("Conclusão de Ordem")

    dm_id = st.number_input("ID do Demand Manager", min_value=1, step=1, key="conclusion_dm_id")

    if st.button("Carregar Dados"):
        try:
            dados = api.get_conclusion_data(int(dm_id))
            st.session_state["conclusion_dados"] = dados
        except Exception as e:
            st.error(f"Erro: {e}")

    if "conclusion_dados" not in st.session_state:
        return

    dados = st.session_state["conclusion_dados"]

    st.subheader("Dados da Ordem")
    st.write(f"**Demanda:** {dados['demand_title']}")
    st.write(f"**Projeto:** {dados['project_id']}")
    st.write(f"**Técnico ID:** {dados['technician_id']}")
    st.write(f"**Tempo Estimado:** {dados['estimated_time']}h")

    st.divider()
    st.subheader("Registrar Conclusão")

    with st.form("form_conclusao"):
        actual_time     = st.number_input("Tempo Real (horas)", min_value=0.5, step=0.5)
        travel_time     = st.number_input("Tempo de Deslocamento (horas)", min_value=0.0, step=0.5)
        travel_distance = st.number_input("Distância Percorrida (km)", min_value=0.0, step=1.0)
        finish_date     = st.date_input("Data de Conclusão")

        submitted = st.form_submit_button("Concluir Ordem")

    if submitted:
        try:
            result = api.conclude_demand(int(dm_id), {
                "actual_time":      actual_time,
                "travel_time":      travel_time,
                "travel_distance":  travel_distance,
                "finish_date":      finish_date.isoformat(),
            })
            st.success(f"Ordem concluída! Status da demanda: {result['status']}")
            del st.session_state["conclusion_dados"]
        except Exception as e:
            st.error(f"Erro: {e}")