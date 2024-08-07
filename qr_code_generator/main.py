import base64
import qrcode
import uuid

from fasthtml.common import *
from io import BytesIO

from settings import THEME

app, route = fast_app(live=True)


@route('/')
def get():
    return(
        Header(
            Link(
                rel='stylesheet', 
                href=(
                    'https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.'
                    f'{THEME}.min.css'),
            )
        ),
        Container(
            Titled('QR Generator'),
            Form(
                Input(type='text', name='data'),
                Button(
                    'Generate', 
                    hx_post='/generate_qr', 
                    hx_target='#qr_container', 
                    hx_swap='innerHTML',
                ),
                method='POST',
            ),
            Card(
                Body(
                    Div(
                        '', 
                        id='qr_container', 
                        style='text-align: center',
                    ),
                ),
                style='margin-top: 1em',
            ),
        )
    )


@route('/generate_qr')
async def post(request):
    form = await request.form()

    if not form.get('data'):
        return

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(form.get('data'))
    qr.make(fit=True)
    
    # Create an image from the QR code instance
    img = qr.make_image(fill='black', back_color='white')
    
    # Save the image to a BytesIO object
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    
    # Encode the image as a Base64 string
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return (
        Div(
            Img(src=f'data:image/png;base64,{img_str}', alt='QR Code'),
        ),
        Div(
            Span(
                A(
                    Button('Download'),
                    href=f'data:image/png;base64,{img_str}',
                    download=f'{str(uuid.uuid4()).split("-")[0]}.png',
                    target='_blank',
                )
            )
        )

    )


serve()