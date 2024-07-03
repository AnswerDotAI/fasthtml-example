FROM python:3.10
WORKDIR /code
COPY --link --chown=1000 . .
RUN mkdir -p /tmp/cache/
RUN chmod a+rwx -R /tmp/cache/
ENV HF_HUB_CACHE=HF_HOME
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1 PORT=7860
CMD ["python", "main.py"]
