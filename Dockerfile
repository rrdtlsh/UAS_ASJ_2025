# 1. Gunakan base image Python
FROM python:3.9-slim

# 2. Set working directory di dalam container
WORKDIR /app

# 3. Copy file requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy seluruh kode aplikasi ke dalam working directory
COPY ./app .

# 5. Set environment variable untuk Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# Menonaktifkan Flask debugger di produksi, tapi mengaktifkannya di dev (lihat docker-compose)
ENV FLASK_DEBUG=0

# 6. Expose port yang digunakan oleh Flask
EXPOSE 5000

# 7. Perintah untuk menjalankan aplikasi
CMD ["flask", "run"]