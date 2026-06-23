FROM python:3.12-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install mp4decrypt (Bento4)
RUN wget -q https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip \
    -O /tmp/bento4.zip \
    && unzip /tmp/bento4.zip -d /tmp/bento4 \
    && cp /tmp/bento4/Bento4-SDK-1-6-0-641.x86_64-unknown-linux/bin/mp4decrypt /usr/local/bin/ \
    && chmod +x /usr/local/bin/mp4decrypt \
    && rm -rf /tmp/bento4 /tmp/bento4.zip

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create downloads directory
RUN mkdir -p downloads

EXPOSE 8080

CMD ["python", "modules/main.py"]
