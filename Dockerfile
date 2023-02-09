FROM python:3.7-slim
RUN python -m pip install "rasa[full]"
RUN python -m spacy download en_core_web_md
WORKDIR /app
COPY . .
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "8080"]