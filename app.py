import os
import pandas as pd
import numpy as np
import rasterio
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Monitor Agro-Pastoral | Angola", page_icon="🛰️", layout="wide")

# --- CABEÇALHO EXECUTIVO ---
st.title("🛰️ Sala de Situação: Monitoramento de Seca e Pastagens")
st.markdown("**Sistema de Apoio à Decisão Municipal e Comunitária** | Dados de Satélite NASA (MODIS)")
st.divider()

@st.cache_data
def carregar_dados():
    df = pd.read_csv("ndvi_processado.csv")
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['mes'] = df['date'].dt.month
    df['ano'] = df['date'].dt.year
    return df

df = carregar_dados()

# --- CÁLCULOS DE INTELIGÊNCIA SAZONAL (SEM JARGÃO) ---
ultimo_registo = df.iloc[-1]
ultimo_valor = ultimo_registo['ndvi']
ultimo_mes = ultimo_registo['mes']
ultima_data_str = ultimo_registo['date'].strftime('%d/%m/%Y')

# Compara APENAS com o mesmo mês nos anos anteriores (evita falsos alarmes no cacimbo)
media_esperada_mes = df[df['mes'] == ultimo_mes]['ndvi'].mean()
saude_relativa_pct = (ultimo_valor / media_esperada_mes) * 100
desvio_pct = saude_relativa_pct - 100

# --- 1. SEMÁFORO DE DECISÃO IMEDIATA (O QUE O ADMINISTRADOR VÊ PRIMEIRO) ---
if saude_relativa_pct < 80:
    st.error(f"### 🚨 ESTADO DE ALERTA SEVERO (Atualizado em {ultima_data_str})\n"
             f"A cobertura vegetal da região está **{abs(desvio_pct):.0f}% abaixo do normal** para esta época do ano. "
             f"Alto risco de escassez de pasto e perda de gado nas próximas semanas.")
    nivel_alerta = "CRÍTICO"
elif saude_relativa_pct < 95:
    st.warning(f"### ⚠️ ESTADO DE VIGILÂNCIA (Atualizado em {ultima_data_str})\n"
               f"A vegetação apresenta sinais iniciais de estresse hídrico (**{abs(desvio_pct):.0f}% abaixo da média histórica** deste mês). "
               f"Recomenda-se monitoramento preventivo das reservas de água.")
    nivel_alerta = "ATENÇÃO"
else:
    st.success(f"### ✅ CONDIÇÕES ESTÁVEIS (Atualizado em {ultima_data_str})\n"
               f"O vigor das pastagens e lavouras está **dentro ou acima do esperado ({saude_relativa_pct:.0f}%)** para esta época do ano.")
    nivel_alerta = "NORMAL"

# --- 2. INDICADORES TRADUZIDOS PARA LINGUAGEM HUMANA ---
col1, col2, col3 = st.columns(3)
col1.metric(
    label="Capacidade Atual de Pastagem",
    value=f"{saude_relativa_pct:.0f}% do Normal",
    delta=f"{desvio_pct:+.1f}% vs. anos anteriores"
)
col2.metric(
    label="Tendência Recente (Últimos 30 dias)",
    value="Em Queda" if df['ndvi'].iloc[-1] < df['ndvi'].iloc[-3] else "Em Recuperação",
    delta="Baseado nas últimas passagens do satélite"
)
col3.metric(
    label="Cobertura Analisada",
    value="Sul de Angola",
    delta=f"Última leitura: {ultima_data_str}"
)

st.divider()

# --- 3. VISÃO ESPACIAL (ONDE ESTÁ O PROBLEMA?) + COMPARAÇÃO POR ANO ---
col_mapa, col_grafico = st.columns([1.1, 1])

with col_mapa:
    st.subheader("🗺️ Onde está o pasto agora? (Visão de Satélite)")
    st.caption("Verde = Vegetação saudável / Pasto disponível | Vermelho/Amarelo = Solo seco / Área crítica")
    
    # Carrega a última imagem TIF real para mostrar o mapa visual
    ultimo_tif = ultimo_registo['arquivo']
    caminho_tif = None
    for raiz, _, arquivos in os.walk("nasaangola"):
        if ultimo_tif in arquivos:
            caminho_tif = os.path.join(raiz, ultimo_tif)
            break
            
    if caminho_tif:
        with rasterio.open(caminho_tif) as src:
            matriz = src.read(1).astype(float)
            matriz = np.where(matriz < -3000, np.nan, matriz * 0.0001)
            
            fig_mapa = px.imshow(
                matriz,
                color_continuous_scale="RdYlGn", # Escala intuitiva: Vermelho -> Amarelo -> Verde
                zmin=0.1, zmax=0.6,
                labels={'color': 'Vigor Vegetal'}
            )
            fig_mapa.update_xaxes(showticklabels=False).update_yaxes(showticklabels=False)
            fig_mapa.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=380)
            st.plotly_chart(fig_mapa, use_container_width=True)

with col_grafico:
    st.subheader("📅 Como este ano se compara aos anteriores?")
    st.caption("Selecione um ano para comparar o comportamento da vegetação mês a mês")
    
    anos_disponiveis = sorted(df['ano'].unique(), reverse=True)
    ano_selecionado = st.selectbox("Comparar histórico do ano:", anos_disponiveis)
    
    df_ano = df[df['ano'] == ano_selecionado].copy()
    df_ano['Saúde (%)'] = (df_ano['ndvi'] / media_esperada_mes) * 100
    
    fig_barras = px.bar(
        df_ano,
        x='date',
        y='Saúde (%)',
        color='Saúde (%)',
        color_continuous_scale="RdYlGn",
        range_color=[60, 120],
        labels={'date': 'Data', 'Saúde (%)': 'Saúde da Vegetação (%)'}
    )
    fig_barras.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Média Esperada (100%)")
    fig_barras.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=330, showlegend=False)
    st.plotly_chart(fig_barras, use_container_width=True)

st.divider()

# --- 4. PLANO DE AÇÃO E COMUNICAÇÃO COM A COMUNIDADE (A ÚLTIMA MILHA) ---
st.subheader("📢 Ação Comunitária e Alerta Rápido")
col_acao1, col_acao2 = st.columns([1.5, 1])

with col_acao1:
    st.write("**Recomendação Operacional para a Administração:**")
    if nivel_alerta == "CRÍTICO":
        st.write("- **Mobilização:** Orientar criadores das zonas em vermelho no mapa a deslocarem o gado para os corredores verdes identificados a norte/nordeste.")
        st.write("- **Logística:** Priorizar envio de cisternas e suplementação alimentar para as comunas mais afetadas.")
    elif nivel_alerta == "ATENÇÃO":
        st.write("- **Prevenção:** Alertar cooperativas agrícolas para racionamento de água de irrigação e proteção de cacimbas.")
    else:
        st.write("- **Manutenção:** Manter acompanhamento quinzenal. Sem necessidade de intervenção de emergência.")

with col_acao2:
    st.write("**Disparo de Aviso Comunitário (SMS / Rádio Local):**")
    msg_sms = (f"ALERTA AGRO-PASTORAL ({ultima_data_str}): Pastagem a {saude_relativa_pct:.0f}% do normal. "
               f"Estado: {nivel_alerta}. Consulte o agente local para rotas de pasto.")
    st.text_area("Mensagem pronta para envio aos Sobas e Cooperativas:", value=msg_sms, height=90)
    if st.button("📲 Simular Envio de Alerta SMS para Líderes Locais"):
        st.toast("Alerta enviado com sucesso para 142 líderes comunitários e agentes rurais!", icon="✅")
        st.success("Boletim disparado para a rede comunitária!")