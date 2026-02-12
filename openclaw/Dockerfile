FROM ubuntu:22.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies + Docker CLI
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    gnupg \
    lsb-release \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /openclaw

# Clone OpenClaw repository
RUN curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard

# Create data directories that will be mounted as volumes
RUN mkdir -p /openclaw-data/config/.openclaw/credentials /openclaw-data/workspace \
    && chmod 700 /openclaw-data/config/.openclaw/credentials

# Set environment to use our custom paths instead of ~/.openclaw
ENV OPENCLAW_HOME=/openclaw-data/config
ENV OPENCLAW_WORKSPACE=/openclaw-data/workspace

# Expose ports
EXPOSE 18789 18790

# Default command - start the OpenClaw gateway server
CMD ["openclaw", "gateway", "--port", "18789"]
# CMD ["bash"]