print("--- INICIANDO O MAIN.PY ---")

try:
    from src.jogo import Game
    print("✅ Sucesso: Classe Game importada!")
except ImportError as e:
    print(f"❌ ERRO: Não consegui importar o jogo. Verifique a pasta 'src'. Erro: {e}")
    exit()

if __name__ == "__main__":
    print("🚀 Criando a janela do jogo...")
    try:
        jogo = Game()
        print("🎮 Janela criada! Entrando no loop...")
        jogo.rodar()
    except Exception as e:
        print(f"❌ ERRO FATAL ao rodar o jogo: {e}")

print("--- FIM DO SCRIPT ---")