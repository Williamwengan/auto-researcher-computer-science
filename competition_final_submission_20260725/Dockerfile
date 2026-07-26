FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Runtime dependencies used by the demo backend and the optional IAD scaffold.
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    scikit-learn \
    pillow \
    openpyxl \
    pyyaml

COPY . /app

EXPOSE 8902

CMD ["python", "03_demo_video/demo_assets/start_demo_server.py", "--host", "0.0.0.0", "--port", "8902", "--strict-port"]
