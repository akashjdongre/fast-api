FROM python:3.12-slim as builder

#---- Sets the current working directory inside the container. -----#
WORKDIR /app

#----- Install dependencies 
#----- sorurce(from your computer)) ---> destination (inside the container)---------#
COPY requirements.txt .

#-----| Install dependencies from requirements.txt -----#
#-----| without using cache to reduce image size.-----#
#-----| --no-cache-dir ---> stores downloaded packages in a cache.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

    #-----------------------------------Stage 2 -----------------------------------------#
#  Runtime: only what's needed to run
FROM python:3.12-slim AS runtime

# Security: don't run as root
RUN useradd --create-home appuser
WORKDIR /home/appuser/app
USER appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code
# changes ownership to : appuser
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8063

# Production server: Gunicorn manages Uvicorn workers
CMD ["python", "-m", "gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8063", \
     "--timeout", "120", \
     "--access-logfile", "-"]

