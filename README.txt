# 🛰️ Sala de Situação Agro-Pastoral: Monitoramento Precoce de Seca em Angola

Link da App: [https://nasa-space-apps-calumbo.streamlit.app](https://nasa-space-apps-calumbo.streamlit.app)

**Projeto desenvolvido no âmbito do NASA Space Apps Challenge Calumbo 2026**  
Sistema de apoio à decisão municipal e comunitária para mitigação dos impactos da seca e gestão de pastagens no Sul de Angola utilizando dados de observação da Terra da NASA.
---

## 📋 1. Visão Geral e Problema

Milhões de famílias no sul de Angola (com destaque para a província do Cunene e áreas adjacentes) dependem da agricultura e da pastorícia. Atualmente, os impactos da seca são frequentemente identificados apenas quando já há perda severa de colheitas ou mortalidade de gado.

Esta solução traduz dados brutos de satélites da NASA numa **Sala de Situação intuitiva**, permitindo que administrações municipais, autoridades rurais e cooperativas identifiquem o estresse hídrico da vegetação com semanas de antecedência e orientem a deslocação preventiva do gado.

---

## ✨ 2. Funcionalidades Principais

* **Semáforo de Decisão Imediata:** Classificação automática do estado da região (*Normal*, *Vigilância* ou *Alerta Severo*) baseada no desvio percentual em relação ao esperado para o período.

* **Mapa Espacial de Pastagens:** Visualização georreferenciada da última passagem do satélite em escala intuitiva (*Vermelho* = solo seco/crítico; *Verde* = pasto disponível e saudável), indicando onde está o problema e para onde deslocar o gado.

* **Comparação Histórica Anual:** Análise evolutiva mês a mês que permite contrastar anos críticos de seca com anos regulares.

* **Canal de Última Milha (Alerta Comunitário):** Gerador automático de boletins curtos prontos para disparo via SMS/USSD ou rádio comunitária para líderes locais (Sobas) e associações de pastores sem acesso contínuo à internet.

---

## 🛰️ 3. Fonte de Dados e Metodologia Científica

* **Fonte Oficial:** AppEEARS (*Application for Extracting and Exploring Analysis Ready Samples*).
* **Missão / Sensor:** Satélites Terra e Aqua — Produto **MOD13Q1 v061** (*MODIS Vegetation Indices*).
* **Resolução Espacial e Temporal:** 250 metros por pixel, com composições a cada 16 dias (período analisado: 2020 – 2026).
* **Indicadores Extraídos:**
  * **NDVI (*Normalized Difference Vegetation Index*):** Mede o vigor fotossintético através da diferença entre a absorção de luz vermelha e a reflexão do infravermelho próximo (NIR), ideal para monitorar pastagens abertas e vegetação rasteira no sul de Angola.
  * **EVI (*Enhanced Vegetation Index*):** Índice complementar otimizado para corrigir distorções atmosféricas (poeira/fumaça) e o brilho do solo exposto.


---

## 🏗️ 4. Arquitetura do Projeto

O pipeline foi desenhado em duas etapas (processamento offline pesado + visualização leve em nuvem) para garantir alta performance no deploy:

```text
nasa-space-apps-calumbo/
├── nasaangola/             # (Local) Rasters GeoTIFF (.tif) extraídos via NASA AppEEARS
├── limpeza.py              # Pipeline ETL: lê os rasters, extrai datas julianas e gera o CSV
├── mapa.py                 # Pré-processamento espacial: converte o último GeoTIFF em matriz NumPy
├── ndvi_processado.csv     # Série temporal limpa e ordenada das médias regionais
├── ultimo_mapa.npy         # Matriz leve (250m) da última imagem de satélite para renderização rápida
├── app.py                  # Aplicação web interativa (Sala de Situação em Streamlit)
├── requirements.txt        # Dependências de produção para o Streamlit Community Cloud
└── README.md               # Documentação técnica do projeto

5. Instalação e execução 