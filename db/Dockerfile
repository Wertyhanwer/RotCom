FROM postgres:16-alpine

LABEL maintainer="konndann@mail.ru" \
      version="1.0" \
      description="RotCom DB"

ENV POSTGRES_DB=rotcom \
    POSTGRES_USER=user \
    POSTGRES_PASSWORD=12345

WORKDIR /docker-entrypoint-initdb.d
COPY ./init/*.sql ./

EXPOSE 5432


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}


CMD ["postgres"]