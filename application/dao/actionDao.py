"""
Action data access object from SIS Oracle database. Contains SQL queries related to action.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.action import Action
from application.utils.query_sanitizer import safe_order_by

_ACTION_ALLOWED_COLUMNS = {
    "ACTION_ID": Action.action_id,
    "NAME": Action.name,
    "STATUS": Action.status,
    "URL": Action.url,
    "CREATED_AT": Action.created_at,
    "UPDATED_AT": Action.updated_at,
}


class ActionDao:
    @staticmethod
    def get_actions(page: int, size: int, order_by: Action, order_method: str) -> List[Action]:
        """
        Get a list of the actions from the database by query parameters.
        :return: A list containing Action model objects.
        """
        actions = Action.query
        actions = safe_order_by(actions, _ACTION_ALLOWED_COLUMNS, order_by, order_method)

        if page and size:
            actions = actions.offset((page - 1) * size).limit(size)
        elif size:
            actions = actions.limit(size)

        return actions.all()

    @staticmethod
    def get_action_by_id(action_id: int) -> Action:
        """
        Get a single action from the database based on action id.
        :param action_id: Action ID which uniquely identifies the action.
        :return: The result of the database query
        """
        return Action.query.get(action_id)

    @staticmethod
    def get_action_by_id_and_status(action_id: int, status: int) -> Action:
        """
        Get a single action from the database based on action id and status.
        :param action_id: Action ID which uniquely identifies the action.
        :param status: Status which identify active or inactive
        :return: The result of the database query
        """
        return Action.query.filter_by(action_id=action_id, status=status).first()

    @staticmethod
    def add_action(action: Action) -> bool:
        """
        Add an action to database
        :param action: Action object representing an action for the application.
        :return: True if the action is inserted into the database, False otherwise.
        """
        db.session.add(action)
        return BasicDao.safe_commit()

    @staticmethod
    def update_action(action_id: int, action: Action) -> bool:
        """
        Update an action in the database.
        :param action_id: Action ID which uniquely identifies the action.
        :param action: Action object representing an action for the application.
        :return: True if the action is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE action SET
                name=:name,
                description=:description,
                updated_by=:updated_by,
                updated_at=:current_date,
                status=:status
            WHERE action_id=:action_id
            """),
            {
                "name": action.name,
                "description": action.description,
                "updated_by": action.updated_by,
                "current_date": datetime.now(),
                "status": action.status,
                "action_id": action_id,
            },
        )
        return BasicDao.safe_commit()
