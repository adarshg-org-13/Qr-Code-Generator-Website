from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
import io
from PIL import Image

app = FastAPI(title="Qr Code Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"], 
)

def hex_to_rgb(hex_color:str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2],16) for i in (0,2,4))

@app.get("/")
def root():
    return {"message":"API Is Running!"}

@app.get("/generate")
def generate_qr(
    text:              str = Query(...,description="Text or URL to encode"),
    size:              int = Query(10,ge=1,le=40,description="Qr Code box size (1 to 40)"),
    border:            int = Query(4,ge=0,le=10,description="Border Size"),
    fg_color:          str = Query("000000",description="Foreground Color (hex)"),
    bg_color:          str = Query("FFFFFF",description="Background Color (hex)"),
    style:             str = Query("Square",description="Style: square, rounded, circle"),
    error_correction:  str = Query("M",description="Error Correction level: L,M,Q,H"),
):
    
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    ec_level = ec_map.get(error_correction.upper(),qrcode.constants.ERROR_CORRECT_M)

    style_map = {
        "rounded": RoundedModuleDrawer(),
        "circle":  CircleModuleDrawer(),
        "square":  SquareModuleDrawer(),
    }
    drawer=style_map.get(style.lower(),SquareModuleDrawer())

    fg_rgb = hex_to_rgb(fg_color)
    bg_rgb = hex_to_rgb(bg_color)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_level,
        box_size=size,
        border=border,
    )

    qr.add_data(text)
    qr.make(fit=True)


    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=drawer,
        color_mask=SolidFillColorMask(
            front_color=fg_rgb,
            back_color=bg_rgb,
        ),
    )

    buf= io.BytesIO()
    img.save(buf,format="PNG")
    buf.seek(0)

    return StreamingResponse(buf,media_type="image/png")