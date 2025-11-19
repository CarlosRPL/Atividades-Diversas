def ler_matriz(p, n):
    print(f"\nDigite a matriz da transformação ({p}x{n}):")
    matriz = []
    for i in range(p):
        linha = input(f"Linha {i+1}: ").strip().split()
        matriz.append([float(x) for x in linha])
    return matriz


def escalonar(M):
    M = [linha[:] for linha in M]
    linhas, colunas = len(M), len(M[0])
    pivo_linha = 0

    for j in range(colunas):
        if pivo_linha >= linhas:
            break

        # Encontrar melhor pivô
        i_max = max(range(pivo_linha, linhas), key=lambda i: abs(M[i][j]))
        M[pivo_linha], M[i_max] = M[i_max], M[pivo_linha]

        pivo = M[pivo_linha][j]
        if abs(pivo) < 1e-10:
            continue

        # Normalizar
        M[pivo_linha] = [x / pivo for x in M[pivo_linha]]

        # Eliminar abaixo
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
            if val != 0 :
                pivos.append(j)
                break
    return pivos


def calcular_base_nucleo(esc, pivos):
    colunas = len(esc[0])
    todas = set(range(colunas))
    livres = list(todas - set(pivos))

    base = []

    for livre in livres:
        vetor = [0] * colunas
        vetor[livre] = 1  

        for i in range(len(pivos) - 1, -1, -1):
            j = pivos[i]
            soma = 0
            for k in range(j + 1, colunas):
                soma += esc[i][k] * vetor[k]

            vetor[j] = -soma / esc[i][j]

        base.append(vetor)

    return base, livres


def main():
    print("=== Transformação Linear ===")

    n = int(input("Dimensão do domínio (ex: 3 para R^3): "))
    p = int(input("Dimensão do contradomínio (ex: 2 para R^2): "))

    M = ler_matriz(p, n)

    esc = escalonar(M)
    pivos = achar_pivos(esc)

    print("\nMatriz escalonada:")
    for linha in esc:
        print(linha)

    print("\nPivôs nas colunas:", pivos)

    # Base e dimensão do núcleo
    base_nucleo, livres = calcular_base_nucleo(esc, pivos)

    print("\nVariáveis livres:", livres)
    print("\nBase do núcleo:")
    for v in base_nucleo:
        print(v)

    dim_nucleo = len(base_nucleo)
    print("\nDimensão do núcleo:", dim_nucleo)

    # AGORA SOMENTE PELO TEOREMA:
    # dim(imagem) = dim(domínio) - dim(núcleo)
    dim_imagem = n - dim_nucleo
    print("Dimensão da imagem (TEOREMA):", dim_imagem)

    print("\nVerificação do Teorema:")
    print(f"{n} = {dim_nucleo} + {dim_imagem}")


main()
