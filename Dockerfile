FROM python:3.10-bullseye

# Node.js 19 is deprecated too, but you can still install it manually
RUN curl -fsSL https://deb.nodesource.com/setup_19.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir -U -r requirements.txt

CMD bash start
