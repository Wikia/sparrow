FROM python:3.4
WORKDIR /code
ADD requirements/ requirements/
RUN pip install -r requirements/local.txt
ADD . /code
ENV PYTHONUNBUFFERED 1
ENV POSTGRES_PASSWORD="foo"
ENV SPARROW_SECRET_KEY="23465rtdgew3245rt"
ENV SPARROW_DATABASE_URL="postgresql://postgres:foo@db:5432/postgres"
ENV DJANGO_SETTINGS_MODULE="sparrow.settings.local"
ENV PYTHONPATH="/code/"