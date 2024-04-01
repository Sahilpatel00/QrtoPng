from fastapi import FastAPI, HTTPException, Response, Query
import qrcode
from io import BytesIO
from PIL import Image
import requests
import os
app = FastAPI()

def generate_qr_with_logo(json_data: dict, size: int):
    # Convert JSON data to string
    json_str = json_data
    # Load logo image
    logo_path = "logo.jpeg"  # Replace with your logo path
    logo = Image.open(logo_path)
    basewidth = 100
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize))
    # Generate QR code
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1
    )
    qr.add_data(json_str)
    qr.make(fit=True)
    # Create QR code image
    img_buffer = BytesIO()
    qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    qr_image = qr_image.resize((size, size))
    # Calculate the position to put the logo
    position = ((qr_image.size[0] - logo.size[0]) // 2, (qr_image.size[1] - logo.size[1]) // 2)

    qr_image.paste(logo, position)
    qr_image.save(img_buffer, format="PNG")
    return img_buffer.getvalue()

@app.get("/generate_qr_code/")
async def generate_qr_code(json_data: str = Query(None), size: int = Query(None)):
    qr_code_bytes = generate_qr_with_logo(json_data, size)
    return Response(content=qr_code_bytes, media_type="image/png")
