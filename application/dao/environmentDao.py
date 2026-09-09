"""
Environment data access object from SIS Oracle database. Contains SQL queries related to environment.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.environment import Environment
from application.utils.query_sanitizer import safe_order_by

_ENVIRONMENT_ALLOWED_COLUMNS = {
    "ENV_ID": Environment.env_id,
    "NAME": Environment.name,
    "URL": Environment.url,
    "DESCRIPTION": Environment.description,
    "CREATED_AT": Environment.created_at,
    "UPDATED_AT": Environment.updated_at,
}


class EnvironmentDao:
    @staticmethod
    def get_environments(page: int, size: int, order_by: Environment, order_method: str) -> List[Environment]:
        """
        Get a list of the environments from the database by query parameters.
        :return: A list containing Environment model objects.
        """
        environments = Environment.query
        environments = safe_order_by(environments, _ENVIRONMENT_ALLOWED_COLUMNS, order_by, order_method)

        if page:
            environments = environments.offset((page - 1) * size)

        if size:
            environments = environments.limit(size)

        return environments.all()

    @staticmethod
    def get_environment_by_id(environment_id: int) -> Environment:
        """
            Get a single environment from the database based on environment id.
            :param id: Environment ID which uniquely identifies the environment.
            :return: The result of the database query
            """
        return Environment.query.get(environment_id)

    @staticmethod
    def add_environment(environment: Environment) -> bool:
        """
        Add an environment to database
        :param environment: Environment object representing an environment for the application.
        :return: True if the environment is inserted into the database, False otherwise.
        """
        db.session.add(environment)
        return BasicDao.safe_commit()

    @staticmethod
    def update_environment(environment_id: int, environment: Environment) -> bool:
        """
            Update an environment in the database.
            :param environment_id: Environment ID which uniquely identifies the action.
            :param action: Action object representing an environment for the application.
            :return: True if the environment is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE environment SET
                name=:name,
                description=:description,
                url=:url,
                updated_by=:updated_by,
                updated_at=:updated_at
            WHERE env_id=:env_id
            """),
            {
                "name": environment.name,
                "description": environment.description,
                "url": environment.url,
                "updated_by": environment.updated_by,
                "updated_at": datetime.now(),
                "env_id": environment_id,
            },
        )
        return BasicDao.safe_commit()
