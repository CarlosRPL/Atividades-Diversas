def ler_matriz(n):
    print(f"\nDigite a matriz do operador linear ({n}x{n}):")
    M = []
    for i in range(n):
        linha = input(f"Linha {i+1}: ").strip().split()
        M.append([float(x) for x in linha])
    return M


# -------------------------
# Funções auxiliares
# -------------------------
def determinante_2x2(M):
    return M[0][0]*M[1][1] - M[0][1]*M[1][0]


def determinante_3x3(M):
    return (M[0][0]*(M[1][1]*M[2][2] - M[1][2]*M[2][1])
         -  M[0][1]*(M[1][0]*M[2][2] - M[1][2]*M[2][0])
         +  M[0][2]*(M[1][0]*M[2][1] - M[1][1]*M[2][0]))


def subtrair_lambdaI(M, lamb):
    n = len(M)
    R = []
    for i in range(n):
        R.append([M[i][j] - (lamb if i == j else 0) for j in range(n)])
    return R


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


def achar_pivos(M):
    pivos = []
    for linha in M:
        for j, val in enumerate(linha):
            if abs(val) > 1e-10:
                pivos.append(j)
                break
    return pivos


def base_nucleo(M):
    esc = escalonar(M)
    pivos = achar_pivos(esc)

    colunas = len(esc[0])
    livres = list(set(range(colunas)) - set(pivos))

    base = []

    for livre in livres:
        v = [0] * colunas
        v[livre] = 1

        for i in range(len(pivos)-1, -1, -1):
            j = pivos[i]
            soma = sum(esc[i][k]*v[k] for k in range(j+1, colunas))
            v[j] = -soma / esc[i][j] if abs(esc[i][j]) > 1e-10 else 0

        base.append(v)

    return base


# -------------------------
# Polinômio característico
# -------------------------
def polinomio_caracteristico(M):
    n = len(M)

    if n == 2:
        a, b = M[0][0], M[0][1]
        c, d = M[1][0], M[1][1]
        # λ² − (a+d)λ + (ad − bc)
        A = 1
        B = -(a + d)
        C = (a * d - b * c)
        return (A, B, C)

    elif n == 3:
        # coeficientes do polinômio λ³ − tr(A)λ² + ...
        tr = M[0][0] + M[1][1] + M[2][2]

        # precisamos de determinante
        detA = determinante_3x3(M)

        # soma dos menores principais 2×2
        m1 = M[1][1]*M[2][2] - M[1][2]*M[2][1]
        m2 = M[0][0]*M[2][2] - M[0][2]*M[2][0]
        m3 = M[0][0]*M[1][1] - M[0][1]*M[1][0]
        soma_menores = m1 + m2 + m3

        # λ³ − tr λ² + soma_menores λ − detA
        return (1, -tr, soma_menores, -detA)

    else:
        print("Apenas matrizes 2×2 e 3×3 são suportadas.")
        return None


# Resolve polinômio de 2º grau
def resolver_quadratica(a, b, c):
    delta = b*b - 4*a*c
    if delta < 0:
        return []
    elif abs(delta) < 1e-10:
        return [-b / (2*a)]
    else:
        d = delta**0.5
        return [(-b+d)/(2*a), (-b-d)/(2*a)]


# -------------------------
# Programa principal
# -------------------------
def main():
    print("=== Autovalores, Autovetores e Autoespaços ===")

    n = int(input("Dimensão do operador (2 ou 3): "))

    A = ler_matriz(n)

    print("\n=== Matriz do operador ===")
    for row in A:
        print(row)

    # Polinômio característico
    coef = polinomio_caracteristico(A)
    if coef is None:
        return

    print("\nPolinômio característico:")
    print("Coeficientes:", coef)

    # Autovalores
    if n == 2:
        lambdas = resolver_quadratica(*coef)
    else:
        print("\nPara 3×3, o cálculo exato das raízes não é feito (método cúbico),")
        print("mas você pode testar valores que acha serem autovalores.")
        teste = input("Digite possíveis autovalores separados por espaço: ").strip().split()
        lambdas = [float(x) for x in teste]

    print("\nAutovalores encontrados/testados:", lambdas)

    # Para cada autovalor, calculamos autoespaço e autovetores
    for lamb in lambdas:
        print(f"\n=== λ = {lamb} ===")

        M = subtrair_lambdaI(A, lamb)

        print("Matriz (A - λI):")
        for r in M:
            print(r)

        base = base_nucleo(M)

        print("Autovetores (base do núcleo):")
        for v in base:
            print(v)

        print("Dimensão do autoespaço:", len(base))

    print("\nConcluído.")


main()
