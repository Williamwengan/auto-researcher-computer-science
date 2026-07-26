FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install --no-cache-dir \
    numpy \
    pandas \
    scikit-learn \
    pillow \
    openpyxl \
    pyyaml

COPY . /app

EXPOSE 8902

CMD ["python", "demo_assets/start_demo_server.py", "--host", "0.0.0.0", "--port", "8902", "--strict-port"]
