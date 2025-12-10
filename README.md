# 🐊 UFPE Road: O Desafio do Campus

> Projeto da disciplina de Introdução à Programação (2025.2) - CIn/UFPE.

## 👥 Equipe de Desenvolvimento
| Nome | Login | Email |
|------|-------|-------|
| Davi de Souza Mello | `dsm5` | dsm5@cin.ufpe.br |
| Davi Rosendo Carvalho | `drc4` | drc4@cin.ufpe.br |
| Gabriel Godoy Carvalho de Menezes | `ggcm` | ggcm@cin.ufpe.br |
| João Felipe Costa Neves | `jfcn4` | jfcn4@cin.ufpe.br |
| João Pedro Medeiros | `jpmmm` | jpmmm@cin.ufpe.br |
| Vitor Costa Nunes | `vnsfc` | vnsfc@cin.ufpe.br |

---

## 📝 Sobre o Projeto
**UFPE Road** é um jogo de arcade em estilo *Endless Runner* (baseado em *Crossy Road*), desenvolvido inteiramente em Python utilizando a biblioteca **PyGame** e conceitos de **Orientação a Objetos**.

O jogador controla um aluno que deve atravessar o perigoso campus da UFPE, desviando de ônibus "Circular", carros e obras intermináveis, enquanto coleta fragmentos de crachá e lanches para sobreviver.

---

## 🎮 Como Rodar o Jogo
[cite_start]Siga os passos abaixo para executar o projeto em sua máquina:

### Pré-requisitos
* Python 3.x instalado.
* Gerenciador de pacotes `pip`.

### Instalação
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/projeto_ufpe_road.git](https://github.com/SEU_USUARIO/projeto_ufpe_road.git)
    cd projeto_ufpe_road
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    # Ou manualmente: pip install pygame
    ```

3.  **Execute o jogo:**
    ```bash
    python main.py
    ```

### Controles
* **Setas Direcionais:** Movem o personagem (Cima, Baixo, Esquerda, Direita).
* **ESC:** Sair do jogo.

---

## [cite_start]📂 Arquitetura do Projeto [cite: 50]
*Esta seção descreve como o código foi organizado baseando-se em Orientação a Objetos.*

O projeto segue uma estrutura modular:
* `src/entidades.py`: Contém a classe mãe `Entidade` e as classes filhas (`Aluno`, `Obstaculo`, `Coletavel`), aplicando **Herança** e **Polimorfismo**.
* `src/jogo.py`: Gerencia o loop principal, eventos e atualização de tela (Classe `Game`).
* `src/config.py`: Centraliza constantes (cores, dimensões) para fácil manutenção.
* `main.py`: Ponto de entrada da aplicação.

*(Preencher mais detalhes aqui conforme o desenvolvimento avançar)*

---

## [cite_start]🛠️ Ferramentas e Bibliotecas Utilizadas [cite: 51]
* **Python:** Linguagem base do projeto.
* **PyGame:** Escolhido por ser uma biblioteca robusta para criação de jogos 2D, facilitando o gerenciamento de sprites, colisiones e loops de eventos.
* **Git/GitHub:** Para versionamento e trabalho colaborativo em equipe.

---

## [cite_start]🧩 Conceitos de POO Utilizados [cite: 53]
* **Classes e Objetos:** Utilizados para representar todos os elementos do jogo (Jogador, Inimigos, Itens).
* **Herança:** A classe `Aluno` herda de `Entidade` (Sprite), reaproveitando código de posição e renderização.
* **Polimorfismo:** (Descrever aqui como diferentes obstáculos agem de forma diferente usando os mesmos métodos).
* **Encapsulamento:** (Descrever uso de métodos para alterar atributos internos como `vida` ou `pontuacao`).

---

## [cite_start]🚧 Desafios e Lições Aprendidas [cite: 54]

### [cite_start]1. Maior Erro Cometido [cite: 55]
*(Espaço reservado para descrever um erro técnico ou de organização, ex: conflito de merge no Git ou erro na lógica de colisão)*

### [cite_start]2. Maior Desafio Enfrentado [cite: 56]
*(Espaço reservado para descrever a parte mais difícil, ex: implementar a movimentação em grid ou gerenciar a velocidade dos obstáculos)*

### [cite_start]3. Lições Aprendidas [cite: 57]
*(Espaço reservado para o que o grupo aprendeu, ex: importância da modularização, pair programming, funcionamento do Pygame)*

---

## [cite_start]📸 Galeria do Projeto [cite: 51]
*(Adicionar capturas de tela do jogo funcionando aqui)*
