import os

from pdfs import leer_archivo, ordena_archivos
from layout import ImpresionPago, ImpresionComprobante

ruta = [r'\\192.168.24.10', 'e$', 'cfd', 'almacen']
mes_anio = '022019'


def agencias():
    agencias = ['QMO710112RH2', 'AIQ070917FVA', 'ACA080131IL5', 'ACE050912GZ0',
                'APA040128N75', 'RCA100823GI9']
    return agencias


def documento(ruta, mes_anio, agencia, tipo):
    try:
        nombre = f'{agencia}-{tipo}.pdf'
        archivo = ordena_archivos(agencia, mes_anio, ruta, tipo)[0]
        comp = leer_archivo(archivo, mes_anio, ruta, agencia)
        if tipo == 'UA20':
            imp = ImpresionPago(comp)
        else:
            imp = ImpresionComprobante(comp)
        imp.genera_pdf()
        os.rename(imp.nombre, nombre)
    except IndexError:
        pass
    except FileExistsError:
        os.remove(nombre)
        os.rename(imp.nombre, nombre)


def test_pagos():
    for agencia in agencias():
        documento(ruta, mes_anio, agencia, 'UA29')

def test_notas():
    for agencia in agencias():
        documento(ruta, mes_anio, agencia, 'UD03')

def test_credito():
    for agencia in agencias():
        documento(ruta, mes_anio, agencia, 'UA03')

