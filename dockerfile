FROM --platform=linux/amd64 ubuntu:20.04

# Set environment variable to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install required dependencies (Boost, CMake, GCC)
RUN apt-get update && apt-get install -y \
    # Required dependencies
    libboost-all-dev \
    cmake \
    gcc \
    g++ \
    # Optional dependencies
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Verify CMake version meets requirement (>=3.4)
RUN cmake --version | grep -q "cmake version 3" && \
    cmake --version | awk '{split($3,a,"."); if (a[1] > 3 || (a[1] == 3 && a[2] >= 4)) exit 0; else exit 1;}'

# Set up working directory
WORKDIR /app

# Copy application files
COPY . .

# Set up Python virtual environment and install optional dependencies
RUN python3 -m venv venv && \
    . ./venv/bin/activate && \
    pip install --no-cache-dir \
    python-sat \
    mlpack

CMD ["/bin/bash"]