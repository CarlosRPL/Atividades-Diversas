# Relatório das Tarefas de Álgebra Linear 

Este repositório reúne a implementação e explicação das quatro tarefas solicitadas na disciplina de Álgebra Linear, envolvendo subespaços, transformações lineares, mudança de base e operadores lineares. O objetivo é demonstrar tanto a teoria quanto a prática computacional aplicada em Python.

---

## **Tarefa 1 — Base e Dimensão do Subespaço W**
O programa recebe três valores reais **a**, **b**, **c** que definem o subespaço:

\[
W=\{(x,y,z)\in \mathbb{R}^3 \mid ax + by + cz = 0\}
\]

Esse é o conjunto de vetores ortogonais ao vetor normal **(a, b, c)**.

### O que o programa faz
- Monta a equação do plano (ou subespaço) a partir de **a, b, c**.  
- Encontra dois vetores linearmente independentes que satisfazem a equação.  
- Retorna:
  - **Uma base para W**  
  - **A dimensão de W**, que sempre será 2 se **(a,b,c) ≠ (0,0,0)**.  

---

## **Tarefa 2 — Base, Dimensão, Núcleo e Imagem de T**
Aqui, o programa recebe uma **transformação linear T: Rⁿ → Rᵐ**, representada por sua matriz.

### O que o programa calcula:
- **Base do núcleo (N(T))**  
- **Dimensão do núcleo (dim N(T))**  
- **Base da imagem (Im(T))**  
- **Dimensão da imagem (dim Im(T))**  

Isso é feito usando operações de Álgebra Linear como:
- redução à forma escalonada,
- cálculo do espaço nulo,
- cálculo do espaço gerado pelas colunas.

---

## **Tarefa 3 — Matriz da Transformação de β para γ**
Nesta tarefa, o programa recebe:

- **N:** dimensão do domínio  
- **M:** dimensão do contradomínio  
- **β:** base do domínio  
- **γ:** base do contradomínio  

E a transformação linear **T**, aplicada sobre os vetores da base β.

### Objetivo:
Construir a matriz da transformação:

\[
[T]_{\beta}^{\gamma}
\]

### Como o programa funciona:
1. Aplica T a cada vetor de β.  
2. Expressa cada resultado na base γ.  
3. Forma a matriz coluna por coluna.  

---

## **Tarefa 4 — Operador Linear: Autovalores, Autovetores e Autoespaços**
O programa recebe um **operador linear**, representado pela sua matriz em alguma base.

### Saída produzida:
- **Matriz do operador**  
- **Autovalores**  
- **Autovetores correspondentes**  
- **Autoespaços** descritos como:
  \[
  E_{\lambda} = \{ v \mid Av = \lambda v \}
  \]
- Tudo calculado automaticamente usando métodos numéricos.

Essa tarefa permite visualizar completamente o comportamento do operador linear no espaço vetorial.

---

## Conclusão
O conjunto de tarefas cobre os principais tópicos de Álgebra Linear computacional:

- Subespaços definidos por equações
- Transformações lineares
- Mudanças de base
- Autovalores, autovetores e decomposição espectral

---
