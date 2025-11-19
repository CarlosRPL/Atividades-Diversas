def base_W(a, b, c):
    # Caso especial: a=b=c=0
    if a == 0 and b == 0 and c == 0:
        return [(1,0,0), (0,1,0), (0,0,1)], 3

    # Caso geral: o espaço é um plano (dimensão 2)

    # Encontrar dois vetores ortogonais (perpendiculares) a (a,b,c)
    # Primeiro vetor:
    if a != 0 or b != 0:
        v1 = (-b, a, 0)
    else:
        # a=b=0 e c != 0 → vetor normal é (0,0,c)
        v1 = (1, 0, 0)

    # Segundo vetor é o produto vetorial entre normal e v1
    # (a,b,c) x v1
    vx = b * v1[2] - c * v1[1]
    vy = c * v1[0] - a * v1[2]
    vz = a * v1[1] - b * v1[0]
    v2 = (vx, vy, vz)

    return [v1, v2], 2


def main():
    print("=== Subespaço W: ax + by + cz = 0 ===")
    a = float(input("a = "))
    b = float(input("b = "))
    c = float(input("c = "))

    base, dim = base_W(a, b, c)

    print("\nBase de W:")
    for v in base:
        print(v)

    print("\nDimensão de W:", dim)


main()
