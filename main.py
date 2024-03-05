from fastapi import FastAPI, UploadFile, File, Response
from fastapi.responses import JSONResponse, FileResponse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from fastapi.middleware.cors import CORSMiddleware
import os
from prepro import process_file
import time
import shutil
import zipfile

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow CORS from this domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileWatcher(FileSystemEventHandler):
    def __init__(self, source_dir, target_dir):
        self.source_dir = source_dir
        self.target_dir = target_dir

    def on_created(self, event):
        print(f"New file {event.src_path} has been created.")
        if event.src_path.endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.wav', '.mp3', '.aac', '.flac', '.ogg', '.wma')):
            file_name = os.path.basename(event.src_path)
            # Wait for the file to be fully written
            time.sleep(3)
            try:
                # Delete all files inside target_path directory if it is not empty
                for filename in os.listdir(self.target_dir):
                    file_path = os.path.join(self.target_dir, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f'Failed to delete {file_path}. Reason: {e}')
                process_file(self.source_dir, self.target_dir, file_name)
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

# Define the save path and start the file watcher
save_path = "/app/source"
target_path = "/app/data"
os.makedirs(save_path, exist_ok=True)
event_handler = FileWatcher(save_path, target_path)
observer = Observer()
observer.schedule(event_handler, save_path, recursive=False)
observer.start()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(save_path, exist_ok=True)
    try:
        # Delete all files inside save_path directory if it is not empty
        for filename in os.listdir(save_path):
            file_path = os.path.join(save_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        with open(os.path.join(save_path, file.filename), 'wb') as fileobj:
            content = await file.read()
            fileobj.write(content)
        return JSONResponse(content={"filename": file.filename}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/files")
async def list_files():
    files = os.listdir(target_path)
    return JSONResponse(content={"files": files}, status_code=200)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(target_path, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)

# @app.get("/download/all")
# async def download_all_files():
#     # Create a zip file
#     zip_file_path = os.path.join(target_path, "all_files.zip")
#     with zipfile.ZipFile(zip_file_path, 'w') as zipf:
#         for file in os.listdir(target_path):
#             file_path = os.path.join(target_path, file)
#             if os.path.isfile(file_path):
#                 zipf.write(file_path, arcname=file)

#     # Send the zip file as a response
#     if os.path.exists(zip_file_path):
#         return FileResponse(zip_file_path)
#     else:
#         return JSONResponse(content={"error": "File not found"}, status_code=404)