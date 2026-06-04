FROM python:3.12-slim
WORKDIR /app
COPY requirements-dev.txt ./requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
CMD ["python", "services/runner/run_task.py"]
