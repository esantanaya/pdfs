import os

from lxml import etree as ET
from pdfs import construye_comprobante


def get_tipos(ruta):
    tipos = []
    for ubicacion, folders, archivos in os.walk(ruta):
        tipos += folders
        for nombre in archivos:
            if nombre.endswith('.xml'):
                ar_xml = os.path.join(ubicacion, nombre)

    carpetas_archivos = {
        x:y for x, y in enumerate(os.walk(ruta))
    }
    tipos = carpetas_archivos.get(0)[1]
    return tipos


def leer_archivo(ruta_archivo, archivo):
    tree = ET.parse(ruta_archivo)
    comprobante = construye_comprobante(tree, archivo)

