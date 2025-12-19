# 🎓 CIn Road: Rumo ao Diploma

> **Projeto da disciplina de Introdução à Programação (2025.2)**
> **Instituição:** Centro de Informática (CIn) - UFPE

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
**CIn Road** é um jogo de ação e estratégia 2D desenvolvido em Python com a biblioteca **PyGame**. Inspirado no clássico *Crossy Road*, o objetivo é guiar um estudante do CIn em uma jornada desafiadora até o diploma.

O jogador deve avançar por um mapa gerado proceduralmente, desviando de **ônibus circulares**, **carros** e **obras**, enquanto gerencia seus recursos coletando **fragmentos de crachá** (pontuação), **energéticos** (efeito de câmera lenta) e **escudos** (proteção contra dano).

O sistema foi construído rigorosamente sobre o paradigma de **Orientação a Objetos**, garantindo código modular e extensível.

---

## 📂 Arquitetura do Projeto
O código foi organizado utilizando **Modularização** para separar responsabilidades e facilitar o trabalho em grupo. A estrutura de arquivos final é:

```text
projeto/
│
├── main.py                  # Classe Game: Gerencia o loop principal, estados (Start, Playing, GameOver) e eventos.
├── src/
│   ├── config.py            # Centraliza constantes (tamanho da tela, cores, FPS, distância da meta).
│   └── entities/
│       ├── entity_base.py   # Classe Mãe (Entity): Define imagem, rect e posição para todos os objetos.
│       ├── player.py        # Classe Player: Lógica de movimento em grade, animação de sprite e sistema de vidas.
│       ├── obstacles.py     # Classe Obstacle: Lógica de tráfego, direção e velocidade variável.
│       └── collectibles.py  # Classes Itens: BadgeFragment, EnergyDrink e Shield (Polimorfismo).
└── assets/                  # Imagens e Sons
```
---

## Capturas de tela




---

## Ferramentas Ultilizadas



---

## Divisão do Trabalho



--

## Desafios e Erros
Qual foi o maior erro cometido durante o projeto? Como vocês lidaram com ele?

Qual foi o maior desafio enfrentado durante o projeto? Como vocês lidaram com ele?

Quais as lições aprendidas durante o projeto?
