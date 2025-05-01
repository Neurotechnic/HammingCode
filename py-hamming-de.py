from typing import List
from math import log2, ceil
from random import randrange, sample
from colorama import Fore, Back, Style
from colorama import just_fix_windows_console


def __hamming_common(src: List[List[int]], s_num: int, encode=True) -> None:
    """
    Here's the real magic =)
    """
    s_range = range(s_num)

    for i in src:
        sindrome = 0
        for s in s_range:
            sind = 0
            for p in range(2 ** s, len(i) + 1, 2 ** (s + 1)):
                for j in range(2 ** s):
                    if (p + j) > len(i):
                        break
                    sind ^= i[p + j - 1]

            if encode:
                i[2 ** s - 1] = sind
            else:
                sindrome += (2 ** s * sind)

        if (not encode) and sindrome:
            i[sindrome - 1] = int(not i[sindrome - 1])


def hamming_encode(msg: str, mode: int=8) -> str:
    """
    Kodierung der Nachricht mit Hamming-Code.

    :param msg: Message string to encode
    :param mode: Anzahl der Datenbits Bits
    :return: 
    """

    result = ""

    msg_b = msg.encode("utf-8")
    s_num = ceil(log2(log2(mode + 1) + mode + 1))   # Anzahl der Paritätsbits
    bit_seq = []
    for byte in msg_b:  # Bytes in Binärwerte umwandeln; jedes Bit in Unterliste speichern
        bit_seq += list(map(int, f"{byte:08b}"))

    res_len = ceil((len(msg_b) * 8) / mode)     # length of result (bytes)
    bit_seq += [0] * (res_len * mode - len(bit_seq))    # filling zeros

    to_hamming = []

    for i in range(res_len):    # Einfügen von Steuerbits an bestimmten Positionen
        code = bit_seq[i * mode:i * mode + mode]
        for j in range(s_num):
            code.insert(2 ** j - 1, 0)
        to_hamming.append(code)

    __hamming_common(to_hamming, s_num, True)   # process

    for i in to_hamming:
        result += "".join(map(str, i))

    return result


def hamming_decode(msg: str, mode: int=8) -> str:
    """
    Dekodierung der Nachricht mit Hamming-Code.

    :param msg: Message string to decode
    :param mode: Anzahl der Datenbits Bits
    :return: 
    """

    result = ""

    s_num = ceil(log2(log2(mode + 1) + mode + 1))   # Anzahl der Paritätsbits
    res_len = len(msg) // (mode + s_num)    # length of result (bytes)
    code_len = mode + s_num     # length of one code sequence

    to_hamming = []

    for i in range(res_len):    # convert binary-like string to int-list
        code = list(map(int, msg[i * code_len:i * code_len + code_len]))
        to_hamming.append(code)

    __hamming_common(to_hamming, s_num, False)  # process

    for i in to_hamming:    # Paritätsbits löschen
        for j in range(s_num):
            i.pop(2 ** j - 1 - j)
        result += "".join(map(str, i))

    msg_l = []

    for i in range(len(result) // 8):   # convert from binary-sring value to integer
        val = "".join(result[i * 8:i * 8 + 8])
        msg_l.append(int(val, 2))

    result = bytes(msg_l).decode("utf-8")   # finally decode to a regular string

    return result

def hamming_decode_raw(msg: str, mode: int=8) -> bytes:
    """
    Gibt Bytes zurück (ohne den Versuch der Dekodierung in UTF-8).
    """
    from math import log2, ceil

    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    res_len = len(msg) // (mode + s_num)
    code_len = mode + s_num

    to_hamming = []
    for i in range(res_len):
        code = list(map(int, msg[i * code_len : i * code_len + code_len]))
        to_hamming.append(code)

    # Korrektur von Fehlern
    __hamming_common(to_hamming, s_num, False)

    # Löschen der Paritätsbits
    for i in range(res_len):
        for j in range(s_num):
            to_hamming[i].pop(2 ** j - 1 - j)

    data_bits = "".join("".join(map(str, block)) for block in to_hamming)
    msg_bytes = []
    for i in range(0, len(data_bits), 8):
        byte_str = data_bits[i : i + 8]
        msg_bytes.append(int(byte_str, 2))

    return bytes(msg_bytes)

def noizer(msg: str, mode: int) -> str:
    """
    Erzeugt einen Zufallsfehler in jedem Element einer Hamming-kodierten Nachricht
    """
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    code_len = mode + s_num
    cnt = len(msg) // code_len
    result = ""

    for i in range(cnt):
        to_noize = seq[i * code_len:i * code_len + code_len]
        noize = randrange(code_len)
        to_noize[noize] = int(not to_noize[noize])
        result += "".join(map(str, to_noize))

    return result

def noizer2(msg: str, mode: int) -> str:
    """
    Erzeugt zwei Zufallsfehler in jedem Element einer Hamming-kodierten Nachricht
    """
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    code_len = mode + s_num
    cnt = len(seq) // code_len
    result = ""

    for i in range(cnt):
        block = seq[i * code_len : i * code_len + code_len]
        # Wähle 2 zufällige Positionen im Block, die wir umdrehen werden
        flip_positions = sample(range(code_len), 2)
        for pos in flip_positions:
            block[pos] = 1 - block[pos]
        result += "".join(map(str, block))

    return result

def chunk_string(text: str, chunk_size: int, separator: str) -> str:
    # In Stücke aufteilen und zusammenfügen
    return separator.join(text[i:i+chunk_size] for i in range(0, len(text), chunk_size))

def string_to_bit_sequence(msg: str) -> list[int]:
    """
    Wandelt die Eingabezeichenkette in eine Liste von Bits (0 und 1) um, die den UTF-8-Codes der Zeichen entsprechen.
    
    :param msg: Ursprünglicher String
    :return: Liste von Bits (0 und 1)
    """
    bit_seq = []
    msg_b = msg.encode("utf-8")
    for byte in msg_b:
        # Wir wandeln jedes Byte in das Binärformat 08b (8 Bit) um
        #und konvertieren jedes Zeichen '0' oder '1' in die ganze Zahl 0 oder 1.
        bit_seq.extend(map(int, f"{byte:08b}"))
    return bit_seq

def string_to_binary_string(msg: str) -> str:
    """
    Wandelt die Eingabezeichenkette in eine Binärdarstellung (0 und 1) um
    und gibt das Ergebnis als einen einzigen String zurück.

    :param msg: Ursprünglicher String
    :return: Ein String mit der Bitdarstellung (z. B. '0100100001100101...')
    """
    return ''.join(f"{byte:08b}" for byte in msg.encode("utf-8"))

def highlight_parity(hamming_str: str, mode: int) -> str:
    """
    Hebt die Paritätsbits in einem Hamming-Code-String grün hervor.
    Die Paritätsbits befinden sich an den Positionen 2^p - 1 (0-basiert).
    """
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    code_len = mode + s_num
    highlighted_chunks = []

    # Vorab teilen wir den gesamten String in Blöcke mit je code_len Bits auf.
    for i in range(0, len(hamming_str), code_len):
        block = hamming_str[i:i+code_len]
        block_colored = []
        # Wir berechnen alle Paritätsindizes im aktuellen Block.
        parity_positions = [2**p - 1 for p in range(s_num)]  # 0-based
        for idx, bit in enumerate(block):
            if idx in parity_positions:
                # Paritätsbit – grün hervorheben
                block_colored.append(Fore.GREEN + bit + Style.RESET_ALL)
            else:
                block_colored.append(bit)
        highlighted_chunks.append("".join(block_colored))

    # Wir fügen die Blöcke mit Leerzeichen zusammen, um jeden Codeblock visuell zu trennen.
    return " ".join(highlighted_chunks)

def highlight_noise_bits(original: str, noised: str, mode: int) -> str:
    """
    Hebt die Bits rot hervor, die sich durch das „Rauschen“ verändert haben (original -> noised).
    Dabei wird die Zeichenkette in Blöcke derselben Länge wie beim Kodieren aufgeteilt.
    """
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    code_len = mode + s_num
    highlighted_chunks = []

    # Wir teilen beide Strings in Blöcke mit je code_len Bits auf.
    for i in range(0, len(original), code_len):
        orig_block = original[i : i + code_len]
        noz_block = noised[i : i + code_len]
        block_colored = []
        for idx in range(len(orig_block)):
            if orig_block[idx] != noz_block[idx]:
                # Dieses Bit hat sich verändert - wir heben es rot hervor.
                block_colored.append(Fore.RED + noz_block[idx] + Style.RESET_ALL)
            else:
                block_colored.append(noz_block[idx])
        highlighted_chunks.append("".join(block_colored))

    return " ".join(highlighted_chunks)

if __name__ == "__main__":
    just_fix_windows_console()
    MODE = 8    # Anzahl der Paritätsbits
    msg = input("Gib eine Zeichenkette ein: ")
    print("\n"+ "Anzahl der Paritätsbits = "+str(MODE))
    print("msg:", chunk_string(string_to_binary_string(msg), MODE, " "))

    enc_msg = hamming_encode(msg, MODE) # Encode your message to Hamming code
    print("enc:", highlight_parity(enc_msg, MODE))

    noize_msg = noizer(enc_msg, MODE)   # Noizer for encoded message
    print(Fore.RED+"nz: "+Style.RESET_ALL, highlight_noise_bits(enc_msg, noize_msg, MODE))

    dec_msg = hamming_decode(noize_msg, MODE)   # Hamming decode
    print("dec:", dec_msg)


    MODE = 4    # Anzahl der Paritätsbits
    print("\n"+ "Anzahl der Paritätsbits = "+str(MODE))
    print("msg:", chunk_string(string_to_binary_string(msg), MODE, " "))
    enc_msg = hamming_encode(msg, MODE) # Encode your message to Hamming code
    print("enc:", highlight_parity(enc_msg, MODE))

    noize_msg = noizer(enc_msg, MODE)   # Noizer for encoded message
    noize_msg2 = noizer2(enc_msg, MODE)
    print(Fore.RED+"nz1:"+Style.RESET_ALL, highlight_noise_bits(enc_msg, noize_msg, MODE))
    dec_msg = hamming_decode(noize_msg, MODE)   # Hamming decode
    print("dec:", dec_msg+"\n")
    print(Fore.RED+"nz2:"+Style.RESET_ALL, highlight_noise_bits(enc_msg, noize_msg2, MODE))
    try:
        raw_bytes = hamming_decode_raw(noize_msg2, MODE)
        # Jetzt dekodieren wir „sanft“, wobei falsche Zeichen ersetzt werden.
        dec_msg = raw_bytes.decode("utf-8", errors="replace")
        # Oder wir ignorieren fehlerhafte Sequenzen:
        # dec_msg = raw_bytes.decode("utf-8", errors="ignore")
        print("dec:", Back.RED+dec_msg+Style.RESET_ALL)
    except Exception as e:
        # Jeder andere Fehler im Prozess
        print("dec:", f"Couldn't even get the bytes back: {e}")
