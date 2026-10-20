FROM python:3.12-slim

# Run as a non-root user
RUN useradd --create-home appuser
WORKDIR /app

COPY app/ ./app/
USER appuser

ENV PORT=8080 PYTHONUNBUFFERED=1
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["python", "-m", "app.server"]
