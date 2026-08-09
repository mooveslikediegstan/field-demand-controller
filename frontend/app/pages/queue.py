# frontend/app/pages/queue.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import api_client as api


def show():
    st.title("Fila do Técnico")

    technician_id = st.number_input("ID do Técnico", min_value=1, step=1, key="queue_tech_id")

    if st.button("Carregar Fila"):
        try:
            fila = api.get_queue(int(technician_id))
            st.session_state["fila"] = fila
        except Exception as e:
            st.error(f"Erro: {e}")

    if "fila" not in st.session_state or not st.session_state["fila"]:
        return

    fila = st.session_state["fila"]

    st.subheader("Ordem atual")
    for i, item in enumerate(fila):
        st.write(f"{i+1}. **{item['demand_title']}** — {item['estimated_time']}h — {item['status']}")

    st.divider()
    st.subheader("Reordenar")
    st.caption("Informe os IDs na nova ordem desejada, separados por vírgula.")

    ids_disponiveis = [str(item['demand_manager_id']) for item in fila]
    st.caption(f"IDs disponíveis: {', '.join(ids_disponiveis)}")

    nova_ordem = st.text_input("Nova ordem (ex: 3, 1, 2)")

    if st.button("Salvar Sequência"):
        try:
            ordered_ids = [int(x.strip()) for x in nova_ordem.split(",")]
            resultado = api.save_sequence(int(technician_id), ordered_ids)
            st.session_state["fila"] = resultado
            st.success("Sequência salva e planejamento atualizado!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")