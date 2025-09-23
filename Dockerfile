FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libx11-xcb1 libdrm2 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

ENV PLAYWRIGHT_BROWSERS_PATH=/.cache/ms-playwright

# Install playwright
RUN playwright install --with-deps

# Switch to the "user" user
USER user
# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=$HOME/app \
	PYTHONUNBUFFERED=1 \
	PLAYWRIGHT_BROWSERS_PATH=/.cache/ms-playwright \
	SYSTEM=spaces

WORKDIR $HOME/app

# Copy code
COPY --chown=user . $HOME/app

# Expose port
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
