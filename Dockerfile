FROM ubuntu:22.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies + Docker CLI
RUN apt-get update && apt-get install -y \
    git \
    curl \
    file \
    procps \
    build-essential \
    ca-certificates \
    python3 \
    python3-pip

# brew install
RUN useradd -m -s /bin/bash linuxbrew \
    && NONINTERACTIVE=1 su - linuxbrew -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
ENV PATH=/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:$PATH
RUN su - linuxbrew -c "/home/linuxbrew/.linuxbrew/bin/brew update"

# Install Node.js 22.x
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g openclaw@latest

# Create a directory for OpenClaw data
RUN mkdir -p /openclaw/

# Set working directory
WORKDIR /openclaw

# Expose the default gateway port
EXPOSE 18789

COPY start.py /start.py
RUN chmod +x /start.py

CMD ["python3", "/start.py"]