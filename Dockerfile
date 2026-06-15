# SWE Study Guide web app image (automation#356).
#
# Built on the VPS by the automation container_service role (external-repo mode)
# and pushed to ECR. Stateless: the study-guide content is baked in and served
# by Python's stdlib http.server (serve.py); no S3, DB, or secrets.

FROM python:3.12-slim AS runtime
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8088
HEALTHCHECK --interval=30s --timeout=5s \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8088/health')"]
CMD ["python", "serve.py", "--host", "0.0.0.0", "--port", "8088"]
