import os

from lxml import etree as ET
from pdfs import construye_comprobante, cons_f33
from layout import (ImpresionComprobante, ImpresionPago, ImpresionServicio,
                    ImpresionVehiculos)


def genera_impresion(tipo, comprobante):
    if tipo == 'servicio':
        imp = ImpresionServicio(comprobante)
    elif tipo == 'recibos':
        imp = ImpresionPago(comprobante)
    elif tipo == 'vehiculos':
        imp = ImpresionVehiculos(comprobante)
    else:
        imp = ImpresionComprobante(comprobante)
    imp.genera_pdf()


def construye_f33(archivo, comprobante):
    lista_ruta = archivo.split(os.sep)
    nombre = lista_ruta[-1]
    emisor = comprobante.emisor.rfc.upper()
    nombre_archivo = f'{emisor}-{nombre}.F33'
    ruta_archivo = os.path.join(*lista_ruta[:-1], nombre_archivo)
    return ruta_archivo


def ruta_out(archivo):
    return os.path.join('test', 'output', archivo)


def get_tipos(ruta):
    tipos = []
    arc_xml = []
    for ubicacion, folders, archivos in os.walk(ruta):
        tipos += folders
        for nombre in archivos:
            if nombre.endswith('.xml'):
                arc_xml.append(os.path.join(ubicacion, nombre))
    for tipo in tipos:
        xml_tipo = [_ for _ in arc_xml if tipo in _]
        for num, xml in enumerate(xml_tipo):
            tree = ET.parse(xml)
            ruta_archivo = ruta_out(f'{tipo}{num}.pdf')
            comprobante = construye_comprobante(tree, ruta_archivo)
            f33 = construye_f33(xml[:-4], comprobante)
            comprobante = cons_f33(comprobante, f33)
            genera_impresion(tipo, comprobante)


def test_archivos():
    get_tipos(os.path.join('test', 'archivos'))
