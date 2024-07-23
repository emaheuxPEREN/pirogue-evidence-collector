import qrcode


class QRCodeGenerator:
    def __init__(self, url):
        self.url = url

    def generate(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            border=2,
        )
        qr.add_data(self.url)
        qr.print_ascii()

