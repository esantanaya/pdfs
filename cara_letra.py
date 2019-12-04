import string


def caracter_letra(texto):
    NOMBRES = ('CERO', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS',
               'SIETE', 'OCHO', 'NUEVE')
    nombre_numero = dict(zip(string.digits, NOMBRES))
    lista_letras = []

    for letra in texto:
        if letra.isdigit():
            lista_letras.append(nombre_numero.get(letra))
        else:
            lista_letras.append(letra.upper())

    return ' '.join(lista_letras)
