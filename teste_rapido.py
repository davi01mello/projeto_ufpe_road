import pygame
import sys


try:
    pygame.init()
    print("✅ PyGame iniciou com sucesso!")
except Exception as e:
    print(f"❌ Erro ao iniciar PyGame: {e}")


try:
    tela = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Teste de Janela")
    print("✅ Janela configurada!")
except Exception as e:
    print(f"❌ Erro ao criar janela: {e}")
print("⏳ Tentando manter a janela aberta... (Pressione X para fechar)")
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    tela.fill((0, 0, 255)) # Pinta de Azul
    pygame.display.flip()

pygame.quit()
print("👋 Encerrando teste.")