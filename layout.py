from os import startfile

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.colors import Color, black, red
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (Frame, PageTemplate, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

from pagos import Comprobante


class ImpresionPagos:
    def __init__(self, comprobante):
        self._comprobante = comprobante


    def _primera_hoja(self, canvas, document):
        canvas.setAuthor('Enrique Santana')
        canvas.setTitle('Representación impresa CFDI')
        canvas.setSubject('Complemento de Pago')
        canvas.setCreator('ReportLab')
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

        datos_emisor = '''
            <b>ALECSA CAMIONES Y AUTOBUSES S DE RL DE CV</b><br/>
            AV. 5 DE FEBRERO 1708 <br/>
            COL. ZONA INDUSTRIAL BENITO JUAREZ <br/>
            QUERETARO <br/>
            QUERETARO, MEXICO <br/>
            C.P. 76120 <br/>
            R.F.C. ACA080131IL5 <br/>
            Regímen fiscal: 601
        '''
        titulos_receptor = [[
            'Receptor del comprobante', 'Clave:', 'C100381',
        ]]
        datos_receptor = '''
            <font size=8>GALLETAS JUANITA SA DE CV</font><br/><br/>
            CALLE NARCISO MENDOZA SIN NUMERO INT SIN NUMERO<br/>
            COL. AMPLIACION SAN PEDRO ATZOMPA<br/>
            TECAMAC<br/>
            ESTADO DE MEXICO, MEX<br/>
            C.P. 55770<br/>
            R.F.C. GJU040820HU2<br/>
        '''

        titulo_comprobante = 'RECIBO'
        serie_folio = 'RH-00417'
        fecha_emision = '2018-08-01T19:08:09'
        serie_cert_emisor = '00001000000403775746'
        uuid = '1E399AAF-002A-4C84-A00E-74C0718FAF51'
        serie_cert_sat = '00001000000404512308'
        fecha_hora_cert = '2018-08-01T19:08:44'
        lugar_expedicion = '76120'

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
            ['CIENTO CINCUENTA MIL PESOS 00/100 M.N.', '', '', ''],
            ['Forma de pago:', '03 Transferencia electrónica de fondos', '', ''],
            ['Método de pago:', 'PPD Pago en parcialidades o diferido',
                'Número de cuenta:', '0199713662'],
            ['Condiciones:', '', '', ''],
        ]
        info_totales = [
            ['Total:', '$150,000.00'],
        ]
        info_info = [
            ['Sello digital del CFDI:'],
            [Paragraph('JZC9GYMrfJVZU6syt6BjP7xhKdHksWkiL5fxWykpDaKp1aM35PCSZbdOLr'
                       + '64VYPU+KGebWusMZVH8jeTez13wZBm2Bj/m2dlTdxC34BYOzCEIVqFQZ45JEAsW63'
                       + 'lq/Y6Yf2pHxtKit0Nf+k/F5wxH51g0zd9cgr2bxq+8YuH0lNgJMOoVy1gLSJCPyW1'
                       + 'ROsuMvncoVFLTy4SrOiUt+U2EBzLIyG50MGf7+w8YV+FJ+eKsk/kfIdHT/Nwn+oBG'
                       + '9++cpNBo8EDtAZDQk9y', small
                       )],
            ['Sello del SAT:'],
            [Paragraph('hWPZqNXnAXtTsgZYIC3Rv4fDa9itCRM0Hxvv966CrVWbVku7VeOBGs2l+x'
                       + 'Q4S4zTgp9T7FEFAkO93qB/IxreA/hvRkStbW2bGwC5jhxkgh7MlCbiVkHMrSTwZe'
                       + 'w1Wt3ZSU+zCpts0J2hl2f0fVlF/piQOs9R2FvoiPD1S+ZkrEORStX3Fn9IxlD0lI'
                       + '3Azu4DQqJg1VtyZADXxCaikYm9Z5OV7ycDN3PeKpwODm7l12LblAQIAXyVV2tUhj'
                       + 'uJ07wzjEHWX0rT3ayFTepfQUYg', small
                       )],
            ['Cadena original del complemento de certificación digital del SAT:'],
            [Paragraph('||1.1|1E399AAF-002A-4C84-A00E-74C0718FAF51|2018-08-01T19:08'
                       + ':44Z|TLE011122SC2|JZC9GYMrfJVZU6syt6BjP7xhKdHksWkiL5fxWykpDaKp1aM'
                       + '35PCSZbdOLr64VYPU+KGebWusMZVH8jeTez13wZBm2Bj/m2dlTdxC34BYOzCEIVqF'
                       + 'QZ45JEAsW63lq/Y6Yf2pHxtKit0Nf+k/F5wxH51g0zd9cgr2bxq+8YuH0lNgJMOoV'
                       + 'y1gLSJCPyW1ROsuMvncoVFLTy4SrOiUt+U2EBzLIyG50MGf7+w8YV+FJ+eKsk/kfI'
                       + 'dHT/Nwn+oBG9++cpNBo8EDtAZDQk9yvZUILogLsR0QF+0P5oo4L7vnk077JrfNQ8v'
                       + 'kdBgvQI17USKf0mTeJihIsXw2U6F0zQDwzQ==|00001000000404512308||',
                       small
                       )],
        ]

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
        canvas.drawImage(
            'recursos\\logos\\hino-logo1-300x261.jpg',
            7.0556 * mm,
            240.50 * mm,
            width=36.49 * mm,
            height=32.10 * mm
        )
        # Marcos
        canvas.setStrokeColorRGB(1, .208, .149)  # Rojo
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
        para_emisor.drawOn(canvas, 54.55 * mm, 240.04 * mm)
        flowables_cabecera.append(Spacer(0, 36 * mm))
        titulos = Table(
            titulos_receptor,
            colWidths=[
                128.94 * mm, 11.29 * mm, 15.522 * mm
            ]
        )
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
            f'?re=ACA080131IL5&rr=RLI051025J88&tt=6005.390000'
            + f'&id=09E1D1B8-44F5-47AD-B3FC-0762B179CF7D'
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


    def _define_layout(self, comprobante=None):
        documento = SimpleDocTemplate(
            'test.pdf',
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
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
            [
                '89BEF399-FAD5-4457-ACC1-05A1B28A7021',
                'AA1119',
                'MXN',
                'PPD',
                '1',
                '783,232.00',
                '150,000.00',
                '633,232.00'
            ],
        ]
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
            ('SIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ])
        tabla_detalle.setStyle(estilo_tabla_detalle)
        t = tabla_detalle.split(201.79 * mm, 119.94 * mm)
        for x in t:
            flowables.append(x)

        documento.build(flowables, onFirstPage=self._primera_hoja,
                        onLaterPages=self._primera_hoja)


def main():
    impre = ImpresionPagos(None)
    impre._define_layout()
    startfile('test.pdf')


if __name__ == '__main__':
    main()
