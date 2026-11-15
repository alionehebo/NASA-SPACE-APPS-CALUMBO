import os
import re
import rasterio
import numpy as np
import pandas as pd

pasta_tif = "nasaangola"
dados_extraidos = []

print("A procurar e processar os ficheiros TIF...")

for raiz, _, arquivos in os.walk(pasta_tif):
    for arquivo in arquivos:
        if arquivo.endswith(".tif") and "NDVI" in arquivo:
            caminho_completo = os.path.join(raiz, arquivo)
            
            # Procura por 'doy2020001', 'd2020001' ou qualquer sequência de 7 dígitos (Ano + Dia Juliano)
            match = re.search(r'(?:doy|d)?(20\d{5})', arquivo)
            if match:
                data_str = match.group(1)
                data_real = pd.to_datetime(data_str, format='%Y%j')
            else:
                print(f"Aviso: Data não reconhecida no nome do ficheiro -> {arquivo}")
                continue

            with rasterio.open(caminho_completo) as src:
                banda = src.read(1)
                banda = np.where(banda < -3000, np.nan, banda)
                media_ndvi = np.nanmean(banda)
                
                if not np.isnan(media_ndvi):
                    media_ndvi = media_ndvi * 0.0001

            dados_extraidos.append({
                'date': data_real,
                'arquivo': arquivo,
                'ndvi': media_ndvi
            })

if not dados_extraidos:
    print("ERRO: Nenhum ficheiro NDVI correspondente foi encontrado na pasta 'nasaangola'.")
else:
    df = pd.DataFrame(dados_extraidos)
    df = df.dropna(subset=['ndvi']).sort_values('date')
    df.to_csv("ndvi_processado.csv", index=False)
    print(f"Sucesso! {len(df)} registos guardados em 'ndvi_processado.csv'.")