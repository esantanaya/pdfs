import qrcode
from pagos import Comprobante, Emisor, Receptor, Concepto, DoctoRelacionado
from pagos import Pago, TimbreFiscalDigital
from xml.etree import ElementTree as ET
import os

ruta = ['recursos', '01-UA29001-RH00417.xml']
archivo = os.sep.join(ruta)

tree = ET.parse(archivo)
root = tree.getroot()

for child in root:
    if child.tag == '{http://www.sat.gob.mx/cfd/3}Emisor':
        emisor = Emisor(
            child.attrib['Nombre'],
            child.attrib['RegimenFiscal'],
            child.attrib['Rfc']
        )
    elif child.tag == '{http://www.sat.gob.mx/cfd/3}Receptor':
        receptor = Receptor(
            child.attrib['Nombre'],
            child.attrib['Rfc'],
            child.attrib['UsoCFDI'],
        )
    elif child.tag == '{http://www.sat.gob.mx/cfd/3}Conceptos':
        conceptos = []
        for grandchild in child:
            concepto = Concepto(
                grandchild.attrib['Cantidad'],
                grandchild.attrib['ClaveProdServ'],
                grandchild.attrib['ClaveUnidad'],
                grandchild.attrib['Descripcion'],
                grandchild.attrib['Importe'],
                grandchild.attrib['ValorUnitario'],
            )
            conceptos.append(concepto)
    elif child.tag == '{http://www.sat.gob.mx/cfd/3}Complemento':
        for grandchild in child:
            if grandchild.tag == '{http://www.sat.gob.mx/Pagos}Pagos':
                element_pagos = grandchild.getchildren()
            if grandchild.tag == '{http://www.sat.gob.mx/TimbreFiscalDigital}TimbreFiscalDigital':
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
    element_docto = element_pago.find('{http://www.sat.gob.mx/Pagos}DoctoRelacionado')
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

if root.tag == '{http://www.sat.gob.mx/cfd/3}Comprobante':
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
        conceptos,
        pagos,
        timbre,
    )

ruta_f33 = ['recursos', 'ACA080131IL5-01-UA29001-RH00417.F33']
archivo_f33 = os.sep.join(ruta_f33)

with open(archivo_f33, 'r') as f33:
    lineas = {x.rstrip().split('|')[0]:x.rstrip().split('|')[1:] for x in f33}

comprobante.total_letra = lineas['DOCUMENTO'][15]
comprobante.receptor.calle = lineas['CLIENTE'][2]
comprobante.receptor.colonia = lineas['CLIENTE'][3]
comprobante.receptor.municipio = lineas['CLIENTE'][10]
comprobante.receptor.estado = lineas['CLIENTE'][11]
comprobante.receptor.pais = lineas['CLIENTE'][12]
