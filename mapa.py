import os
import pandas as pd
import numpy as np
import rasterio

df = pd.read_csv("ndvi_processado.csv").sort_values("date")
ultimo_tif = df.iloc[-1]["arquivo"]

for raiz, _, arquivos in os.walk("nasaangola"):
    if ultimo_tif in arquivos:
        caminho = os.path.join(raiz, ultimo_tif)
        with rasterio.open(caminho) as src:
            matriz = src.read(1).astype(float)
            matriz = np.where(matriz < -3000, np.nan, matriz * 0.0001)
            # Salva a matriz leve para o Streamlit Cloud ler sem precisar do rasterio
            np.save("ultimo_mapa.npy", matriz)
            print("Sucesso! Ficheiro 'ultimo_mapa.npy' gerado.")
        break