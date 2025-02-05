import os
import re
import traceback
import logging
import configparser

from lxml import etree as ET

from layout import (ImpresionComprobante, ImpresionPago, ImpresionServicio,
                    ImpresionVehiculos)
from comprobante import (Comprobante, Concepto, DoctoRelacionado, Emisor, Pago,
                         Receptor, TimbreFiscalDigital, Vehiculo,
                         VehiculoNuevo, CfdiRelacionado)


logging.basicConfig(filename=os.path.join('errores.log'),
                    format='%(asctime)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    level=logging.INFO)


def ordena_archivos(agencia, mes_anio, directorio, tipo):
    print(f'Ordenando archivos...')
    logging.info(f'Inicio')
    patron = r'\d{2}\-' + tipo + r'\w{3}\-\w{7}\.xml'
    ruta_archivos = (os.sep.join(directorio) + os.sep + agencia + os.sep +
                     mes_anio)
    try:
        archivos = os.listdir(ruta_archivos)
        archivos_validos = re.findall(patron, '|'.join(archivos))
        return archivos_validos
    except Exception as e:
        print(e)
        logging.error(e)


def construye_comprobante(tree, archivo):
    root = tree.getroot()
    ns_cfdi = '{http://www.sat.gob.mx/cfd/3}'
    ns_pago10 = '{http://www.sat.gob.mx/Pagos}'
    ns_tfd = '{http://www.sat.gob.mx/TimbreFiscalDigital}'
    element_pagos = None
    uuid_rel = None
    conceptos = []
    for child in root:
        if child.tag == f'{ns_cfdi}CfdiRelacionados':
            rel = child.find(f'{ns_cfdi}CfdiRelacionado')
            if rel is not None:
                uuid_rel = CfdiRelacionado(
                    child.attrib.get('TipoRelacion'),
                    rel.attrib.get('UUID'),
                )
        if child.tag == f'{ns_cfdi}Emisor':
            emisor = Emisor(
                child.attrib['Nombre'],
                child.attrib['RegimenFiscal'],
                child.attrib['Rfc']
            )
        if child.tag == f'{ns_cfdi}Receptor':
            receptor = Receptor(
                child.attrib['Nombre'],
                child.attrib['Rfc'],
                child.attrib['UsoCFDI'],
            )
        if child.tag == f'{ns_cfdi}Conceptos':
            for grandchild in child:
                if grandchild.tag == f'{ns_cfdi}Concepto':
                    concepto = Concepto(
                        grandchild.attrib['Cantidad'],
                        grandchild.attrib['ClaveProdServ'],
                        grandchild.attrib.get('NoIdentificacion'),
                        grandchild.attrib['ClaveUnidad'],
                        grandchild.attrib['Descripcion'],
                        grandchild.attrib['Importe'],
                        grandchild.attrib['ValorUnitario'],
                    )
                    conceptos.append(concepto)
        if child.tag == f'{ns_cfdi}Complemento':
            for grandchild in child:
                if grandchild.tag == f'{ns_pago10}Pagos':
                    element_pagos = list(grandchild)
                if grandchild.tag == f'{ns_tfd}TimbreFiscalDigital':
                    str_timbre = ET.tostring(grandchild)
                    xdoc = ET.fromstring(str_timbre)
                    xslt = ET.parse(os.path.join(
                        'recursos',
                        'xslt',
                        'cadenaoriginal_TFD_1_1.xslt',
                    ))
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
    if element_pagos is not None:
        for element_pago in element_pagos:
            for element_docto in element_pago:
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
        impuestos = root.find(f'{ns_cfdi}Impuestos')
        if impuestos is not None:
            iva = impuestos.attrib.get('TotalImpuestosTrasladados')
            retencion = impuestos.attrib.get('TotalImpuestosRetenidos')
        else:
            iva = None
            retencion = None
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
            pagos=pagos,
            timbre=timbre,
            conceptos=conceptos,
            cfdi_relacionado=uuid_rel,
            iva=iva,
            retenidos=retencion,
        )
        if comprobante.tipo_comprobante != 'P':
            comprobante.forma_pago = root.attrib['FormaPago']
            comprobante.metodo_pago = root.attrib['MetodoPago']
    return comprobante


def dar_tipo_impresion(agencia, tipo):
   config = configparser.ConfigParser()
   config.read('layout.ini', encoding='utf-8')
   if agencia in config:
       emisor = config[agencia]
       return emisor.get(tipo).split('|')
   return []


def valida_nuevo(comprobante):
   config = configparser.ConfigParser()
   config.read('layout.ini', encoding='utf-8')
   if comprobante.emisor.rfc in config:
       emisor = config[comprobante.emisor.rfc]
       movs_nuevos = emisor.get('NV').split('|')
       tipo_mov = comprobante.nombre_archivo[3:7]
       return tipo_mov in movs_nuevos


def cons_f33(comprobante, archivo_f33, mensaje=None):
    vehiculo = Vehiculo()
    nuevo = VehiculoNuevo()
    conceptos = []
    try:
        with open(archivo_f33, 'r', encoding='latin-1') as f33:
            if mensaje:
                print('Encontramos el F33 en errores!')
            for linea in f33:
                t_lin = linea.rstrip().split('|')
                if t_lin[0] == 'CONCEPTO':
                    concepto = Concepto(t_lin[1], t_lin[3], t_lin[11],
                                        t_lin[2], t_lin[4], t_lin[6],
                                        t_lin[5])
                    conceptos.append(concepto)
        with open(archivo_f33, 'r', encoding='latin-1') as f33:
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

        nuevo.inventario = lineas['VEHICULO'][11]
        nuevo.serie = lineas['VEHICULO'][0]
        nuevo.condiciones_pago = lineas['VEHICULO'][24]
        nuevo.procedencia = lineas['VEHICULO'][13]
        nuevo.clave_vehicular = lineas['VEHICULO'][15]
        nuevo.marca = lineas['VEHICULO'][1]
        nuevo.linea = lineas['VEHICULO'][2]
        nuevo.modelo = lineas['VEHICULO'][3]
        nuevo.clase = lineas['VEHICULO'][12]
        nuevo.tipo = ''
        nuevo.color = lineas['VEHICULO'][4]
        nuevo.no_puertas = lineas['VEHICULO'][16]
        nuevo.no_cilindros = lineas['VEHICULO'][17]
        nuevo.capacidad = lineas['VEHICULO'][18]
        nuevo.combustible = lineas['VEHICULO'][19]
        nuevo.motor = lineas['VEHICULO'][5]
        nuevo.registro_vehicular = ''

        vehiculo.marca = lineas['VEHICULO'][1]
        vehiculo.modelo = lineas['VEHICULO'][2]
        vehiculo.anio = lineas['VEHICULO'][3]
        vehiculo.color = lineas['VEHICULO'][4]
        vehiculo.serie = lineas['VEHICULO'][0]
        vehiculo.kilometraje = lineas['VEHICULO'][8]
        vehiculo.placas = lineas['VEHICULO'][9]
        vehiculo.motor = lineas['VEHICULO'][5]
        vehiculo.referencia = (f'{lineas["VEHICULO"][6]}-'
                               f'{lineas["VEHICULO"][7]}')
        vehiculo.recepcionista = lineas['VEHICULO'][10]
        vehiculo.siniestro = lineas['EXTRAS'][6]
        vehiculo.bonete = lineas['EXTRAS'][7]
    except IndexError:
        vehiculo.siniestro = 'NA'
        vehiculo.bonete = 'NA'
    except FileNotFoundError:
        raise FileNotFoundError
    else:
        if not valida_nuevo(comprobante):
            comprobante.conceptos = conceptos
    finally:
        comprobante.vehiculo = vehiculo
        comprobante.vehiculo_nuevo = nuevo
    return comprobante


def compl_comp_f33(comprobante, archivo_f33):
    print(f'leyendo archivo {archivo_f33}')
    try:
        comprobante = cons_f33(comprobante, archivo_f33)
    except FileNotFoundError as ffe:
        print(f'{ffe} | Buscando en Errores!')
        logging.error(f'No encontramos {archivo_f33}, se buscara en errores')
        archivo_error = archivo_f33.replace('Procesado', 'Errores')
        try:
            comprobante = cons_f33(comprobante, archivo_error, 1)
        except FileNotFoundError as e:
            print(f'{e} | tampoco lo encontramos en errores!')
            logging.error(e)
    finally:
        return comprobante


def leer_archivo(archivo, mes_anio, ruta, agencia):
    print(f'leyendo archivo {archivo}')
    ruta = os.sep.join(ruta)
    tree = ET.parse(os.path.join(ruta, agencia, mes_anio, archivo))
    comprobante = construye_comprobante(tree, archivo)
    ruta_f33 = [
        '\\\\192.168.24.10',
        'E$',
        'CFD',
        'Intercambio',
        'Procesado',
        f'{comprobante.emisor.rfc}',
        mes_anio,
        f'{comprobante.emisor.rfc}-{archivo[:-4]}.F33',
    ]
    archivo_f33 = os.sep.join(ruta_f33)
    comprobante = compl_comp_f33(comprobante, archivo_f33)

    return comprobante


def uno(archivo, mes_anio, ruta, agencia):
    comp = leer_archivo(archivo, mes_anio, ruta, agencia)
    imp = ImpresionComprobante(comp)
    imp.genera_pdf()


def main():
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
        'Notas Hino': 'UA14',
        'Credito': 'UA03',
        'Credito Auto': 'UA60',
        'Servicio': 'UD10',
        'Auto': 'UD06',
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
            if tipo in dar_tipo_impresion(agencia, 'SC'):
                imp = ImpresionServicio(comp)
            elif tipo in dar_tipo_impresion(agencia, 'PG'):
                imp = ImpresionPago(comp)
            elif tipo in dar_tipo_impresion(agencia, 'NV'):
                imp = ImpresionVehiculos(comp)
            else:
                imp = ImpresionComprobante(comp)
            imp.genera_pdf()
        except KeyError as ke:
            logging.error(traceback.print_exc())
            with open('errores.log', '+a', encoding='UTF-8') as log:
                log.write(f'\n [Error] en {agencia}-{archivo_valido} no se '
                          f'encontró {str(ke)}')
            continue
        except Exception as e:
            print(e)
            traceback.print_exc()
            logging.error(f'{agencia}-{archivo_valido} : {e}', exc_info=True)
            continue


if __name__ == '__main__':
    main()
    #uno('01-UA03001-ZN00732.xml', '012020', [r'\\192.168.24.10','e$', 'cfd', 'almacen'], 'AIQ070917FVA')
    logging.info(f'Fin')
