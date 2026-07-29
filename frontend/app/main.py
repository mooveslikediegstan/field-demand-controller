# frontend/app/main.py
import streamlit as st

st.set_page_config(page_title="Gestão de Agenda Técnica", layout="wide")

st.sidebar.title("Menu")
page = st.sidebar.radio("Navegar para:", [
    "Demandas",
    "Alocação",
    "Fila do Técnico",
    "Gantt",
    "Conclusão de Ordem",
])

if page == "Demandas":
    from pages.demands import show
    show()
elif page == "Alocação":
    from pages.allocation import show
    show()
elif page == "Fila do Técnico":
    from pages.queue import show
    show()
elif page == "Gantt":
    from pages.gantt import show
    show()
elif page == "Conclusão de Ordem":
    from pages.conclusion import show
    show()