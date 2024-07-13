# Base Image
FROM python:3.9 as base

WORKDIR /home/autodockgpu

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    wget \
    python3-pip \
    openbabel \
    zip \
    unzip \
    cmake \
    netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# MGLTools Installation
FROM base as mglinstall

WORKDIR /home/autodockgpu

RUN wget https://ccsb.scripps.edu/mgltools/download/491/ && \
    mv index.html mgltools_x86_64Linux2_1.5.7.tar.gz && \
    tar -xvzf mgltools_x86_64Linux2_1.5.7.tar.gz && \
    cd mgltools_x86_64Linux2_1.5.7 && \
    ./install.sh

ENV PATH="/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/bin:${PATH}"
ENV LD_LIBRARY_PATH="/home/autodockgpu/mgltools_x86_64Linux2_1.5.7/lib:${LD_LIBRARY_PATH}"

# AutoDock Suite Installation
FROM mglinstall as autodocksuiteinstall

WORKDIR /home/autodockgpu

RUN wget https://autodock.scripps.edu/wp-content/uploads/sites/56/2021/10/autodocksuite-4.2.6-x86_64Linux2.tar && \
    tar -xvf autodocksuite-4.2.6-x86_64Linux2.tar

# Final Image with Python Requirements and Application Code
FROM autodocksuiteinstall as requirements_install

WORKDIR /var/www/server

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy the wait script
COPY wait_for_db.sh /usr/src/app/wait_for_db.sh
RUN chmod +x /usr/src/app/wait_for_db.sh
COPY ./AD4_parameters.dat /home/autodockgpu/x86_64Linux2/

# Use the script as entrypoint
ENTRYPOINT ["/usr/src/app/wait_for_db.sh"]

EXPOSE 8000

# Default command (adjust as needed)
CMD ["python", "app.py"]
