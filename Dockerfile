FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for Chromium and Selenium
RUN yum install -y \
    alsa-lib atk cups-libs gtk3 \
    libXcomposite libXcursor libXdamage libXext libXi libXrandr \
    libXScrnSaver libXtst pango xorg-x11-server-Xvfb \
    wget unzip libdrm mesa-libgbm nss \
    xdg-utils && yum clean all

# Install Chrome (fixed version)
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm && \
    yum install -y ./google-chrome-stable_current_x86_64.rpm && \
    rm google-chrome-stable_current_x86_64.rpm

# Set fixed chromedriver version to match Chrome
ENV CHROME_DRIVER_VERSION=124.0.6367.207

# Install Chromedriver
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_DRIVER_VERSION}/chromedriver_linux64.zip" && \
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
