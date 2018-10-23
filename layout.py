from os import sep
from re import match

from pagos import Comprobante
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import red
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Frame, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)


class ImpresionPagos:
    def __init__(self, comprobante):
        self._comprobante = comprobante
        self._ruta_logos = ''
        self._archivo_logo = ''
        self._codigo_color_lineas = ''

    @property
    def comprobante(self):
        return self._comprobante

    @comprobante.setter
    def comprobante(self, comprobante):
        self._comprobante = comprobante

    @property
    def ruta_logos(self):
        return self._ruta_logos

    @ruta_logos.setter
    def ruta_logos(self, ruta_logos):
        self._ruta_logos = ruta_logos

    @property
    def archivo_logo(self):
        return self._archivo_logo

    @archivo_logo.setter
    def archivo_logo(self, archivo_logo):
        self._archivo_logo = archivo_logo

    @property
    def codigo_color_lineas(self):
        return self._codigo_color_lineas

    @codigo_color_lineas.setter
    def codigo_color_lineas(self, codigo_color_lineas):
        self._codigo_color_lineas = codigo_color_lineas

    def _lee_ini(self):
        with open('layout.ini') as config:
            bandera = ''
            for linea in config:
                linea = linea.strip()
                if linea.startswith('[') and linea.endswith(']'):
                    titulo = linea[1:-1]
                    if titulo == 'Configuracion':
                        bandera = 'conf'
                    elif match(r'^[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}', titulo):
                        bandera = 'emisor'
                elif '=' in linea:
                    llave, valor = linea.split('=')
                    if bandera == 'conf':
                        if llave == 'ruta_logos':
                            self._ruta_logos = valor.split('|')
                    elif (bandera == 'emisor'
                          and titulo == self._comprobante.emisor.rfc):
                        if llave == 'CN':
                            self._comprobante.emisor.calle_numero = valor
                        elif llave == 'C':
                            self._comprobante.emisor.colonia = valor
                        elif llave == 'CD':
                            self._comprobante.emisor.ciudad = valor
                        elif llave == 'EP':
                            self._comprobante.emisor.estado_pais = valor
                        elif llave == 'CP':
                            self._comprobante.emisor.codigo_postal = valor
                        elif llave == 'LG':
                            self._archivo_logo = valor
                        elif llave == 'CL':
                            self._codigo_color_lineas = valor

    def _primera_hoja(self, canvas, document):
        canvas.setAuthor('Enrique Santana')
        canvas.setTitle('Representación impresa CFDI')
        canvas.setSubject('Complemento de Pago')
        canvas.setCreator('ReportLab')
        emisor = self._comprobante.emisor
        receptor = self._comprobante.receptor
        rojo, verde, azul = self._codigo_color_lineas[1:-1].split(',')
        cabecera = Frame(
            7.0556 * mm,
            207.38 * mm,
            width=201.88 * mm,
            height=64.56 * mm,
            id='Cabecera',
            leftPadding=43.6956 * mm
        )
        frame_pie_datos = Frame(
            7.0556 * mm,
            69.02 * mm,
            width=144.64 * mm,
            height=16.93 * mm,
            id="PieDatos",
            leftPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        frame_pie_totales = Frame(
            152.3256 * mm,
            69.02 * mm,
            width=56.44 * mm,
            height=16.93 * mm,
            id='PieTotales',
            leftPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        frame_pie_info = Frame(
            38.3256 * mm,
            13.99 * mm,
            width=170.52 * mm,
            height=54.50 * mm,
            id='PieInfo',
            leftPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        flowables_cabecera = []
        flowables_pie_datos = []
        flowables_pie_totales = []
        flowables_pie_info = []
        styles = getSampleStyleSheet()
        small = ParagraphStyle('Pequeña')
        small.fontSize = 7
        small.leading = 7
        small.splitLongWords = True
        small.spaceShrinkage = 0.05

        datos_emisor = (f'<b>{emisor.nombre}</b><br/><para leading=8>'
                        + f'<font size=8>{emisor.calle_numero}<br/>'
                        + f'COL. {emisor.colonia}<br/>'
                        + f'{emisor.ciudad}<br/>{emisor.estado_pais}<br/>'
                        + f'C.P. {emisor.codigo_postal}<br/>'
                        + f'R.F.C. {emisor.rfc}<br/>'
                        + f'Regímen fiscal: {emisor.regimen_fiscal}</font>')

        titulos_receptor = [[
            'Receptor del comprobante', 'Clave:',
            self._comprobante.receptor.clave,
        ]]
        datos_receptor = (f'<font size=8>{receptor.nombre}</font><br/><br/>'
                          + f'{receptor.calle}<br/>COL. {receptor.colonia}<br/>'
                          + f'{receptor.municipio}<br/>'
                          + f'{receptor.estado}, {receptor.pais}<br/>'
                          + f'C.P. {receptor.codigo_postal}<br/>'
                          + f'R.F.C. {receptor.rfc}<br/>')

        titulo_comprobante = 'PAGO'
        serie_folio = f'{self._comprobante.serie}-{self._comprobante.folio}'
        fecha_emision = self._comprobante.fecha
        serie_cert_emisor = self._comprobante.no_certificado
        uuid = self._comprobante.timbre.uuid
        serie_cert_sat = self._comprobante.timbre.no_certificado_sat
        fecha_hora_cert = self._comprobante.timbre.fecha_timbrado
        lugar_expedicion = self._comprobante.lugar_expedicion

        titulos_documento = [
            [titulo_comprobante],
            [serie_folio],
            ['Fecha de emisión del CFDI'],
            [fecha_emision],
            ['No. serie certificado emisor'],
            [serie_cert_emisor],
            ['Folio fiscal'],
            [uuid],
            ['No. serie certificado SAT'],
            [serie_cert_sat],
            ['Fecha y hora de certificación'],
            [fecha_hora_cert],
            ['Lugar expedición'],
            [lugar_expedicion],
        ]
        info_extra = [
            [self._comprobante.total_letra, '', '', ''],
            ['Forma de pago:', self._comprobante.pagos[0].forma_pago_p,
                'Unidad de Medida:', self._comprobante.concepto.clave_unidad],
            ['Uso de CFDI:', self._comprobante.receptor.uso_cfdi,
                'Clave de Producto:', self._comprobante.concepto.clave_prod_serv],
            ['Condiciones:', '', '', ''],
        ]
        info_totales = [
            ['Total:', f'${self._comprobante.pagos[0].monto}'],
        ]
        info_info = [
            ['Sello digital del CFDI:'],
            [Paragraph(self._comprobante.timbre.sello_cfd, small)],
            ['Sello del SAT:'],
            [Paragraph(self._comprobante.timbre.sello_sat, small)],
            ['Cadena original del complemento de certificación digital del SAT:'],
            [Paragraph(self._comprobante.timbre.cadena_original, small)],
        ]

        estilo_tabla_titulos = TableStyle([
            ('LEFTPADDING', (1, 0), (-1, -1), 4),
        ])
        estilo_tabla_doc = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 1), (0, 1), red),
            ('SIZE', (0, 7), (0, 7), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 7), (0, 7), 8),
        ])
        estilo_tabla_info = TableStyle([
            ('SIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 5.7),
            ('SPAN', (0, 0), (3, 0)),
        ])
        estilo_tabla_totales = TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ])
        estilo_tabla_info_qr = TableStyle([
            ('SIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 5.7),
        ])
        canvas.saveState()
        ruta_logo = sep.join(self._ruta_logos) + sep + self._archivo_logo
        canvas.drawImage(
            ruta_logo,
            7.0556 * mm,
            240.50 * mm,
            width=36.49 * mm,
            height=32.10 * mm
        )
        # Marcos
        canvas.setStrokeColorRGB(float(rojo), float(verde), float(azul))
        # Marcos Cabecera
        canvas.roundRect(7.0556 * mm, 207.58 * mm, 155.22 * mm, 32.46 * mm, 5)
        canvas.roundRect(162.9856 * mm, 207.58 * mm, 45.86 * mm, 64.56 * mm, 5)
        # Marco Detalle
        canvas.roundRect(7.0556 * mm, 87.01 * mm, 201.79 * mm, 119.94 * mm, 5)
        # Marcos Pie
        canvas.roundRect(7.0556 * mm, 69.02 * mm, 144.64 * mm, 16.93 * mm, 5)
        canvas.roundRect(152.3256 * mm, 69.02 * mm, 56.44 * mm, 16.93 * mm, 5)
        canvas.roundRect(7.0556 * mm, 13.99 * mm, 201.79 * mm, 54.50 * mm, 5)
        canvas.line(7.0556 * mm, 13.10 * mm, 208.8456 * mm, 13.10 * mm)

        # Cabecera
        para_emisor = Paragraph(datos_emisor, styles['Normal'])
        para_emisor.wrapOn(canvas, 106 * mm, 31 * mm)
        para_emisor.drawOn(canvas, 49.55 * mm, 247 * mm)
        flowables_cabecera.append(Spacer(0, 36 * mm))
        titulos = Table(
            titulos_receptor,
            colWidths=[
                128.94 * mm, 11.29 * mm, 15.522 * mm
            ],
        )
        titulos.setStyle(estilo_tabla_titulos)
        titulos.wrapOn(canvas, 0, 0)
        titulos.drawOn(canvas, 6 * mm, 233.86 * mm)
        tabla_documento = Table(
            titulos_documento,
            colWidths=45.86 * mm,
            rowHeights=4.61 * mm,
        )
        tabla_documento.setStyle(estilo_tabla_doc)
        tabla_documento.wrapOn(canvas, 0, 0)
        tabla_documento.drawOn(canvas, 162.9856 * mm, 207.58 * mm)
        para_receptor = Paragraph(datos_receptor, small)
        para_receptor.wrapOn(canvas, 155.22 * mm, 26.28 * mm)
        para_receptor.drawOn(canvas, 7.5 * mm, 212.58 * mm)
        cabecera.addFromList(flowables_cabecera, canvas)

        # Pie
        tabla_pie = Table(
            info_extra,
            colWidths=[
                25.41 * mm,
                65.99 * mm,
                28.23 * mm,
                25 * mm,
            ]
        )
        tabla_pie.setStyle(estilo_tabla_info)
        tabla_pie.vAlign = 'TOP'
        tabla_pie.hAlign = 'LEFT'
        flowables_pie_datos.append(tabla_pie)
        frame_pie_datos.addFromList(flowables_pie_datos, canvas)

        tabla_totales = Table(
            info_totales,
            colWidths=[32.59 * mm, 23.85 * mm]
        )
        tabla_totales.setStyle(estilo_tabla_totales)
        tabla_totales.vAlign = 'TOP'
        tabla_totales.hAlign = 'LEFT'
        flowables_pie_totales.append(tabla_totales)
        frame_pie_totales.addFromList(flowables_pie_totales, canvas)

        tabla_info = Table(
            info_info,
            colWidths=170.52 * mm,
        )
        tabla_info.setStyle(estilo_tabla_info_qr)
        flowables_pie_info.append(tabla_info)
        frame_pie_info.addFromList(flowables_pie_info, canvas)

        # QR
        qr_code = qr.QrCodeWidget(
            f'?re={emisor.rfc}&rr={self._comprobante.receptor.rfc}'
            + f'&tt={self._comprobante.total}&id={self._comprobante.timbre.uuid}'
        )
        qr_code.barWidth = 30 * mm
        qr_code.barHeight = 30 * mm
        qr_code.qrVersion = 1
        d = Drawing()
        d.add(qr_code)
        renderPDF.draw(d, canvas, 8 * mm, 37 * mm)

        # Líneas Grises punteadas
        canvas.setStrokeColorRGB(.80, .80, .80)  # Gris Claro
        canvas.setDash([0.5 * mm, 0.5 * mm], 0)
        # Líneas Grises punteadas Cabecera
        canvas.line(7.0556 * mm, 233.86 * mm, 162.2756 * mm, 233.86 * mm)
        canvas.line(135.9956 * mm, 240.04 * mm, 135.9956 * mm, 233.86 * mm)
        canvas.line(147.2856 * mm, 240.04 * mm, 147.2856 * mm, 233.86 * mm)
        y_factura = 212.34 * mm
        canvas.line(162.9856 * mm, y_factura, 208.8456 * mm, y_factura)
        for _ in range(12):
            y_factura += 4.59 * mm
            canvas.line(162.9856 * mm, y_factura, 208.8456 * mm, y_factura)
        # Líneas Grises punteadas Detalle
        canvas.line(7.0556 * mm, 199.37 * mm, 208.8456 * mm, 199.37 * mm)

        canvas.restoreState()

    def _define_layout(self):
        documento = SimpleDocTemplate(
            self._comprobante.nombre_archivo[:-4] + '.pdf',
            pagesize=letter,
            rightMargin=7.0556 * mm,
            leftMargin=7.0556 * mm,
            topMargin=72.55 * mm,
            bottomMargin=86.79 * mm,
        )
        styles = getSampleStyleSheet()
        flowables = []
        lista_detalle = [
            [
                'Pago correspondiente a: Folio Fiscal',
                'Folio y Serie',
                'Moneda',
                'Met. Pago',
                'N° Parc.',
                'Saldo Ant.',
                'Imp. Pagado',
                'Saldo Insoluto',
            ],
        ]
        for pago in self._comprobante.pagos:
            fila = [
                pago.docto_relacionado.id_documento,
                (pago.docto_relacionado.serie
                 + pago.docto_relacionado.folio),
                pago.docto_relacionado.moneda_dr,
                pago.docto_relacionado.metodo_pago_dr,
                pago.docto_relacionado.num_parcialidad,
                pago.docto_relacionado.imp_saldo_ant,
                pago.docto_relacionado.imp_pagado,
                pago.docto_relacionado.imp_saldo_insoluto,
            ]
            lista_detalle.append(fila)
        # Detalle
        tabla_detalle = Table(
            lista_detalle,
            colWidths=[
                65.73 * mm,
                22.07 * mm,
                14.56 * mm,
                17.40 * mm,
                13.77 * mm,
                19.24 * mm,
                22.06 * mm,
                24.89 * mm,
            ],
            repeatRows=1,
        )
        estilo_tabla_detalle = TableStyle([
            ('SIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ])
        tabla_detalle.setStyle(estilo_tabla_detalle)
        t = tabla_detalle.split(201.79 * mm, 119.94 * mm)
        for x in t:
            flowables.append(x)

        documento.build(flowables, onFirstPage=self._primera_hoja,
                        onLaterPages=self._primera_hoja)

    def genera_pdf(self):
        self._lee_ini()
        self._define_layout()
