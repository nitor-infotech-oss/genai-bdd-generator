FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libprotobuf-dev \
    protobuf-compiler\
    pkg-config \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

EXPOSE 8501

# RUN python startup.py

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "1_🏠_Home.py", "--server.port=8501", "--server.address=0.0.0.0"]

# CMD ["python", "startup.py", "&"]