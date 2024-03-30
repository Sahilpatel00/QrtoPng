from fastapi import FastAPI, HTTPException, Response, Query
import qrcode
from io import BytesIO
from pydantic import BaseModel
app = FastAPI()

@app.get("/generate_qr_code/")
async def generate_qr_code(json_data: str = Query(None), size: int = Query(None)):
    try:
        # json_data = data.get("json_data")
        # size = data.get("size")

        if not json_data or not size:
            raise HTTPException(status_code=400, detail="JSON data and size are required")

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(json_data)
        qr.make(fit=True)

        img_buffer = BytesIO()
        img = qr.make_image(fill_color="black", back_color="white")

        img = img.resize((size, size))

        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        qr_code_bytes = img_buffer.getvalue()
        return Response(content=qr_code_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
