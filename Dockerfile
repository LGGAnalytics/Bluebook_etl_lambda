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

# Set the ChromeDriver version to match the installed Chrome version
ENV CHROME_DRIVER_VERSION=124.0.6367.91

# Download and install ChromeDriver from the new CfT URL
RUN wget -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/bin && \
    chmod +x /usr/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# Set display variable for headless Chrome
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
