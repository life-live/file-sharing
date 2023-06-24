import hashlib
import os
import uuid
import zipfile
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse

app = FastAPI()

if not os.path.isdir("files"):
    os.mkdir("files")


@app.get("/")
async def root():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Form</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
            }
            form {
                background-color: #fff;
                border-radius: 5px;
                padding: 20px;
                margin: 20px auto;
                width: 50%;
            }
            input[type=text] {
                padding: 10px;
                border-radius: 5px;
                border: 2px solid #000000; 
                box-shadow: 1px 1px 5px rgba(0,0,0,.2);
                margin-bottom: 20px;
            }
            button[type=submit] {
                background-color: #4CAF50;
                color: #fff;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
                cursor: pointer;
            }
            .upload input[type="file"] {
                background-color: #4CAF50;
                color: #fff;
                padding: 10px 20px;
                border-radius: 5px;
                border: 2px solid #000000; 
                cursor: pointer;
            }
            .upload input[type="file"]::file-selector-button {
                background-color: #4CAF50;
                color: #fff;
                padding: 10px 20px;
                border-radius: 5px;
                border: 2px solid #000000; 
                cursor: pointer;
                transition: 1s;
            }
            .upload input[type="file"]::file-selector-button:hover {
                background-color: #00723E;
                color: #fff;
                padding: 10px 20px;
                border-radius: 5px;
                border: 2px solid #FFFFFF; 
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <form class="upload" action="/upload" enctype="multipart/form-data" method="post">
            <input name="files" type="file" multiple>
            <button type="submit">Upload Files</button>
        </form>
        <form action="/download" method="post">
            <input name="file_id" type="text">
            <button type="submit">Download Files</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=content)


@app.post("/upload")
async def upload(files: Annotated[list[UploadFile], File(description="Multiple files as UploadFile")]):
    if files[0].filename == "":
        return {"message": "You have not added files"}

    file_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    with zipfile.ZipFile(f"files/{file_id}.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            with archive.open(file.filename, "w") as f:
                while contents := await file.read(1024 * 1024):
                    f.write(contents)
            await file.close()
    return {"message": f"Successfully uploaded {len(files)} files, their ID: {file_id}"}


@app.post("/download")
async def download(request: Request):
    form_data = await request.form()
    file_id = form_data["file_id"]
    return FileResponse(path=f"files/{file_id}.zip", filename=f"{file_id}.zip")


if __name__ == "__main__":
    uvicorn.run(app)
