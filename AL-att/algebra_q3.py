def ler_vetor(dim):
    valores = input().strip().split()
    return [float(x) for x in valores]


def ler_base(nome, quantidade, dimensao):
    print(f"\nDigite a base {nome} ({quantidade} vetores de dimensão {dimensao}):")
    base = []
    for i in range(quantidade):
        print(f"Vetor {nome}{i+1}:")
        base.append(ler_vetor(dimensao))
    return base


# -------------------------
# Escalonamento "na mão" (como o do seu código anterior)
# -------------------------
def escalonar(M):
    M = [linha[:] for linha in M]
    linhas, colunas = len(M), len(M[0])
    pivo_linha = 0

    for j in range(colunas):
        if pivo_linha >= linhas:
            break

        i_max = max(range(pivo_linha, linhas), key=lambda i: abs(M[i][j]))
        M[pivo_linha], M[i_max] = M[i_max], M[pivo_linha]

        pivo = M[pivo_linha][j]
        if abs(pivo) < 1e-10:
            continue

        M[pivo_linha] = [x / pivo for x in M[pivo_linha]]

        for i in range(pivo_linha + 1, linhas):
            fator = M[i][j]
            for k in range(colunas):
                M[i][k] -= fator * M[pivo_linha][k]

        pivo_linha += 1

    return M


# Resolve Ax = b por eliminação
def resolver_sistema(A, b):
    M = [A[i] + [b[i]] for i in range(len(A))]
    M = escalonar(M)

    linhas, colunas = len(A), len(A[0])
    x = [0]*colunas

    for i in reversed(range(linhas)):
        linha = M[i]
        if abs(linha[i]) < 1e-10:
            continue

        soma = sum(linha[j]*x[j] for j in range(i+1, colunas))
        x[i] = (linha[-1] - soma) / linha[i]

    return x


# -------------------------
# Programa principal
# -------------------------
def main():
    print("=== Matriz da Transformação Linear [T]β→γ ===")

    n = int(input("Dimensão do domínio N: "))
    m = int(input("Dimensão do contradomínio M: "))

    # Ler bases
    beta = ler_base("β", n, n)
    gama = ler_base("γ", m, m)

    print("\nDigite T(bi) para cada vetor da base β:")

    Tb = []
    for i in range(n):
        print(f"T(b{i+1}):")
        Tb.append(ler_vetor(m))

    # Matriz da base gama (colunas = vetores de gama)
    A = []
    for linha in range(m):
        A.append([gama[col][linha] for col in range(m)])

    matriz_T = []

    for i in range(n):
        coeficientes = resolver_sistema(A, Tb[i])
        matriz_T.append(coeficientes)

    print("\n=== Matriz [T] β→γ ===")
    for col in matriz_T:
        print(col)


main()
