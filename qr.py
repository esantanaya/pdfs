import qrcode

img = qrcode.make('?re=ACA080131IL5&rr=RLI051025J88&tt=6005.390000&id=09E1D1B8-44F5-47AD-B3FC-0762B179CF7D')
img.save('qr.png', format='png')
