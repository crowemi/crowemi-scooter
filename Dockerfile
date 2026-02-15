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
RUN su - linuxbrew -c "/home/linuxbrew/.linuxbrew/bin/brew update"
RUN mv /home/linuxbrew/.linuxbrew/bin/brew /home/linuxbrew/.linuxbrew/bin/brew-real \
    && printf '%s\n' '#!/bin/sh' 'if [ "$(id -u)" -eq 0 ]; then' '  exec /usr/sbin/runuser -u linuxbrew -- /home/linuxbrew/.linuxbrew/bin/brew-real "$@"' 'fi' 'exec /home/linuxbrew/.linuxbrew/bin/brew-real "$@"' > /home/linuxbrew/.linuxbrew/bin/brew \
    && chmod +x /home/linuxbrew/.linuxbrew/bin/brew
RUN printf '%s\n' '#!/bin/sh' 'exec /usr/sbin/runuser -u linuxbrew -- /home/linuxbrew/.linuxbrew/bin/brew "$@"' > /usr/local/bin/brew \
    && chmod +x /usr/local/bin/brew \
    && brew update \
    && brew install uv gh himalaya

ENV PATH=/usr/local/bin:$PATH:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin

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