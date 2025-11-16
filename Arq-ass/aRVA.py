"""
Montador simples de duas passagens para RISC-V RV32I (com apenas LA como pseudo-instrução).
Entrada: arquivo de texto com assembly.
Saída: arquivo de texto com linhas de 32 bits (binário) e opcionalmente arquivo .raw com little-endian.
Andamento:

Limitações:
 - Suporta um conjunto razoável de instruções RV32I (lista no código).
 - Não implementa extensões (M, F, atomic, etc).
 - Algumas diretivas/encodings simplificados. Ajuste endereços base conforme necessário.
"""
import re
import sys
import struct
from collections import OrderedDict

# Endereços base (ajustáveis)
TEXT_BASE = 0x00400000
DATA_BASE = 0x10010000

#|| funções auxiliares||
def to_signed(val, bits):
    mask = (1 << bits) - 1
    if val & (1 << (bits - 1)):
        return val - (1 << bits)
    return val & mask

def int_to_bin(value, bits):
    return format(value & ((1 << bits) - 1), '0{}b'.format(bits))

def parse_reg(reg: str) -> int:
    r = reg.lower().strip()

    # Caso formato xN
    if r.startswith("x") and r[1:].isdigit():
        num = int(r[1:])
        return num if 0 <= num <= 31 else -1

    # Nomes especiais
    special = {
        "ra":   1,
        "sp":   2,
        "gp":   3,
        "tp":   4,
        "fp":   8,   # alias de s0
    }
    if r in special:
        return special[r]

    # Temporários t0–t6
    if r.startswith("t") and len(r) == 2 and r[1].isdigit():
        n = int(r[1])
        if 0 <= n <= 6:
            mapping = [5, 6, 7, 28, 29, 30, 31]
            return mapping[n]
        return -1

    # Saved registers s0–s11
    if r.startswith("s") and len(r) >= 2 and r[1].isdigit():
        n = int(r[1])
        if n == 0: return 8
        if n == 1: return 9
        if 2 <= n <= 11:
            return 18 + (n - 2)
        return -1

    # Argument registers a0–a7
    if r.startswith("a") and len(r) == 2 and r[1].isdigit():
        n = int(r[1])
        if 0 <= n <= 7:
            return 10 + n
        return -1

    return -1

#||  Formatos de instrução  ||

def formato_r(funct7,rs2,rs1,funct3,rd,opcode):
    return  (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def formato_i(imm,rs1,funct3,rd,opcode):
    imm&= 0xfff
    return  (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def formato_s(imm,rs2,rs1,funct3,opcode):
    imm &= 0xfff
    imm11_5 = (imm >> 5) & 0x7f
    imm4_0 = imm & 0x1f
    return (imm11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4_0 << 7) | opcode

def formato_b(imm, rs2, rs1, funct3, opcode):
    imm &= 0x1fff
    imm12 = (imm >> 12) & 0x1
    imm10_5 = (imm >> 5) & 0x3f
    imm4_1 = (imm >> 1) & 0xf
    imm11 = (imm >> 11) & 0x1
    return (imm12 << 31) | (imm11 << 7) | (imm10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4_1 << 8) | opcode

def formato_u(imm, rd, opcode):
    return (imm & 0xfffff000) | (rd << 7) | opcode

def formato_j(imm, rd, opcode):
    imm &= 0x1fffff
    imm20 = (imm >> 20) & 0x1
    imm10_1 = (imm >> 1) & 0x3ff
    imm11 = (imm >> 11) & 0x1
    imm19_12 = (imm >> 12) & 0xff
    return (imm20 << 31) | (imm19_12 << 12) | (imm11 << 20) | (imm10_1 << 21) | (rd << 7) | opcode

# Instruções
# Formato R
def add_enc(args): # add rd, rs1, rs2
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x0, rd, 0x33)
def sub_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x20, rs2, rs1, 0x0, rd, 0x33)
def sll_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x1, rd, 0x33)
def srl_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x5, rd, 0x33)
def sra_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x20, rs2, rs1, 0x5, rd, 0x33)
def and_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x7, rd, 0x33)
def or_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x6, rd, 0x33)
def xor_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x4, rd, 0x33)
def slt_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x2, rd, 0x33)
def sltu_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1]) 
    rs2 = parse_reg(args[2])
    return formato_r(0x00, rs2, rs1, 0x3, rd, 0x33)

#Formato I

def addi_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    imm = int(args[2], 0)
    return formato_i(imm, rs1, 0x0, rd, 0x13)

def andi_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    imm = int(args[2], 0)
    return formato_i(imm, rs1, 0x7, rd, 0x13)

def ori_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    imm = int(args[2], 0)
    return formato_i(imm, rs1, 0x6, rd, 0x13)

def xori_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    imm = int(args[2], 0)
    return formato_i(imm, rs1, 0x4, rd, 0x13)

def slti_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    imm = int(args[2], 0)
    return formato_i(imm, rs1, 0x2, rd, 0x13)

def sltiu_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    imm = int(args[2], 0)
    return formato_i(imm, rs1, 0x3, rd, 0x13)

def slli_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    sh = int(args[2], 0)
    return formato_i(sh, rs1, 0x1, rd, 0x13)

def srli_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    sh = int(args[2], 0)
    return formato_i(sh, rs1, 0x5, rd, 0x13)

def srai_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    sh = int(args[2], 0)
    return formato_i(sh | (0x20 << 5), rs1, 0x5, rd, 0x13)

#l-type
import re

def lw_enc(args):
    rd = parse_reg(args[0])
    m = re.match(r'(-?\d+)\((.+)\)', args[1].replace(' ', ''))
    imm = int(m.group(1), 0)
    rs1 = parse_reg(m.group(2))
    return formato_i(imm, rs1, 0x2, rd, 0x03)

def lb_enc(args):
    rd = parse_reg(args[0])
    m = re.match(r'(-?\d+)\((.+)\)', args[1].replace(' ', ''))
    imm = int(m.group(1), 0)
    rs1 = parse_reg(m.group(2))
    return formato_i(imm, rs1, 0x0, rd, 0x03)

def lh_enc(args):
    rd = parse_reg(args[0])
    m = re.match(r'(-?\d+)\((.+)\)', args[1].replace(' ', ''))
    imm = int(m.group(1), 0)
    rs1 = parse_reg(m.group(2))
    return formato_i(imm, rs1, 0x1, rd, 0x03)

def jalr_enc(args):
    rd = parse_reg(args[0])
    rs1 = parse_reg(args[1])
    imm = int(args[2], 0)
    return formato_i(imm, rs1, 0x0, rd, 0x67)

#formato S

def sw_enc(args):
    rs2 = parse_reg(args[0])
    m = re.match(r'(-?\d+)\((.+)\)', args[1].replace(' ', ''))
    imm = int(m.group(1), 0)
    rs1 = parse_reg(m.group(2))
    return formato_s(imm, rs2, rs1, 0x2, 0x23)

def sb_enc(args):
    rs2 = parse_reg(args[0])
    #isso é para capturar o deslocamento do deslocamento
    m = re.match(r'(-?\d+)\((.+)\)', args[1].replace(' ', ''))
    imm = int(m.group(1), 0)
    rs1 = parse_reg(m.group(2))
    return formato_s(imm, rs2, rs1, 0x0, 0x23)

def sh_enc(args):
    rs2 = parse_reg(args[0])
    m = re.match(r'(-?\d+)\((.+)\)', args[1].replace(' ', ''))
    imm = int(m.group(1), 0)
    rs1 = parse_reg(m.group(2))
    return formato_s(imm, rs2, rs1, 0x1, 0x23)

# Formato B

def beq_enc(args, curr_addr, symtab):
    rs1 = parse_reg(args[0])
    rs2 = parse_reg(args[1])
    lbl = args[2]
    offset = symtab[lbl] - curr_addr
    return formato_b(offset, rs2, rs1, 0x0, 0x63)

def bne_enc(args, curr_addr, symtab):
    rs1 = parse_reg(args[0])
    rs2 = parse_reg(args[1])
    lbl = args[2]
    offset = symtab[lbl] - curr_addr
    return formato_b(offset, rs2, rs1, 0x1, 0x63)

def blt_enc(args, curr_addr, symtab):
    rs1 = parse_reg(args[0])
    rs2 = parse_reg(args[1])
    lbl = args[2]
    offset = symtab[lbl] - curr_addr
    return formato_b(offset, rs2, rs1, 0x4, 0x63)

def bge_enc(args, curr_addr, symtab):
    rs1 = parse_reg(args[0])
    rs2 = parse_reg(args[1])
    lbl = args[2]
    offset = symtab[lbl] - curr_addr
    return formato_b(offset, rs2, rs1, 0x5, 0x63)

#Formato U

def lui_enc(args):
    rd = parse_reg(args[0])
    imm = int(args[1], 0)
    return formato_u(imm, rd, 0x37)

def auipc_enc(args):
    rd = parse_reg(args[0])
    imm = int(args[1], 0)
    return formato_u(imm, rd, 0x17)

#Formato J

def jal_enc(args, curr_addr, symtab):
    rd = parse_reg(args[0])
    lbl = args[1]
    offset = symtab[lbl] - curr_addr
    return formato_j(offset, rd, 0x6F)

INSTR_MAP = {
    'add': ('R', add_enc),
    'sub': ('R', sub_enc),
    'sll': ('R', sll_enc),
    'srl': ('R', srl_enc),
    'sra': ('R', sra_enc),
    'and': ('R', and_enc),
    'or': ('R', or_enc),
    'xor': ('R', xor_enc),
    'slt': ('R', slt_enc),
    'sltu':('R', sltu_enc),

    'addi':('I', addi_enc),
    'andi':('I', andi_enc),
    'ori':('I', ori_enc),
    'xori':('I', xori_enc),
    'slti':('I', slti_enc),
    'sltiu':('I', sltiu_enc),
    'slli':('I', slli_enc),
    'srli':('I', srli_enc),
    'srai':('I', srai_enc),

    'lw':('I', lw_enc),
    'lb':('I', lb_enc),
    'lh':('I', lh_enc),

    'jalr':('I', jalr_enc),

    'sw':('S', sw_enc),
    'sb':('S', sb_enc),
    'sh':('S', sh_enc),

    'beq':('B', beq_enc),
    'bne':('B', bne_enc),
    'blt':('B', blt_enc),
    'bge':('B', bge_enc),

    'lui':('U', lui_enc),
    'auipc':('U', auipc_enc),

    'jal':('J', jal_enc),
}

tok_re = re.compile(r'[\s(),]+')

def parse_line(line):
    # tira comentarios
    line = line.split('#',1)[0].strip()
    if not line: return None
    # label?
    if ':' in line:
        parts = line.split(':',1)
        lbl = parts[0].strip()
        rest = parts[1].strip()
        if rest == '':
            return ('label', lbl)
        else:
            return ('label+rest', (lbl, rest))
    # diretiva?
    if line.startswith('.'):
        m = line.split(None,1)
        if len(m)==1:
            return ('directive', (m[0], ''))
        return ('directive', (m[0], m[1].strip()))
    # instrução e dividir operandos
    parts = line.strip().split(None,1)
    mnem = parts[0]
    args = []
    if len(parts) > 1:
        # separar virgulas, mas deixar os parenteses intactos da bola
        args = [a for a in re.split(r'\s*,\s*', parts[1]) if a!='']
    return ('instr', (mnem, args))

# ---------------------------
# Algoritimo de duas passagens
# ---------------------------
def assemble(lines):
    # pass 1: encontrar simpbolos 
    text_addr = TEXT_BASE
    data_addr = DATA_BASE
    symtab = {}
    # guarda elementos para a segunda passagem
    items = []  
    cur_section = 'text'
    for ln_no, raw in enumerate(lines, start=1):
        parsed = parse_line(raw)
        if not parsed: continue
        kind = parsed[0]
        if kind == 'label':
            lbl = parsed[1]
            addr = text_addr if cur_section=='text' else data_addr
            symtab[lbl] = addr
            items.append(('label', addr, lbl))
            continue
        if kind == 'label+rest':
            lbl, rest = parsed[1]
            addr = text_addr if cur_section=='text' else data_addr
            symtab[lbl] = addr
            items.append(('label', addr, lbl))
            # parse rest recursively
            parsed = parse_line(rest)
            if not parsed: continue
            kind = parsed[0]

        if kind == 'directive':
            dname, carg = parsed[1]
            if dname == '.text':
                cur_section = 'text'
                continue
            if dname == '.data':
                cur_section = 'data'
                continue
            if cur_section == 'text':
                if dname == '.align':
                    n = int(carg,0)
                    align_bytes = 1 << n
                    while text_addr % align_bytes != 0:
                        text_addr += 4
                    continue
            else:
                if dname == '.word':
                    vals = [int(x,0) for x in re.split(r'\s*,\s*', carg)]
                    for v in vals:
                        items.append(('data_word', data_addr, v))
                        data_addr += 4
                    continue
                if dname == '.half':
                    vals = [int(x,0) for x in re.split(r'\s*,\s*', carg)]
                    for v in vals:
                        items.append(('data_half', data_addr, v))
                        data_addr += 2
                    continue
                if dname == '.byte':
                    vals = [int(x,0) for x in re.split(r'\s*,\s*', carg)]
                    for v in vals:
                        items.append(('data_byte', data_addr, v))
                        data_addr += 1
                    continue
                if dname == '.ascii' or dname == '.asciiz':
                    m = re.match(r'\"(.*)\"', carg)
                    if not m:
                        raise ValueError(f"String literal expected at line {ln_no}")
                    s = m.group(1).encode('utf-8').decode('unicode_escape')
                    b = s.encode('utf-8')
                    for ch in b:
                        items.append(('data_byte', data_addr, ch))
                        data_addr += 1
                    if dname == '.asciiz':
                        items.append(('data_byte', data_addr, 0))
                        data_addr += 1
                    continue
                if dname == '.space':
                    n = int(carg,0)
                    for _ in range(n):
                        items.append(('data_byte', data_addr, 0))
                        data_addr += 1
                    continue
                if dname == '.align':
                    n = int(carg,0)
                    align_bytes = 1 << n
                    while data_addr % align_bytes != 0:
                        items.append(('data_byte', data_addr, 0))
                        data_addr += 1
                    continue
                items.append(('unknown_directive', (dname, carg)))
            continue

        if kind == 'instr':
            mnem, args = parsed[1]
            if mnem == '.text' or mnem == '.data':
                if mnem == '.text': cur_section='text'
                else: cur_section='data'
                continue
            if cur_section == 'text':
                items.append(('text_instr', text_addr, (mnem, args, raw.strip())))
                text_addr += 4
            else:
                items.append(('unknown_in_data', (mnem,args)))
    # primeiro passo feito tabela completa mas sem valores calculados
 # segunda passagem: resolvendo valores binarios e e as labels
    text_bin = OrderedDict()  # addr -> 32-bit int
    data_bin = OrderedDict()  # addr -> byte (0-255) 
    for it in items:
        if it[0] == 'data_word':
            addr = it[1]; val = it[2]
            bytes_ = [(val >> (8*i)) & 0xff for i in range(4)]
            for i,b in enumerate(bytes_):
                data_bin[addr+i] = b
        if it[0] == 'data_half':
            addr = it[1]; val = it[2]
            bytes_ = [(val >> (8*i)) & 0xff for i in range(2)]
            for i,b in enumerate(bytes_):
                data_bin[addr+i] = b
        if it[0] == 'data_byte':
            addr = it[1]; val = it[2] & 0xff
            data_bin[addr] = val

    # resolver as labels
    for it in items:
        if it[0] == 'text_instr':
            addr = it[1]; mnem,args,raw = it[2]
            mnem_lower = mnem.lower()
            #pseudoinstrução a adicionar no futuro 
            if mnem_lower == 'la':
                sym = args[1] if len(args)>1 else args[0]  # allow la rd,sym or la sym? assume la rd, sym
                rd = parse_reg(args[0])
                if sym not in symtab:
                    raise ValueError(f"símbolo {sym} não encontrado para 'la' at {hex(addr)}")
                target = symtab[sym]
                offset = target - addr
                imm_hi = (target - addr) & ~0xfff
                # encode auipc
                auipc_word = formato_u(imm_hi, rd, 0x17)
                text_bin[addr] = auipc_word
                imm_lo = (target - (addr + imm_hi)) 
                addi_word = formato_i(imm_lo, rd, 0x0, rd, 0x13)
                text_bin[addr+4] = addi_word
                continue
            if mnem_lower in INSTR_MAP:
                typ, handler = INSTR_MAP[mnem_lower]
                try:
                    if typ == 'R' or typ == 'I' or typ == 'S' or typ == 'U':
                        word = handler(args)
                        text_bin[addr] = word
                    elif typ == 'B' or typ == 'J':
                        word = handler(args, addr, symtab)
                        text_bin[addr] = word
                    else:
                        raise ValueError("tipo desconhecido")
                except Exception as e:
                    raise ValueError(f"erro ao montar instrução '{raw}' em {hex(addr)}: {e}")
            else:
                raise ValueError(f"mnemônico desconhecido '{mnem}' em {hex(addr)}")
    return text_bin, data_bin, symtab

# ---------------------------
# I/O?
# ---------------------------
#analizar direito dps oq o deep seek fez
def write_text_bin_file(text_bin, data_bin, out_txt_path, raw_bin_path=None):
    # write textual binary: text instructions as 32-bit binary lines, then data bytes as bytes with addresses noted
    with open(out_txt_path, 'w') as f:
        f.write("# Text segment (addr: 32-bit binary)\n")
        for addr, word in text_bin.items():
            f.write(f"{hex(addr)}: {int_to_bin(word,32)}\n")
        f.write("\n# Data bytes (addr: byte)\n")
        # group by contiguous regions
        addrs = sorted(data_bin.keys())
        for a in addrs:
            f.write(f"{hex(a)}: {int(data_bin[a])}\n")
    if raw_bin_path:
        # combine text and data in two separate raw files for simplicity: text.raw (instructions little-endian) and data.raw
        # We'll write a single raw file with text then data segments padded? Simpler: produce two files
        txt_raw = raw_bin_path + ".text.raw"
        data_raw = raw_bin_path + ".data.raw"
        with open(txt_raw, 'wb') as ft:
            for addr, word in text_bin.items():
                ft.write(struct.pack('<I', word))
        with open(data_raw, 'wb') as fd:
            # write bytes starting from lowest address to highest contiguous filling gaps with zeros
            if data_bin:
                min_a = min(data_bin.keys()); max_a = max(data_bin.keys())
                for a in range(min_a, max_a+1):
                    b = data_bin.get(a, 0)
                    fd.write(bytes([b]))
        print(f"raw text written to {txt_raw}, raw data written to {data_raw}")
#organizar levemente o arquivo né
#proximo passo é fazer ele ser inteligente reconhecer dependencias e relações com memoria de predição de branch
def main():
    if len(sys.argv) < 3:
        print("Uso: python rv32_assembler.py entrada.s saida.txt [raw_out_prefix(optional)]")
        sys.exit(1)
    infile = sys.argv[1]; outfile = sys.argv[2]
    rawprefix = sys.argv[3] if len(sys.argv) > 3 else None
    with open(infile,'r',encoding='utf-8') as f:
        lines = f.readlines()
    text_bin, data_bin, symtab = assemble(lines)
    write_text_bin_file(text_bin, data_bin, outfile, rawprefix)
    print("Montagem concluída.")
    print(f"Instruções: {len(text_bin)} words; Dados bytes: {len(data_bin)}")
    print("Símbolos:")
    for k,v in symtab.items():
        print(f"  {k} -> {hex(v)}")

if __name__ == '__main__':
    main()