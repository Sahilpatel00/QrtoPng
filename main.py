from fastapi import FastAPI, HTTPException, Response, Query
import qrcode
from io import BytesIO
from PIL import Image
import urllib.parse

app = FastAPI()

@app.get("/generate_qr_code/")
async def generate_qr_code(
    json_data: str = Query(None),
    size: int = Query(None),
    image_path: str = Query(None)
):
    try:
        if not json_data or not size or not image_path:
            raise HTTPException(status_code=400, detail="JSON data, size, and image path are required")

        # URL-decode the file path
        image_path = urllib.parse.unquote(image_path)

        # Load the image from the provided file path
        img = Image.open(image_path)

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
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Resize the QR code
        qr_img = qr_img.resize((size, size))

        # Calculate the size of the uploaded image to be inserted into the QR code
        logo_size = int(size / 5)  # The logo will take up 1/5th of the QR code size

        # Resize the uploaded image as per the calculated size
        img = img.resize((100, 100))

        # Calculate the position where the image should be inserted
        pos = ((qr_img.size[0] - img.size[0]) // 2, (qr_img.size[1] - img.size[1]) // 2)

        # Insert the image in the center of the QR code
        qr_img.paste(img, pos)

        # Save the QR code with the image to a buffer
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Get the bytes value of the image
        qr_code_bytes = img_buffer.getvalue()

        # Return the image response
        return Response(content=qr_code_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
