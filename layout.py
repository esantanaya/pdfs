# TODO: Agregar el frame de los totales y su flowable
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.graphics.shapes import Rect, Drawing
from reportlab.graphics.barcode import qr
from reportlab.graphics import renderPDF
from reportlab.lib.colors import Color, red, black
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    SimpleDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle
)
from os import startfile


def primera_hoja(canvas, document):
    canvas.setAuthor('Enrique Santana')
    canvas.setTitle('Representación impresa CFDI')
    canvas.setSubject('Complemento de Pago')
    canvas.setCreator('ReportLab')
    cabecera = Frame(
        7.0556*mm,
        207.38*mm,
        width=201.88*mm,
        height=64.56*mm,
        id='Cabecera',
        leftPadding=43.6956*mm
    )
    detalle = Frame(
        7.0556*mm,
        87.01*mm,
        width=201.88*mm,
        height=119.94*mm,
        id='Detalle',
    )
    frame_pie_datos = Frame(
        7.0556*mm,
        69.02*mm,
        width=144.64*mm,
        height=16.93*mm,
        id="PieDatos",
        leftPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    frame_pie_totales = Frame(
        152.3256*mm,
        69.02*mm,
        width=56.44*mm,
        height=16.93*mm,
        id='PieTotales',
        leftPadding=0,
        topPadding=0,
        bottomPadding=0,
    )
    flowables_cabecera = []
    flowables_detalles = []
    flowables_pie_datos = []
    flowables_pie_totales = []
    styles = getSampleStyleSheet()
    small = ParagraphStyle('Pequeña')
    small.fontSize = 7
    small.leading = 7
    small.leftIndent = -120

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
    ]
    estilo_tabla_detalle = TableStyle([
        ('SIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ])
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
        ['Método de pago:', 'PPD Pago en parcialidades o diferido', 'Número de cuenta:', '0199713662'],
        ['Condiciones:', '', '', ''],
    ]

    info_totales = [
        ['Total:', '$150,000.00'],
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

    canvas.saveState()
    canvas.drawImage(
        'recursos\\logos\\hino-logo1-300x261.jpg',
        7.0556*mm,
        240.50*mm,
        width=36.49*mm,
        height=32.10*mm
    )
    #Marcos
    canvas.setStrokeColorRGB(1, .208, .149)#Rojo
    #Marcos Cabecera
    canvas.roundRect(7.0556*mm, 207.58*mm, 155.22*mm, 32.46*mm, 5)
    canvas.roundRect(162.9856*mm, 207.58*mm, 45.86*mm, 64.56*mm, 5)
    #Marco Detalle
    canvas.roundRect(7.0556*mm, 87.01*mm, 201.79*mm, 119.94*mm, 5)
    #Marcos Pie
    canvas.roundRect(7.0556*mm, 69.02*mm, 144.64*mm, 16.93*mm, 5)
    canvas.roundRect(152.3256*mm, 69.02*mm, 56.44*mm, 16.93*mm, 5)
    canvas.roundRect(7.0556*mm, 13.99*mm, 201.79*mm, 54.50*mm, 5)
    canvas.line(7.0556*mm, 13.10*mm, 208.8456*mm, 13.10*mm)

    #Cabecera
    para_emisor = Paragraph(datos_emisor, styles['Normal'])
    para_emisor.wrapOn(canvas, 106*mm, 31*mm)
    para_emisor.drawOn(canvas, 54.55*mm, 240.04*mm)
    # flowables_cabecera.append(para_emisor)
    flowables_cabecera.append(Spacer(0,36*mm))
    titulos = Table(
        titulos_receptor,
        colWidths=[
            128.94*mm, 11.29*mm, 15.522*mm
        ]
    )
    titulos.wrapOn(canvas, 0, 0)
    titulos.drawOn(canvas, 6*mm, 233.86*mm)
    tabla_documento = Table(
        titulos_documento,
        colWidths=45.86*mm,
        rowHeights=4.61*mm,
    )
    tabla_documento.setStyle(estilo_tabla_doc)
    tabla_documento.wrapOn(canvas, 0, 0)
    tabla_documento.drawOn(canvas, 162.9856*mm, 207.58*mm)
    para_receptor = Paragraph(datos_receptor, small)
    flowables_cabecera.append(para_receptor)
    canvas.drawString(178.06*mm, 7.0556*mm,  f'Página {document.page}')
    cabecera.addFromList(flowables_cabecera, canvas)

    #Detalle
    tabla_detalle = Table(lista_detalle)
    tabla_detalle.setStyle(estilo_tabla_detalle)
    flowables_detalles.append(tabla_detalle)
    detalle.addFromList(flowables_detalles, canvas)

    #Pie
    tabla_pie = Table(
        info_extra,
        colWidths=[
            25.41*mm,
            65.99*mm,
            28.23*mm,
            25*mm,
        ]
    )
    tabla_pie.setStyle(estilo_tabla_info)
    tabla_pie.vAlign = 'TOP'
    tabla_pie.hAlign = 'LEFT'
    flowables_pie_datos.append(tabla_pie)
    frame_pie_datos.addFromList(flowables_pie_datos, canvas)

    tabla_totales = Table(
        info_totales,
        colWidths=[32.59*mm, 23.85*mm]
    )
    tabla_totales.setStyle(estilo_tabla_totales)
    tabla_totales.vAlign = 'TOP'
    tabla_totales.hAlign = 'LEFT'
    flowables_pie_totales.append(tabla_totales)
    frame_pie_totales.addFromList(flowables_pie_totales, canvas)

    #QR
    qr_code = qr.QrCodeWidget(
        f'?re=ACA080131IL5&rr=RLI051025J88&tt=6005.390000'
        + f'&id=09E1D1B8-44F5-47AD-B3FC-0762B179CF7D'
    )
    qr_code.barWidth = 30*mm
    qr_code.barHeight = 30*mm
    qr_code.qrVersion = 1
    d = Drawing()
    d.add(qr_code)
    renderPDF.draw(d, canvas, 8*mm, 37*mm)

    #Líneas Grises punteadas
    canvas.setStrokeColorRGB(.80, .80, .80)#Gris Claro
    canvas.setDash([0.5*mm,0.5*mm], 0)
    #Líneas Grises punteadas Cabecera
    canvas.line(7.0556*mm, 233.86*mm, 162.2756*mm, 233.86*mm)
    canvas.line(135.9956*mm, 240.04*mm, 135.9956*mm, 233.86*mm)
    canvas.line(147.2856*mm, 240.04*mm, 147.2856*mm, 233.86*mm)
    y_factura = 212.34*mm
    canvas.line(162.9856*mm, y_factura, 208.8456*mm, y_factura)
    for _ in range(12):
        y_factura += 4.59*mm
        canvas.line(162.9856*mm, y_factura, 208.8456*mm, y_factura)
    #Líneas Grises punteadas Detalle
    canvas.line(7.0556*mm, 199.37*mm, 208.8456*mm, 199.37*mm)

    canvas.restoreState()


def define_layout(logo=None, comprobante=None):
    documento = SimpleDocTemplate(
        'test.pdf',
        pagesize=letter,
        rightMargin=7.0556*mm,
        leftMargin=7.0556*mm,
        topMargin=7.0556*mm,
        bottomMargin=7.0556*mm,
    )
    styles = getSampleStyleSheet()
    flowables = []
    p = Paragraph('', styles['Normal'])
    flowables.append(p)

    documento.build(flowables, onFirstPage=primera_hoja)



def main():
    define_layout()
    startfile('test.pdf')

if __name__ == '__main__':
    main()
