# frontend/app/pages/demands.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import api_client as api

from constants import PROBLEM_HIERARCHY, VALID_EQUIPMENTS, VALID_TECHNICAL_REASONS, DEMAND_STATUS

def show():
    st.title("Demandas")

    tab_criar, tab_buscar, tab_listar = st.tabs(["Criar Demanda", "Buscar / Editar", "Listar Demandas"])

    # ── CRIAR ─────────────────────────────────────────────────────────────────
    with tab_criar:
        st.subheader("Nova Demanda")

        with st.form("form_criar"):
            demand_title        = st.text_input("Título")
            problem_description = st.text_area("Descrição do Problema")
            project_id          = st.text_input("ID do Projeto")
            responsible_id      = st.number_input("ID do Analista Responsável", min_value=1, step=1)
            estimated_time      = st.number_input("Tempo Estimado (horas)", min_value=0.5, step=0.5)

            technical_visit_reason = st.selectbox("Motivo da Visita", VALID_TECHNICAL_REASONS)

            causal_sector = st.selectbox("Setor Causador", list(PROBLEM_HIERARCHY.keys()))
            causal_area   = st.selectbox("Área Causadora", list(PROBLEM_HIERARCHY[causal_sector].keys()))
            root_cause    = st.selectbox("Causa Raiz", PROBLEM_HIERARCHY[causal_sector][causal_area])
            equipment     = st.selectbox("Equipamento", VALID_EQUIPMENTS)

            submitted = st.form_submit_button("Criar Demanda")

        if submitted:
            try:
                result = api.create_demand({
                    "demand_title":           demand_title,
                    "problem_description":    problem_description,
                    "project_id":             project_id,
                    "responsible_id":         int(responsible_id),
                    "estimated_time":         estimated_time,
                    "technical_visit_reason": technical_visit_reason,
                    "causal_sector":          causal_sector,
                    "causal_area":            causal_area,
                    "root_cause":             root_cause,
                    "equipment":              equipment,
                })
                st.success(f"Demanda #{result['demand_id']} criada com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")

    # ── BUSCAR / EDITAR ───────────────────────────────────────────────────────
    with tab_buscar:
        st.subheader("Buscar Demanda")

        demand_id = st.number_input("ID da Demanda", min_value=1, step=1, key="buscar_id")
        if st.button("Buscar"):
            try:
                d = api.get_demand(int(demand_id))
                st.session_state["demand_encontrada"] = d
            except Exception as e:
                st.error(f"Erro: {e}")

        if "demand_encontrada" in st.session_state:
            d = st.session_state["demand_encontrada"]
            st.json(d)

            if d["status"] not in ["Concluída", "Cancelada"]:
                if st.button("Cancelar esta Demanda"):
                    try:
                        api.cancel_demand(d["demand_id"])
                        st.success("Demanda cancelada.")
                        del st.session_state["demand_encontrada"]
                    except Exception as e:
                        st.error(f"Erro: {e}")

    # ── LISTAR ───────────────────────────────────────────────────────                        
    with tab_listar:
        st.subheader("Listar Demandas")

        status = st.selectbox("Status",DEMAND_STATUS)
        if st.button("Listar"):
            try:
                d = api.list_demands(status)
                st.session_state["demand_encontrada"] = d
            except Exception as e:
                st.error(f"Erro: {e}")

        if "demand_encontrada" in st.session_state:
            d = st.session_state["demand_encontrada"]
            st.json(d)                     