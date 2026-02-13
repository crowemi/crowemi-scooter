FROM ubuntu:22.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies + Docker CLI
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip

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

# Default command - you can override this when running
CMD ["openclaw", "gateway", "--port", "18789"]