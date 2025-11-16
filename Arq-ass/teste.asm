# ---- TESTE DE INSTRUÇÕES BÁSICAS ----

.text

main:
    addi a0, x0, 10      # a0 = 10
    addi a1, x0, 20      # a1 = 20
    add  a2, a0, a1      # a2 = 30

    sub  a3, a2, a0      # a3 = 20
    and  a4, a0, a1
    or   a5, a0, a1
    la   t3, var1
    lw   a6, 0(x0)       # carrega uma palavra da memória

    beq  a0, a1, label1  # branch se iguais
    addi a7, x0, 1       # só executa se branch não for tomado

label1:
    lui  a0, 0x12345     # carrega imediato grande

# ---- TESTE DE DADOS ----
.data

var1: .word 100
var2: .word 200
