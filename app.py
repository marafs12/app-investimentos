import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Nome do arquivo onde os dados serão salvos permanentemente
ARQUIVO_DADOS = "carteira.csv"
ARQUIVO_META = "meta.txt"

# Configuração da página
st.set_page_config(
    page_title="Planejamento de Aposentadoria",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização visual moderna
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARREGAR DADOS SALVOS ---
if os.path.exists(ARQUIVO_DADOS):
    df_dados = pd.read_csv(ARQUIVO_DADOS)
else:
    df_dados = pd.DataFrame(columns=["Ativo", "Categoria", "Valor (R$)"])

# Carregar meta salva ou usar padrão
meta_inicial = 500000.0
if os.path.exists(ARQUIVO_META):
    try:
        with open(ARQUIVO_META, "r") as f:
            meta_inicial = float(f.read())
    except:
        pass

if 'meta' not in st.session_state:
    st.session_state.meta = meta_inicial

# --- BARRA LATERAL ---
st.sidebar.markdown("## 🏖️ Liberdade & Aposentadoria")
st.sidebar.markdown("---")

nova_meta = st.sidebar.number_input(
    "🎯 Meta de Patrimônio Final (R$)", 
    min_value=0.0, 
    value=float(st.session_state.meta), 
    step=10000.0,
    format="%.2f"
)

if nova_meta != st.session_state.meta:
    st.session_state.meta = nova_meta
    with open(ARQUIVO_META, "w") as f:
        f.write(str(nova_meta))

st.sidebar.markdown("---")
st.sidebar.info("💡 **Foco:** Cada aporte aproxima o dia de largar o trabalho e viver dos rendimentos!")

# --- TELA PRINCIPAL ---
st.title("🏖️ Painel de Independência Financeira")
st.markdown("Acompanhe a construção do seu patrimônio rumo à aposentadoria e liberdade de tempo.")

# Cálculos gerais
total_investido = df_dados["Valor (R$)"].sum() if not df_dados.empty else 0.0
progresso = min(total_investido / st.session_state.meta, 1.0) if st.session_state.meta > 0 else 0.0
falta = max(st.session_state.meta - total_investido, 0.0)

# Exibição de Métricas Principais
col1, col2, col3 = st.columns(3)
col1.metric("💰 Patrimônio Acumulado", f"R$ {total_investido:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))
col2.metric("🎯 Meta de Aposentadoria", f"R$ {st.session_state.meta:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))
col3.metric("⏳ Falta para a Liberdade", f"R$ {falta:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."))

# Barra de Progresso da Independência
st.markdown("### 📈 Progresso Rumo à Liberdade")
st.progress(progresso, text=f"Independência financeira alcançada em: {progresso * 100:.2f}%")

st.markdown("---")

# --- ABAS DE NAVEGAÇÃO ---
aba_visao, aba_adicionar, aba_gerenciar = st.tabs(["📊 Visão Geral & Gráficos", "➕ Adicionar Aporte", "🛠️ Gerenciar Ativos"])

with aba_visao:
    if not df_dados.empty:
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("Composição da Carteira")
            dados_agrupados = df_dados.groupby("Categoria")["Valor (R$)"].sum().reset_index()
            
            fig = px.pie(
                dados_agrupados, 
                names='Categoria', 
                values='Valor (R$)', 
                hole=0.5,
                color_discrete_sequence=px.colors.sequential.Tealgrn
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_graf2:
            st.subheader("Valores por Categoria")
            st.dataframe(dados_agrupados.style.format({"Valor (R$)": "R$ {:,.2f}"}), hide_index=True, use_container_width=True)
    else:
        st.info("Ainda não há investimentos cadastrados. Vá na aba 'Adicionar Aporte' para começar!")

with aba_adicionar:
    st.subheader("Registrar Novo Aporte para o Futuro")
    
    with st.form("form_aporte", clear_on_submit=True):
        f_ativo = st.text_input("Nome do Ativo (ex: Tesouro IPCA+, MXRF11, Ações)")
        f_cat = st.selectbox("Categoria", ["Renda Fixa", "Ações", "Fundos Imobiliários", "Criptomoedas", "Exterior", "Outros"])
        f_valor = st.number_input("Valor Aplicado (R$)", min_value=0.0, step=50.0, format="%.2f")
        
        enviar = st.form_submit_button("💾 Salvar na Carteira", use_container_width=True)
        
        if enviar:
            if f_ativo and f_valor > 0:
                novo_registro = pd.DataFrame({"Ativo": [f_ativo], "Categoria": [f_cat], "Valor (R$)": [f_valor]})
                df_atualizado = pd.concat([df_dados, novo_registro], ignore_index=True)
                # Salva permanentemente no arquivo CSV
                df_atualizado.to_csv(ARQUIVO_DADOS, index=False)
                st.success(f"Aporte em **{f_ativo}** registrado e salvo com sucesso!")
                st.rerun()
            else:
                st.warning("Preencha o nome do ativo e informe um valor maior que zero.")

with aba_gerenciar:
    st.subheader("Gerenciar Ativos da Aposentadoria")
    if not df_dados.empty:
        st.dataframe(df_dados, hide_index=Test if False else True, use_container_width=True) # type: ignore
        
        st.markdown("---")
        st.markdown("### 🗑️ Remover um Ativo Incorreto")
        indice_para_remover = st.number_input("Digite o número da linha do ativo que deseja apagar (começa em 0):", min_value=0, max_value=max(len(df_dados)-1, 0), step=1)
        
        if st.button("Excluir Ativo Selecionado", type="primary"):
            df_atualizado = df_dados.drop(indice_para_remover).reset_index(drop=True)
            df_atualizado.to_csv(ARQUIVO_DADOS, index=False)
            st.success("Ativo removido e alteração salva!")
            st.rerun()
    else:
        st.info("Nenhum ativo cadastrado.")