#!/usr/bin/env python3


import pygame
import json
import os
import requests
import tarfile
import shutil

# Inicialize o pygame
pygame.init()

# Defina a largura e a altura da tela (fullscreen)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

# Defina o título da janela
pygame.display.set_caption("JC GAMES CLÁSSICOS")

# URL do arquivo JSON no GitHub
json_url = "https://raw.githubusercontent.com/JeversonDiasSilva/JSON/main/wine-downloader-info.json"

# Baixar o arquivo JSON do GitHub
response = requests.get(json_url)

# Verificar se a requisição foi bem-sucedida
if response.status_code == 200:
    data = response.json()
else:
    print(f"Erro ao carregar o arquivo JSON: {response.status_code}")
    data = {}

# A lista de versões está dentro de 'wine-releases'
wine_versions = data.get("wine-releases", [])

# Função para criar os botões de versões
def create_buttons(wine_versions, start_index=0, per_page=13):  # Mudança aqui de 15 para 13
    buttons = []
    y_offset = 120  # Posição inicial no eixo Y (ajustado para não cobrir o título)
    for i in range(start_index, start_index + per_page):
        if i >= len(wine_versions): break
        version = wine_versions[i]
        version_name = version["version"]
        button = pygame.Rect(50, y_offset, screen.get_width() - 100, 40)  # Botão com largura ajustada para a tela
        buttons.append((button, version))
        y_offset += 60  # Aumenta a posição Y para o próximo botão
    return buttons

# Função para desenhar os botões na tela
def draw_buttons(buttons, scroll_offset):
    for button, version in buttons:
        button.y += scroll_offset  # Aplica o offset de rolagem
        # Desenhando o botão com borda e efeito de hover
        pygame.draw.rect(screen, (0, 128, 255), button, border_radius=10)  # Cor do botão com borda arredondada
        pygame.draw.rect(screen, (255, 255, 255), button, width=3, border_radius=10)  # Borda do botão (branco)
        
        # Efeito de hover (mudando a cor ao passar o mouse)
        if button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (0, 100, 200), button, border_radius=10)  # Cor do botão ao passar o mouse

        # Adicionando o texto no botão
        font = pygame.font.Font(None, 28)
        text = font.render(version["version"], True, (255, 255, 255))  # Cor do texto (branco)
        screen.blit(text, (button.x + 10, button.y + 10))  # Desenha o texto no botão

# Função para desenhar os botões de navegação
def draw_navigation_buttons():
    # Botão Voltar (verde neon)
    back_button = pygame.Rect(50, screen.get_height() - 120, screen.get_width() // 3 - 50, 50)
    pygame.draw.rect(screen, (57, 255, 20), back_button, border_radius=10)  # Verde neon
    pygame.draw.rect(screen, (255, 255, 255), back_button, width=3, border_radius=10)
    font = pygame.font.Font(None, 36)
    text = font.render("Voltar", True, (255, 255, 255))
    screen.blit(text, (back_button.x + (back_button.width - text.get_width()) // 2, back_button.y + (back_button.height - text.get_height()) // 2))

    # Botão Sair (verde neon)
    exit_button = pygame.Rect(screen.get_width() // 3 + 50, screen.get_height() - 120, screen.get_width() // 3 - 50, 50)
    pygame.draw.rect(screen, (255, 20, 20), exit_button, border_radius=10)  # Vermelho neon
    pygame.draw.rect(screen, (255, 255, 255), exit_button, width=3, border_radius=10)
    text = font.render("Sair", True, (255, 255, 255))
    screen.blit(text, (exit_button.x + (exit_button.width - text.get_width()) // 2, exit_button.y + (exit_button.height - text.get_height()) // 2))

    # Botão Próximo (verde claro)
    next_button = pygame.Rect(2 * (screen.get_width() // 3) + 50, screen.get_height() - 120, screen.get_width() // 3 - 50, 50)
    pygame.draw.rect(screen, (0, 200, 0), next_button, border_radius=10)  # Verde claro
    pygame.draw.rect(screen, (255, 255, 255), next_button, width=3, border_radius=10)
    text = font.render("Próximo", True, (255, 255, 255))
    screen.blit(text, (next_button.x + (next_button.width - text.get_width()) // 2, next_button.y + (next_button.height - text.get_height()) // 2))

    return back_button, exit_button, next_button

# Função para verificar se algum botão foi clicado
def check_button_click(buttons, pos, scroll_offset):
    for button, version in buttons:
        button.y += scroll_offset  # Aplica o offset de rolagem
        if button.collidepoint(pos):
            print(f"Botão clicado: {version['version']}")
            download_and_extract(version["download"], version["version"])

# Função para controlar os botões de navegação
def check_navigation_buttons(back_button, exit_button, next_button, pos):
    if back_button.collidepoint(pos):
        return "back"
    if exit_button.collidepoint(pos):
        return "exit"
    if next_button.collidepoint(pos):
        return "next"
    return None

# Função para download, extração e remoção do arquivo
def download_and_extract(download_url, version_name):
    # Caminhos
    download_path = f"/userdata/system/wine/{version_name}.tar.gz"
    tmp_extract_path = f"/userdata/system/wine/custom/.tmp"
    final_extract_path = f"/userdata/system/wine/custom/{version_name}"
    
    # Baixar o arquivo
    print(f"Baixando o arquivo: {download_url}")
    response = requests.get(download_url, stream=True)
    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

    # Extrair o arquivo para o diretório temporário .tmp
    if tarfile.is_tarfile(download_path):
        print("Extraindo o arquivo...")
        with tarfile.open(download_path, "r:gz") as tar:
            tar.extractall(path=tmp_extract_path)

    # Organizar os arquivos após a extração
    move_files(tmp_extract_path, final_extract_path, version_name)

    # Apagar o arquivo baixado
    print("Removendo o arquivo baixado...")
    os.remove(download_path)

# Função para mover a pasta "files" para o diretório de destino e renomeá-la para a versão
def move_files(tmp_extract_path, final_extract_path, version_name):
    # Remover o prefixo "Proton-" do nome da versão
    clean_version_name = version_name.replace("Proton-", "")  # Remove o prefixo "Proton-"
    
    # Caminho onde 'files' está localizado dentro da pasta temporária
    source_files_path = os.path.join(tmp_extract_path, clean_version_name, "files")

    # Verifica se a pasta "files" existe dentro da pasta extraída
    if os.path.exists(source_files_path):
        print(f"Encontrado 'files' em {source_files_path}, movendo arquivos para {final_extract_path}...")

        # Cria a pasta com o nome da versão em /userdata/system/wine/custom
        if not os.path.exists(final_extract_path):
            os.makedirs(final_extract_path)

        # Move os arquivos da pasta 'files' para o diretório final
        for item in os.listdir(source_files_path):
            source_item = os.path.join(source_files_path, item)
            destination_item = os.path.join(final_extract_path, item)

            # Se for uma pasta, move recursivamente
            if os.path.isdir(source_item):
                shutil.copytree(source_item, destination_item)
                print(f"Diretório {source_item} movido para {destination_item}")
            else:
                shutil.copy2(source_item, destination_item)  # Copia arquivos
                print(f"Arquivo {source_item} movido para {destination_item}")

        # Excluir a pasta temporária .tmp
        shutil.rmtree(tmp_extract_path)  # Remove a pasta temporária .tmp
        print(f"Pasta temporária .tmp removida.")
    else:
        print(f"A pasta 'files' não foi encontrada em {source_files_path}")

# Variáveis para controle de navegação
start_index = 0
per_page = 13  # Reduzido para 13 para sobrar mais espaço

# Criação dos botões de versões
buttons = create_buttons(wine_versions, start_index, per_page)

# Loop principal
running = True
while running:
    screen.fill((30, 30, 30))  # Fundo escuro (cinza escuro)

    # Desenhar o título
    font_title = pygame.font.Font(None, 70)  # Aumentei o tamanho da fonte
    title_text = font_title.render("JC GAMES CLÁSSICOS", True, (255, 255, 255))  # Cor do título (branco)
    screen.blit(title_text, (screen.get_width() // 2 - title_text.get_width() // 2, 20))  # Centraliza o título

    # Desenhar os botões de versões
    draw_buttons(buttons, 0)

    # Desenhar os botões de navegação
    back_button, exit_button, next_button = draw_navigation_buttons()

    # Verificar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Verifica se o botão esquerdo do mouse foi clicado
                check_button_click(buttons, event.pos, 0)

                # Verificar clique nos botões de navegação e atualizar a tela
                action = check_navigation_buttons(back_button, exit_button, next_button, event.pos)
                if action == "back" and start_index > 0:
                    start_index -= per_page
                    buttons = create_buttons(wine_versions, start_index, per_page)  # Atualiza os botões de versões
                elif action == "next" and start_index + per_page < len(wine_versions):
                    start_index += per_page
                    buttons = create_buttons(wine_versions, start_index, per_page)  # Atualiza os botões de versões
                elif action == "exit":
                    running = False

    # Atualizar a tela
    pygame.display.flip()

# Finalizar o pygame
pygame.quit()
