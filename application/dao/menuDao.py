"""
Menu data access object from SIS Oracle database. Contains SQL queries related to Menu.
"""
from datetime import datetime
from typing import List

from sqlalchemy import text

from application import db
from application.dao.basicDao import BasicDao
from application.models.menu import Menu
from application.utils.query_sanitizer import safe_order_by

_MENU_ALLOWED_COLUMNS = {
    "MENU_ID": Menu.menu_id,
    "NAME": Menu.name,
    "STATUS": Menu.status,
    "URL": Menu.url,
    "ICON": Menu.icon,
    "CREATED_AT": Menu.created_at,
    "UPDATED_AT": Menu.updated_at,
}


class MenuDao:
    @staticmethod
    def get_menus(page: int, size: int, order_by: Menu, order_method: str) -> List[Menu]:
        """
        Get a list of the menu from the database by query parameters.
        :return: A list containing Menu model objects.
        """
        menus = Menu.query
        menus = safe_order_by(menus, _MENU_ALLOWED_COLUMNS, order_by, order_method)
        
        if size:
            menus = menus.limit(size)
        if page and size:
            menus = menus.offset((page - 1) * size)

        return menus.all()

    @staticmethod
    def get_menu_by_id(menu_id: int) -> Menu:
        """
            Get a single menu from the database based on menu id.
            :param menu_id: Menu ID which uniquely identifies the Menu.
            :return: The result of the database query
        """
        return Menu.query.get(menu_id)

    @staticmethod
    def get_menu_by_id_and_status(menu_id: int, status: int) -> Menu:
        """
        Get a single menu from the database based on menu id and status.
        :param menu_id: Menu ID which uniquely identifies the menu.
        :param status: Status which identify active or inactive
        :return: The result of the database query
        """
        return Menu.query.filter_by(menu_id=menu_id, status=status).first()

    @staticmethod
    def get_menu_by_name(name: str) -> Menu:
        """
            Get a single menu from the database based on menu name.
            :param name: Menu name which uniquely identifies the Menu.
            :return: The result of the database query
            """
        return Menu.query.filter_by(name=name).first()

    @staticmethod
    def add_menu(menu: Menu) -> bool:
        """
            Add a Menu to database
            :param menu: Menu object representing a Menu for the application.
            :return: True if the menu is inserted into the database, False otherwise.
        """
        db.session.add(menu)
        return BasicDao.safe_commit()

    @staticmethod
    def update_menu(menu_id: int, menu: Menu) -> bool:
        """
            Update Menu in the database.
            :param menu_id: Menu ID which uniquely identifies the Menu.
            :param menu: Menu object representing a Menu for the application.
            :return: True if the menu is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE menu SET
                name=:name,
                description=:description,
                updated_at=:updated_at,
                updated_by=:updated_by,
                status=:status,
                url=:url,
                icon=:icon
            WHERE menu_id=:menu_id
            """),
            {
                "name": menu.name,
                "description": menu.description,
                "updated_at": datetime.now(),
                "updated_by": menu.updated_by,
                "status": menu.status,
                "url": menu.url,
                "icon": menu.icon,
                "menu_id": menu_id
            },
        )
        return BasicDao.safe_commit()
