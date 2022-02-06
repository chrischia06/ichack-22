FROM python:3.8-slim-bullseye

WORKDIR /app

COPY requirements/requirements.txt .
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt

COPY hello.py .

EXPOSE 8501

CMD streamlit run hello.py
