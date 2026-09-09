# Settlement Integration Service (SIS)

The Settlement Integration Service (SIS) is a messaging-oriented middleware system, which is in the middle of systems and core banking systems (flexcube). This version of SIS will replace the existing Adapter system by making the flow more efficient, converting to API services and new UI.

## Pre-requisite

- Docker
- Liquibase

## Installation

- `docker-compose build` (Re-run this anytime when add new python package to requirements.txt)
- duplicate `example.env` file and rename the new one to `.env` file
- navigate to `db` directory, and run `liquibase update-sql` and `liquibase update`

**Note**

- In some case, manual change to migrations file will be needed as sqlAlchemy unable to detect table name changes, column name changes, or anonymously named constraints. Please refer to [Alembic autogenerate documentation](http://alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).
- _(Observation)_ When running `flask db migrate`, sqlAlchemy create extranoeus script when integrate with Oracle DB. Therefore, delete unnessary script from generated migration file in migrations/versions file as fit. Then run `flask db upgrade`.

## Deployment

- `docker-compose up`
- visit `localhost:8000`

_Optional_

- `docker-compose stop`
- `docker-compose restart`

### Reference

- [System Requirements Specification](https://docs.google.com/document/d/1r6dVmq8dGpu9i5AKlSJ5IoFrVoUe_PjdFhPyKljvnW8/edit?usp=sharing)
- [Software Design Document](https://docs.google.com/document/d/1uGyX7Zd36v6MPD4TaV7Wv6YuxqpVugYnnQESW8YfN7g/edit?usp=sharing)

®National Bank of Cambodia, 2022
