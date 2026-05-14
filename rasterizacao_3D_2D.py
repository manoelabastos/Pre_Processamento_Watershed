## Importar as bibliotecas necessárias
import laspy
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import distance_transform_edt
from PIL import Image
import os

## Fazer a leitura da nuvem de pontos
arquivo = laspy.read("D:\\IC\\nuvens de pontos\\plot_1_annotated.las")

## Extrair o valor máximo e mínimo da nuvem de pontos para coordenadas X, Y
x = arquivo.x
y = arquivo.y

max_x = np.max(x)
min_x = np.min(x)
max_y = np.max(y)
min_y = np.min(y)

print("Máximo X:", max_x)
print("Mínimo X:", min_x)
print("Máximo Y:", max_y)
print("Mínimo Y:", min_y)

## Definir a resolução da imagem (Tamanho do Pixel em metros)
tamanho_pixel = 0.25  # Ex: 25 centímetros

## Calcular o tamanho da imagem dividindo a amplitude pela resolução
tamanho_coluna = int((max_x - min_x) / tamanho_pixel) + 1
tamanho_linha = int((max_y - min_y) / tamanho_pixel) + 1

print("Tamanho da Coluna (Pixels):", tamanho_coluna)
print("Tamanho da Linha (Pixels):", tamanho_linha)

## Criar matriz float32 preenchida com o valor mínimo de Z (para não ficar buracos zerados)
imagem = np.full((tamanho_linha, tamanho_coluna), np.min(arquivo.z), dtype=np.float32)

## Preencher a matriz com a retenção de pico e inversão do eixo Y
for i in range(len(x)):
    # Descobrir a posição dividindo a coordenada real pelo tamanho do pixel
    coluna = int((x[i] - min_x) / tamanho_pixel)
    
    # Inverter o Y para o Norte ficar no topo da imagem!
    linha = int((max_y - y[i]) / tamanho_pixel) 
    
    intensidade = arquivo.z[i]
    
    # Regra de Retenção de Pico: Só substitui se o ponto novo for mais alto que o que já está lá
    if intensidade > imagem[linha, coluna]:
        imagem[linha, coluna] = intensidade

## Interpolação de valores vazios usando vizinhos mais próximos
# Identificar células com valor mínimo (vazias)
min_z = np.min(arquivo.z)
mascara_vazia = imagem == min_z

if np.any(mascara_vazia):
    print(f"Interpolando {np.sum(mascara_vazia)} células vazias...")
    
    # Criar coordenadas de grade
    y_grid, x_grid = np.mgrid[0:tamanho_linha, 0:tamanho_coluna]
    
    # Pontos conhecidos (onde há dados)
    pontos_conhecidos = np.column_stack([x_grid[~mascara_vazia], y_grid[~mascara_vazia]])
    valores_conhecidos = imagem[~mascara_vazia]
    
    # Pontos a interpolar
    pontos_interpolar = np.column_stack([x_grid[mascara_vazia], y_grid[mascara_vazia]])
    
    # Interpolação por vizinhos mais próximos
    valores_interpolados = griddata(pontos_conhecidos, valores_conhecidos, pontos_interpolar, method='nearest')
    imagem[mascara_vazia] = valores_interpolados
    
    print("Interpolação concluída!")

## Salvar a imagem resultante
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path_tif = os.path.join(output_dir, 'imagem_rasterizada.tif')
output_path_png = os.path.join(output_dir, 'imagem_rasterizada.png')

# Normalizar para 0-65535 (16-bit) e salvar como TIF
imagem_normalizada = ((imagem - np.min(imagem)) / (np.max(imagem) - np.min(imagem)) * 65535).astype(np.uint16)
img_tif = Image.fromarray(imagem_normalizada)
img_tif.save(output_path_tif)
print(f"Imagem TIF salva em: {output_path_tif}")

# Também salvar como PNG em escala de cinza
imagem_uint8 = ((imagem - np.min(imagem)) / (np.max(imagem) - np.min(imagem)) * 255).astype(np.uint8)
img_png = Image.fromarray(imagem_uint8)
img_png.save(output_path_png)
print(f"Imagem PNG salva em: {output_path_png}")

## Exibir a imagem resultante com melhor visualização
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Primeira imagem: escala de cinza
im1 = axes[0].imshow(imagem, cmap='gray')
axes[0].set_title('Rasterização - Escala de Cinza', fontsize=12, fontweight='bold')
axes[0].axis('off')
plt.colorbar(im1, ax=axes[0], label='Altura Z (m)')

# Segunda imagem: mapa de cores viridis para melhor visualização de topografia
im2 = axes[1].imshow(imagem, cmap='viridis')
axes[1].set_title('Rasterização - Mapa Topográfico', fontsize=12, fontweight='bold')
axes[1].axis('off')
plt.colorbar(im2, ax=axes[1], label='Altura Z (m)')

plt.suptitle('Imagem Rasterizada da Nuvem de Pontos (Pré-processamento Watershed)', 
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.show()


