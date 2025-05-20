FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for Chromium
RUN yum -y install \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-server-Xvfb \
    wget \
    xdg-utils \
    unzip \
    libdrm \
    mesa-libgbm \
    nss

# Download and install latest Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm && \
    yum localinstall -y google-chrome-stable_current_x86_64.rpm && \
    rm google-chrome-stable_current_x86_64.rpm

# Install chromedriver matching Chrome version
RUN CHROME_VERSION=$(google-chrome --version | sed 's/Google Chrome //') && \
    CHROME_MAJOR=$(echo $CHROME_VERSION | cut -d. -f1) && \
    wget -O chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_MAJOR.0.0/chromedriver_linux64.zip" && \
    unzip chromedriver.zip -d /usr/bin && \
    chmod +x /usr/bin/chromedriver && \
    rm chromedriver.zip

# Set display variable (for headless support)
ENV DISPLAY=:99

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all code
COPY . .

# Set Lambda handler
CMD ["lambda_function.lambda_handler"]
