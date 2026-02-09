FROM ubuntu:22.04

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /openclaw

# Clone OpenClaw repository
RUN curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard

# Create data directories that will be mounted as volumes
RUN mkdir -p /openclaw-data/config /openclaw-data/workspace

# Set environment to use our custom paths instead of ~/.openclaw
ENV OPENCLAW_HOME=/openclaw-data/config
ENV OPENCLAW_WORKSPACE=/openclaw-data/workspace

# Expose ports
EXPOSE 18789 18790

#  Update OpenClaw to ensure we have the latest version
RUN openclaw update

# Default command - you'll override this to run setup or dashboard
CMD ["bash"]