import os
import re
from xml.etree import ElementTree as ET

import qrcode
from pagos import (Comprobante, Concepto, DoctoRelacionado, Emisor, Pago,
                   Receptor, TimbreFiscalDigital)

directorio = 'recursos'
patron = r'\d{2}\-\w{7}\-\w{7}\.xml'
archivos = os.listdir(directorio)
archivos_validos = re.findall(patron, '|'.join(archivos))


def leer_archivos(archivo):
    tree = ET.parse(archivo)
    root = tree.getroot()

    ns_cfdi = '{http://www.sat.gob.mx/cfd/3}'
    ns_pago10 = '{http://www.sat.gob.mx/Pagos}'
    ns_tfd = '{http://www.sat.gob.mx/TimbreFiscalDigital}'

    for child in root:
        if child.tag == f'{ns_cfdi}Emisor':
            emisor = Emisor(
                child.attrib['Nombre'],
                child.attrib['RegimenFiscal'],
                child.attrib['Rfc']
            )
        elif child.tag == f'{ns_cfdi}Receptor':
            receptor = Receptor(
                child.attrib['Nombre'],
                child.attrib['Rfc'],
                child.attrib['UsoCFDI'],
            )
        elif child.tag == f'{ns_cfdi}Conceptos':
            for grandchild in child:
                concepto = Concepto(
                    grandchild.attrib['Cantidad'],
                    grandchild.attrib['ClaveProdServ'],
                    grandchild.attrib['ClaveUnidad'],
                    grandchild.attrib['Descripcion'],
                    grandchild.attrib['Importe'],
                    grandchild.attrib['ValorUnitario'],
                )
        elif child.tag == f'{ns_cfdi}Complemento':
            for grandchild in child:
                if grandchild.tag == f'{ns_pago10}Pagos':
                    element_pagos = list(grandchild)
                if grandchild.tag == f'{ns_tfd}TimbreFiscalDigital':
                    timbre = TimbreFiscalDigital(
                        grandchild.attrib['FechaTimbrado'],
                        grandchild.attrib['NoCertificadoSAT'],
                        grandchild.attrib['RfcProvCertif'],
                        grandchild.attrib['SelloCFD'],
                        grandchild.attrib['SelloSAT'],
                        grandchild.attrib['UUID'],
                        grandchild.attrib['Version'],
                    )

    pagos = []
    for element_pago in element_pagos:
        element_docto = element_pago.find(
            f'{ns_pago10}DoctoRelacionado')
        docto = DoctoRelacionado(
            element_docto.attrib['Folio'],
            element_docto.attrib['IdDocumento'],
            element_docto.attrib['ImpPagado'],
            element_docto.attrib['ImpSaldoAnt'],
            element_docto.attrib['ImpSaldoInsoluto'],
            element_docto.attrib['MetodoDePagoDR'],
            element_docto.attrib['MonedaDR'],
            element_docto.attrib['NumParcialidad'],
            element_docto.attrib['Serie'],
        )
        pago = Pago(
            element_pago.attrib['FechaPago'],
            element_pago.attrib['FormaDePagoP'],
            element_pago.attrib['MonedaP'],
            element_pago.attrib['Monto'],
            docto,
        )
        pagos.append(pago)

    if root.tag == f'{ns_cfdi}Comprobante':
        comprobante = Comprobante(
            root.attrib['NoCertificado'],
            root.attrib['Fecha'],
            root.attrib['Folio'],
            root.attrib['LugarExpedicion'],
            root.attrib['Moneda'],
            root.attrib['Sello'],
            root.attrib['Serie'],
            root.attrib['SubTotal'],
            root.attrib['TipoDeComprobante'],
            root.attrib['Total'],
            root.attrib['Version'],
            emisor,
            receptor,
            concepto,
            pagos,
            timbre,
        )

    ruta_f33 = ['recursos', 'ACA080131IL5-01-UA29001-RH00417.F33']
    archivo_f33 = os.sep.join(ruta_f33)

    with open(archivo_f33, 'r') as f33:
        lineas = {x.rstrip().split('|')[0]: x.rstrip().split('|')[
            1:] for x in f33}

    comprobante.total_letra = lineas['DOCUMENTO'][15]
    comprobante.receptor.clave = lineas['CLIENTE'][0]
    comprobante.receptor.calle = lineas['CLIENTE'][2]
    comprobante.receptor.colonia = lineas['CLIENTE'][3]
    comprobante.receptor.municipio = lineas['CLIENTE'][10]
    comprobante.receptor.estado = lineas['CLIENTE'][11]
    comprobante.receptor.pais = lineas['CLIENTE'][12]
    comprobante.receptor.codigo_postal = lineas['CLIENTE'][7]

    img = qrcode.make(
        f'?re={comprobante.emisor.rfc}&rr={comprobante.receptor.rfc}' +
        '&tt={comprobante.total}&id={comprobante.timbre.uuid}'
    )
    img.save(f'{comprobante.emisor.rfc}.png', format='png')

    return comprobante


if __name__ == '__main__':
    while True:
        for archivo_valido in archivos_validos:
            ruta = [directorio, archivo_valido]
            archivo = os.sep.join(ruta)
            print(leer_archivos(archivo))
