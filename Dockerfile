# For more information, please refer to https://aka.ms/vscode-docker-python
FROM ubuntu:22.04 AS base

# 设置非交互模式，避免安装过程中提示交互
ENV DEBIAN_FRONTEND=noninteractive

# 安装依赖库以及工具
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository "deb http://security.ubuntu.com/ubuntu focal-security main"
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    wget \
    pkg-config \
    libnss3 \
    libxi6 \
    libgdk-pixbuf2.0-0 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxext6 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxkbcommon-dev \
    libgbm-dev \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libasound2 \
    libasound2-data \
    libxfixes3 \
    libpangocairo-1.0-0 \
    libcups2 \
    libxshmfence1 \
    xfonts-utils \
    xfonts-encodings \
    fontconfig \
    fonts-dejavu-core \
    tzdata \
    mysql-client \
    libmysqlclient-dev \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' > /etc/timezone \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "deb http://archive.ubuntu.com/ubuntu focal main universe" >> /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    xfonts-75dpi \
    xfonts-base
    
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb && \
    apt-get install -y ./wkhtmltox_0.12.6.1-2.jammy_amd64.deb || apt-get -f install -y && \
    rm -f ./wkhtmltox_0.12.6.1-2.jammy_amd64.deb


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY . /app
WORKDIR /app

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# 拷贝代码
#COPY . /beautify_report

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["python3", "main.py"]
#CMD ["python3", "main.py"]
