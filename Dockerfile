FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends swi-prolog \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser \
 && chown -R appuser:appuser /app

USER appuser

CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0