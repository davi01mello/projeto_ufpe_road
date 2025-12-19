 CIn Road: Rumo ao Diploma

> **Projeto da disciplina de Introdução à Programação (2025.2)**  
> **Instituição:** Centro de Informática (CIn) - UFPE

---

## 👥 Equipe de Desenvolvimento

| Nome | Login | Email |
| :--- | :---: | :--- |
| **Davi de Souza Mello** | `dsm5` | dsm5@cin.ufpe.br |
| **Davi Rosendo Carvalho** | `drc4` | drc4@cin.ufpe.br |
| **Gabriel Godoy Carvalho de Menezes** | `ggcm` | ggcm@cin.ufpe.br |
| **João Felipe Costa Neves** | `jfcn4` | jfcn4@cin.ufpe.br |
| **João Pedro Medeiros** | `jpmmm` | jpmmm@cin.ufpe.br |
| **Vitor Costa Nunes** | `vnsfc` | vnsfc@cin.ufpe.br |

---

## 📝 Sobre o Projeto

**CIn Road** é um jogo de ação e estratégia 2D desenvolvido em Python com a biblioteca **PyGame**. Inspirado no clássico *Crossy Road*, o objetivo é guiar um estudante do CIn em uma jornada desafiadora até o diploma.

O jogador deve avançar por um mapa gerado proceduralmente, desviando de **ônibus circulares**, **carros** e **obras**, enquanto gerencia seus recursos coletando:

- 🎫 **Fragmentos de crachá:** Essenciais para a pontuação e aprovação  
- ⚡ **Energéticos:** Concedem efeito de câmera lenta (*bullet time*)  
- 🛡️ **Escudos:** Proteção contra dano  

O sistema foi desenvolvido rigorosamente seguindo o paradigma de **Programação Orientada a Objetos**, garantindo código modular, reutilizável e extensível.

---

## 🛠️ Divisão do Trabalho

A equipe foi organizada em frentes de atuação para otimizar o desenvolvimento:

- 🎨 **Áudio e Imagens:** Davi Rosendo  
- ⚙️ **Back-end:** João Felipe e João Pedro  
- 🖥️ **Front-end:** Vitor Nunes e Gabriel Godoy  
- 🤝 **Suporte Geral:** Davi Mello  

---

## 📂 Arquitetura do Projeto

O projeto utiliza **modularização** para separar responsabilidades. A estrutura final de arquivos é:

```text
projeto/
│
├── main.py                  # Game Loop: estados (Menu, Jogo, GameOver), eventos e renderização
├── src/
│   ├── config.py            # Constantes globais (tamanho da tela, cores, FPS)
│   └── entities/
│       ├── entity_base.py   # Classe base Entity (herda de pygame.sprite.Sprite)
│       ├── player.py        # Jogador: movimentação, sprites e vidas
│       ├── obstacles.py     # Obstáculos: carros e objetos estáticos
│       └── collectibles.py  # Itens: crachá, energético e escudo
└── assets/                  # Imagens, sons e vídeos
🧩 Conceitos de Programação Orientada a Objetos
🔹 Herança
Criamos a classe base Entity, que herda de pygame.sprite.Sprite.
As classes Player, Obstacle e Collectible herdam de Entity, reutilizando atributos como imagem e posicionamento (rect).

🔹 Polimorfismo
As classes filhas implementam comportamentos distintos para métodos comuns.

Exemplo:

Player.update() responde ao teclado

Obstacle.update() executa movimento automático

Collectible.update() verifica colisões

🔹 Encapsulamento
A classe Game centraliza e protege o estado do jogo.
Variáveis como score, lives e map_layout são gerenciadas internamente, evitando acessos indevidos.

🚧 Desafios, Erros e Lições Aprendidas
❌ Maior erro cometido
Problema: gerenciamento incorreto de caminhos de arquivos (assets), causando falhas em diferentes sistemas.

Solução:

Uso de os.path.join

Tratamento com try/except

Geração de placeholders gráficos quando um asset não é encontrado

⚠️ Maior desafio enfrentado
Problema: conflito entre movimentação em grade (jogador) e pixel a pixel (obstáculos).

Solução:

Separação entre posição lógica (grid_x, grid_y) e visual (rect.x, rect.y)

Ajuste das hitboxes para jogabilidade mais justa

✅ Lições aprendidas
Organização da equipe reduz conflitos no Git

Máquina de Estados (MENU, PLAYING, TUTORIAL) evita código confuso

📸 Galeria
Menu Principal

Gameplay

Cutscene / Game Over

⚠️ Certifique-se de que as imagens estão em assets/screenshots

🎮 Como Rodar o Jogo
1️⃣ Clone o repositório
bash
Copy code
git clone [LINK_DO_SEU_REPOSITORIO]
cd [NOME_DA_PASTA]
2️⃣ Instale as dependências
bash
Copy code
pip install pygame opencv-python
3️⃣ Execute o jogo
bash
Copy code
python main.py
🎮 Controles
Setas / WASD: Movimentação

Enter: Confirmar / Pular cutscene

ESC: Voltar / Sair

F11: Tela cheia

markdown
Copy code

---

### ✅ Resultado
- Renderiza **igual à primeira imagem**
- Totalmente compatível com **GitHub / GitLab**
- Organizado, legível e com **cara de projeto nota máxima**

Se quiser, posso:
- 🔍 revisar segundo a **rubrica da disciplina**
- 🧑‍🏫 adaptar para **formato exigido pelo CIn**
- ⭐ enxugar ou sofisticar (dependendo do professor)

Só dizer 👌






You said:
