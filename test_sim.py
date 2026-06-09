import cv2
import numpy as np
from typing import Tuple

def simulate_sentinel_bands(
    height: int = 256,
    width: int = 256,
    stress_fraction: float = 0.25,
    seed: int | None = None,
    commodity: str = "soja",
    variation_factor: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    red_img = np.full((height, width), 130, dtype=np.uint8)
    nir_img = np.full((height, width), 100, dtype=np.uint8)
    vf = max(0.2, min(2.0, variation_factor))
    
    if commodity == "soja":
        for _ in range(rng.integers(2, 5)):
            x, y = rng.integers(5, width-50), rng.integers(5, height-50)
            w, h = rng.integers(int(80*vf), int(160*vf)), rng.integers(int(80*vf), int(160*vf))
            cv2.rectangle(red_img, (int(x), int(y)), (int(x + w), int(y + h)), int(rng.integers(50, 75)), -1)
            cv2.rectangle(nir_img, (int(x), int(y)), (int(x + w), int(y + h)), int(rng.integers(180, 220)), -1)
        if rng.random() > 0.3:
            cx, cy = rng.integers(100, width-50), rng.integers(100, height-50)
            radius = rng.integers(int(40*vf), int(80*vf))
            cv2.circle(red_img, (int(cx), int(cy)), int(radius), 45, -1)
            cv2.circle(nir_img, (int(cx), int(cy)), int(radius), 230, -1)
    elif commodity == "milho":
        angle_deg = float(rng.uniform(-15, 15))
        line_spacing = rng.integers(int(20*vf), int(45*vf))
        line_width = rng.integers(int(10*vf), int(25*vf))
        temp_red = np.full((height*2, width*2), 130, dtype=np.uint8)
        temp_nir = np.full((height*2, width*2), 100, dtype=np.uint8)
        for i in range(0, width*2, int(line_spacing)):
            cv2.line(temp_red, (i, 0), (i, height*2), int(rng.integers(70, 110)), int(line_width))
            cv2.line(temp_nir, (i, 0), (i, height*2), int(rng.integers(140, 180)), int(line_width))
        M = cv2.getRotationMatrix2D((width, height), angle_deg, 1.0)
        red_img = cv2.warpAffine(temp_red, M, (width, height))
        nir_img = cv2.warpAffine(temp_nir, M, (width, height))
    elif commodity == "cafe":
        cx, cy = rng.integers(int(width*0.3), int(width*0.7)), rng.integers(int(height*0.3), int(height*0.7))
        angle_offset = rng.integers(0, 360)
        for radius in range(20, int(width*1.2), rng.integers(int(20*vf), int(40*vf))):
            angle = int(angle_offset + rng.integers(-10, 10))
            cv2.ellipse(red_img, (int(cx), int(cy)), (int(radius), int(radius*0.7)), angle, 0, 360, 50, int(rng.integers(8, 16)))
            cv2.ellipse(nir_img, (int(cx), int(cy)), (int(radius), int(radius*0.7)), angle, 0, 360, 220, int(rng.integers(8, 16)))
    elif commodity == "boi":
        for _ in range(rng.integers(1, 4)):
            num_pts = rng.integers(6, 12)
            cx, cy = rng.integers(30, width-30), rng.integers(30, height-30)
            rad = rng.integers(30, 100)
            pts = []
            for _ in range(num_pts):
                pts.append([rng.integers(cx-rad, cx+rad), rng.integers(cy-rad, cy+rad)])
            pts = np.array(pts, np.int32)
            pts = cv2.convexHull(pts)
            cv2.fillPoly(red_img, [pts], int(rng.integers(70, 90)))
            cv2.fillPoly(nir_img, [pts], int(rng.integers(160, 200)))
        for _ in range(rng.integers(1, 4)):
            cx, cy = rng.integers(20, width-20), rng.integers(20, height-20)
            cv2.circle(red_img, (int(cx), int(cy)), int(rng.integers(15, 45)), 130, -1)
            cv2.circle(nir_img, (int(cx), int(cy)), int(rng.integers(15, 45)), 110, -1)
    
    red = red_img.astype(np.float32)
    nir = nir_img.astype(np.float32)
    noise = rng.integers(0, 255, (height, width), dtype=np.uint8)
    blob = cv2.GaussianBlur(noise, (111, 111), 0).astype(np.float32)
    blob_norm = (blob - blob.min()) / (blob.max() - blob.min() + 1e-6)
    stress_mag = 50 + (stress_fraction * 150)
    red = np.clip(red + (blob_norm * stress_mag * vf), 0, 255)
    nir = np.clip(nir - (blob_norm * stress_mag * 1.5 * vf), 0, 255)
    return red, nir

simulate_sentinel_bands(commodity='soja')
simulate_sentinel_bands(commodity='milho')
simulate_sentinel_bands(commodity='cafe')
simulate_sentinel_bands(commodity='boi')
print("All passed!")
