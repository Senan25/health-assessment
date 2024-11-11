FROM python:3.8.5-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "runner:app" ,"--host", "0.0.0.0", "--port", "8000"]
