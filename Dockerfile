# For more information, please refer to https://aka.ms/vscode-docker-python
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim

# 设置非交互模式，避免安装过程中提示交互
ENV DEBIAN_FRONTEND=noninteractive

# 安装依赖库以及工具
RUN apt-get update && apt-get install -y \
    git \
    wget \
    pkg-config \
    build-essential \
    tzdata \
    poppler-utils \
    default-libmysqlclient-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' > /etc/timezone \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y  xfonts-75dpi xfonts-base


# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
LABEL Name=report_ocr Version=0.0.1
COPY . /report_ocr
WORKDIR /report_ocr

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt
# Remove opencv-contrib-python if present — it conflicts with opencv-python-headless
RUN pip uninstall -y opencv-contrib-python 2>/dev/null || true

# Creates a non-root user with an explicit UID and adds permission to access the /report_ocr folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /report_ocr
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
ENTRYPOINT ["python3", "main.py"]
#CMD ["python3", "main.py"]
