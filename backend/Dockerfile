
FROM python:3.12
WORKDIR /user/src/app
COPY . .
RUN pip install fastapi pydantic uvicorn psycopg2

EXPOSE 8000

CMD ["python", "api.py"]
