import os
import re

from lxml import etree as ET

from pdfs import construye_comprobante, compl_comp_f33
from layout import ImpresionPago, ImpresionComprobante, ImpresionServicio


def test_archivos_locales():
    for archivo in os.listdir('archivos'):
        if re.match(r'(\S*\.xml)$', archivo):
            tree = ET.parse(f'archivos\\{archivo}')
            comprobante = construye_comprobante(tree, archivo)
            tipo = comprobante.nombre_archivo[3:7]
            archivo_f33 = ('archivos\\' + comprobante.emisor.rfc + '-'
                           + comprobante.nombre_archivo[:-4] + '.f33')
            comprobante = compl_comp_f33(comprobante, archivo_f33)
            if tipo == 'UD10':
                imp = ImpresionServicio(comprobante)
            elif tipo == 'UA29':
                imp = ImpresionPago(comprobante)
            else:
                imp = ImpresionComprobante(comprobante)
            imp.genera_pdf()
