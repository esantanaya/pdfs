import os

from lxml import etree as ET
from pdfs import construye_comprobante


def get_tipos(ruta):
    tipos = []
    for ubicacion, folders, archivos in os.walk(ruta):
        breakpoint()
        tipos += folders
        for nombre in archivos:
            if nombre.endswith('.xml'):
                arc_xml = os.path.join(ubicacion, nombre)
            if nombre.endswith('.f33'):
                arc_f33 = os.path.join(ubicacion, nombre)
        for tipo in tipos:
            xml_tipo = [_ for _ in arc_xml if tipo in _]
            for num, xml in enumerate(xml_tipo):
                print(tipo, num)



def leer_archivo(ruta_archivo, archivo):
    tree = ET.parse(ruta_archivo)
    comprobante = construye_comprobante(tree, archivo)
