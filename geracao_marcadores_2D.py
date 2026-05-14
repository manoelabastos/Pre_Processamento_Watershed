## Importando bibliotecas
import numpy as np
import laspy
import matplotlib.pyplot as plt
import PIL.Image as Image

## Fazer a leitura da nuvem de pontos
arquivo = laspy.read("D:\\IC\\nuvens de pontos\\plot_1_annotated.las")

## Extrair o valor máximo e mínimo da nuvem de pontos para coordenadas X, Y
x = arquivo.x
y = arquivo.y

x_min, x_max = np.min(x), np.max(x)
y_min, y_max = np.min(y), np.max(y)

## Definir a resolução da imagem (Tamanho do Pixel em metros)
tamanho_pixel = 0.25  # Ex: 25 centímetros

## Calcular o tamanho da imagem dividindo a amplitude pela resolução
tamanho_coluna = int((x_max - x_min) / tamanho_pixel) + 1
tamanho_linha = int((y_max - y_min) / tamanho_pixel) + 1

## Criar uma matriz de zeros para armazenar os valores dos pixels
imagem = np.zeros((tamanho_linha, tamanho_coluna), dtype=np.uint8)

## Fazer a leitura do arquivo .txt com coordenadas UTM dos centróides
with open("D:\\IC\\Pre_Processamento_Watershed\\posicao_marcadores.txt", "r") as f:
    linhas = f.readlines()
    for linha in linhas:
        coordenadas = linha.strip().split()
        if len(coordenadas) == 2:
            x_centroid = float(coordenadas[0])
            y_centroid = float(coordenadas[1])

            # Calcular as coordenadas do pixel correspondente
            coluna = int((x_centroid - x_min) / tamanho_pixel)
            linha = int((y_centroid - y_min) / tamanho_pixel)

            # Verificar se as coordenadas do pixel estão dentro dos limites da imagem
            if 0 <= linha < tamanho_linha and 0 <= coluna < tamanho_coluna:
                imagem[linha, coluna] = 255  # Marcar o pixel como branco
                
## Exibir a imagem resultante
plt.imshow(imagem, cmap="gray") 
plt.title("Imagem dos Centróides")
plt.axis("off")
plt.show()

## Salvar a matriz de marcadores
caminho_salvar = r"D:\IC\Pre_Processamento_Watershed\matriz_marcadores.npy"
np.save(caminho_salvar, imagem)
print(f"Matriz de marcadores salva com sucesso em: {caminho_salvar}")

## Salvar como TIFF de 32-bits para visualização
caminho_tif = r"D:\IC\Pre_Processamento_Watershed\marcadores_visualizacao.tif"
img_tif = Image.fromarray(imagem.astype(np.int32))
img_tif.save(caminho_tif)
print(f"Marcadores salvos como TIF em: {caminho_tif}")

