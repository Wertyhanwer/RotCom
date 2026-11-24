FROM postgres:16-alpine

LABEL maintainer="konndann@mail.ru" \
      version="1.0" \
      description="RotCom DB"

# POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD передаются из .env через docker-compose


EXPOSE 5432


HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}


CMD ["postgres"]