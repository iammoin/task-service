# FROM python:3.12
# RUN pip install poetry
# COPY . .
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1
# RUN pip3 install poetry
# RUN poetry config virtualenvs.create false
# RUN poetry install 
# RUN pip3 install fastapi gunicorn uvicorn
# COPY . .
# ENTRYPOINT ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
FROM python:3.12
WORKDIR /code
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . /code/
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
EXPOSE 8000