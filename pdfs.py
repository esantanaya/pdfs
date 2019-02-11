import os
import re
import traceback

from lxml import etree as ET

from layout import ImpresionComprobante, ImpresionPago
from comprobante import (Comprobante, Concepto, DoctoRelacionado, Emisor, Pago,
                   Receptor, TimbreFiscalDigital)


def ordena_archivos(agencia, mes_anio, directorio, tipo):
    print(f'Ordenando archivos...')
    patron = r'\d{2}\-' + tipo + r'\w{3}\-\w{7}\.xml' #Para recibos
    ruta_archivos = (os.sep.join(directorio) + os.sep + agencia + os.sep +
                     mes_anio)
    try:
        archivos = os.listdir(ruta_archivos)
        archivos_validos = re.findall(patron, '|'.join(archivos))
        return archivos_validos
    except Exception as e:
        print(e)


def leer_archivo(archivo, mes_anio, ruta, agencia):
    print(f'leyendo archivo {archivo}')
    ruta = os.sep.join(ruta)
    tree = ET.parse(ruta + os.sep + agencia + os.sep + mes_anio + os.sep + archivo)
    root = tree.getroot()

    ns_cfdi = '{http://www.sat.gob.mx/cfd/3}'
    ns_pago10 = '{http://www.sat.gob.mx/Pagos}'
    ns_tfd = '{http://www.sat.gob.mx/TimbreFiscalDigital}'
    element_pagos = None
    conceptos = []
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
                conceptos.append(concepto)
        elif child.tag == f'{ns_cfdi}Complemento':
            for grandchild in child:
                if grandchild.tag == f'{ns_pago10}Pagos':
                    element_pagos = list(grandchild)
                if grandchild.tag == f'{ns_tfd}TimbreFiscalDigital':
                    str_timbre = ET.tostring(grandchild)
                    xdoc = ET.fromstring(str_timbre)
                    xslt = ET.parse(
                        'recursos\\xslt\\cadenaoriginal_TFD_1_1.xslt')
                    trans = ET.XSLT(xslt)
                    doc = trans(xdoc)
                    timbre = TimbreFiscalDigital(
                        grandchild.attrib['FechaTimbrado'],
                        grandchild.attrib['NoCertificadoSAT'],
                        grandchild.attrib['RfcProvCertif'],
                        grandchild.attrib['SelloCFD'],
                        grandchild.attrib['SelloSAT'],
                        grandchild.attrib['UUID'],
                        grandchild.attrib['Version'],
                        str(doc),
                    )

    pagos = []
    if element_pagos != None:
        for element_pago in element_pagos:
            total_pagos = 0
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
        print(f'Creando comprobante')
        comprobante = Comprobante(
            archivo,
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
            conceptos=conceptos,
            pagos=pagos,
            timbre=timbre,
        )

        if comprobante.tipo_comprobante != 'P':
            comprobante.forma_pago = root.attrib['FormaPago']
            comprobante.metodo_pago = root.attrib['MetodoPago']

    ruta_f33 = [
        '\\\\192.168.24.10',
        'E$',
        'CFD',
        'Intercambio',
        'Procesado',
        f'{emisor.rfc}',
        mes_anio,
        f'{emisor.rfc}-{archivo[:-4]}.F33',
    ]
    archivo_f33 = os.sep.join(ruta_f33)
    print(f'leyendo archivo {archivo_f33}')
    try:
        with open(archivo_f33, 'r') as f33:
            lineas = {
                x.rstrip().split('|')[0]:
                x.rstrip().split('|')[1:] for x in f33
            }
            comprobante.total_letra = lineas['DOCUMENTO'][15]
            comprobante.cuenta_pago = lineas['DOCUMENTO'][13]
            comprobante.receptor.clave = lineas['CLIENTE'][0]
            comprobante.receptor.calle = lineas['CLIENTE'][2]
            comprobante.receptor.colonia = lineas['CLIENTE'][3]
            comprobante.receptor.municipio = lineas['CLIENTE'][10]
            comprobante.receptor.estado = lineas['CLIENTE'][11]
            comprobante.receptor.pais = lineas['CLIENTE'][12]
            comprobante.receptor.codigo_postal = lineas['CLIENTE'][7]
    except FileNotFoundError as ffe:
        print(f'{ffe} | Buscando en Errores!')
        archivo_error = archivo_f33.replace('Procesado', 'Errores')
        try:
            with open(archivo_error, 'r') as f33:
                print(f'Encontramos el F33 en errores!')
                lineas = {
                    x.rstrip().split('|')[0]:
                    x.rstrip().split('|')[1:] for x in f33
                }
                comprobante.total_letra = lineas['DOCUMENTO'][15]
                comprobante.cuenta_pago = lineas['DOCUMENTO'][13]
                comprobante.receptor.clave = lineas['CLIENTE'][0]
                comprobante.receptor.calle = lineas['CLIENTE'][2]
                comprobante.receptor.colonia = lineas['CLIENTE'][3]
                comprobante.receptor.municipio = lineas['CLIENTE'][10]
                comprobante.receptor.estado = lineas['CLIENTE'][11]
                comprobante.receptor.pais = lineas['CLIENTE'][12]
                comprobante.receptor.codigo_postal = lineas['CLIENTE'][7]
        except Exception as e:
            print(f'{e} | tampoco lo encontramos en errores!')
            with open('errores.log', '+a') as log:
                log.write('\n'+str(e))
    return comprobante

def main_pagos():
    agencias = {
        1: 'ACE050912GZ0',
        2: 'APA040128N75',
        3: 'RCA100823GI9',
        4: 'ACA080131IL5',
        5: 'AIQ070917FVA',
        6: 'QMO710112RH2',
    }
    tipos = {
        'Pagos': 'UA29',
        'Notas': 'UD03',
        'Credito': 'UA03'
    }
    num = int(input(f'Selecciona una agencia de la lista {agencias}\n'))
    agencia = agencias[num]
    mes_anio = input(f'Ingresa el mes y anio: \n')
    indice = input(f'Selecciona el tipo: {tipos} \n')
    tipo = tipos[indice]

    ruta = [
        '\\\\192.168.24.10',
        'E$',
        'CFD',
        'Almacen',
    ]
    for archivo_valido in ordena_archivos(agencia, mes_anio, ruta, tipo):
        try:
            comp = leer_archivo(archivo_valido, mes_anio, ruta, agencia)
            if tipo != 'UA29':
                imp = ImpresionComprobante(comp)
            else:
                imp = ImpresionPago(comp)
            imp.genera_pdf()
        except KeyError as ke:
            traceback.print_exc()
            with open('errores.log', '+a', encoding='UTF-8') as log:
                log.write(f'\n [Error] en {agencia}-{archivo_valido} no se encontró {str(ke)}')
            continue
        except Exception as e:
            print(e)
            traceback.print_exc()
            with open('errores.log', '+a') as log:
                log.write('\n'+str(e))
            continue

if __name__ == '__main__':
    main_pagos()
