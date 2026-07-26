from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from instagrapi import Client
import uvicorn
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cl = Client()

@app.get("/")
def home():
    return {"status": "ok", "message": "Instagram API Çalışıyor!"}

@app.get("/api/download")
def download_media(url: str):
    try:
        # img_index tespiti
        img_index = 0
        match = re.search(r'img_index=(\d+)', url)
        if match:
            img_index = int(match.group(1)) - 1

        media_pk = cl.media_pk_from_url(url)
        media_info = cl.media_info(media_pk)
        
        download_url = ""
        thumbnail_url = ""
        media_type = "image"

        # Albüm / Kaydırmalı Gönderi
        if media_info.resources and len(media_info.resources) > 0:
            res_list = media_info.resources
            selected = res_list[img_index] if (0 <= img_index < len(res_list)) else res_list[0]
            
            if selected.video_url:
                download_url = str(selected.video_url)
                thumbnail_url = str(selected.thumbnail_url) if selected.thumbnail_url else ""
                media_type = "video"
            else:
                download_url = str(selected.thumbnail_url)
                thumbnail_url = download_url
                media_type = "image"

        # Tekli Video / Reels
        elif media_info.media_type == 2 or media_info.video_url:
            download_url = str(media_info.video_url)
            thumbnail_url = str(media_info.thumbnail_url) if media_info.thumbnail_url else ""
            media_type = "video"

        # Tekli Fotoğraf
        else:
            download_url = str(media_info.thumbnail_url)
            thumbnail_url = download_url
            media_type = "image"

        return {
            "success": True,
            "download_url": download_url,
            "thumbnail_url": thumbnail_url,
            "type": media_type,
            "title": media_info.caption_text[:60] if media_info.caption_text else "Instagram İçeriği"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
