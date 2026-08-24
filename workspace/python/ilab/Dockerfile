FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements-web.txt .
RUN pip install --no-cache-dir --user -r requirements-web.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/')"

# Exactly 1 worker — session/quiz state is in-memory and process-local
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8001", "--timeout", "120", "wsgi:application"]
