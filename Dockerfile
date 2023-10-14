FROM python:3.8
MAINTAINER jacketex894

Run pip install --upgrade pip 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
Run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y