# Assembler Risc-V 32I didático

  Esta atividade eu desenvolvi um assembler simples para o conjunto de instruções RISC-V.
O objetivo é criar um programa em Python capaz de ler um arquivo de
texto contendo código em assembly e convertê-lo para código de máquina,
gerando arquivos binários que representam as instruções e dados na memória.

  O montador reconhece diretivas como .text e .data, identifica labels, 
traduz instruções básicas para seus formatos binários (R, I, S, B, U e J) 
e lida com uma pseudo-instrução (la). O resultado final é um montador
funcional em duas passagens: a primeira constrói a tabela de símbolos
e calcula endereços; a segunda converte instruções e dados para os binários corretos.

  existem futuras adições pra essa atividade que é ajustar para lidar com dependencias e trocar
a ordem de instruções para evitar essas dependencias e lidar com possiveis pulos condicionais 
envolvendo predição de branch.
