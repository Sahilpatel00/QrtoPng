from fastapi import FastAPI, HTTPException, Response, Query
import qrcode
from io import BytesIO
from PIL import Image
import requests
import os

app = FastAPI()

def generate_qr_code_with_image(json_data: str, size: int, image_path: str) -> bytes:
    try:
        if not json_data or not size:
            raise HTTPException(status_code=400, detail="JSON data and size are required")

        # Create a QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.add_data(json_data)
        qr.make(fit=True)

        # Create an image from the QR Code instance
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Resize the QR code
        img = img.resize((size, size))

        # Load the image
        if image_path.startswith("http"):
            # Download image from URL
            response = requests.get(image_path)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Failed to download image from URL")
            image_data = BytesIO(response.content)
            logo = Image.open(image_data)
        else:
            # Open local image file
            if not os.path.isfile(image_path):
                raise HTTPException(status_code=404, detail="Image file not found")
            logo = Image.open(image_path)

        # Calculate the size of the image to be inserted
        logo_size = int(size / 5)  # The logo will take up 1/5th of the QR code size

        # Resize the logo as per the calculated size
        logo = logo.resize((100, 100))

        # Calculate the position where the image should be inserted
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)

        # Insert the image in the center of the QR code
        img.paste(logo, pos)

        # Save the QR code with the image to a buffer
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Get the bytes value of the image
        qr_code_bytes = img_buffer.getvalue()

        return qr_code_bytes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate_qr_code/")
async def generate_qr_code(json_data: str = Query(None), size: int = Query(None), image_path: str = Query(None)):
    qr_code_bytes = generate_qr_code_with_image(json_data, size, image_path)
    return Response(content=qr_code_bytes, media_type="image/png")
