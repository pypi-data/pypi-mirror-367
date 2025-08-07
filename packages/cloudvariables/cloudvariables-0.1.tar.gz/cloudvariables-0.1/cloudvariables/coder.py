import sys
sys.set_int_max_str_digits(2000000000)

def ncode(file, code, text):
    f = text.encode()
    c = int.from_bytes(f, byteorder='big')
    cc = ""
    output = c + code * 10**200
    with open(str(file), "wb") as f:
        f.write(str(output).encode())


def dcode(file, code):
    with open(str(file), "rb") as f:
        f = f.read()
    txt = f.decode()
    if txt == "" or txt.replace("\n", "") == "":
        return "\"{}\""
    c = int(txt) - (code * 10**200)
    output = list(c.to_bytes((c.bit_length() + 7) // 8, 'big').decode("unicode-escape").replace("\"", "\\\""))
    output[0] = ""
    output[-2] = ""
    o = ""
    for j0 in output:
        o += j0

    return o
