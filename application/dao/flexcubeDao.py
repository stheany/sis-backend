"""
Flexcube data access object from SIS Oracle database. Contains SQL queries related to environment.
"""
from __future__ import annotations

from datetime import datetime
import typing as t
import cx_Oracle

from sqlalchemy.sql import text  # still used in fetch_account_balances
import settings
from application import db
from application.dao.basicDao import BasicDao
from application.models.flexcube import Flexcube
from application.utils.query_sanitizer import safe_order_by

ALLOWED_ORDER_BY = {
    "BRANCH_CODE",
    "CUST_AC_NO",
    "AC_DESC",
    "CCY",
    "ACCOUNT_CLASS",
    "AVAILABLE_BALANCE",
    "CURRENT_BALANCE",
}
ALLOWED_ORDER_METHOD = {"ASC", "DESC"}

_FLEXCUBE_ALLOWED_COLUMNS = {
    "FLEXCUBE_ID": Flexcube.flexcube_id,
    "USERNAME": Flexcube.username,
    "ENVIRONMENT_ID": Flexcube.environment_id,
    "FLEXCUBE_URL": Flexcube.flexcube_url,
    "SOURCE": Flexcube.source,
    "BRANCH": Flexcube.branch,
    "CREATED_AT": Flexcube.created_at,
    "UPDATED_AT": Flexcube.updated_at,
}


class FlexcubeDao:
    @staticmethod
    def get_flexcubes(page: int, size: int, order_by: Flexcube, order_method: str) -> List[Flexcube]:
        """
        Get a list of the environments from the database by query parameters.
        :return: A list containing Environment model objects.
        """
        flexcubes = Flexcube.query
        flexcubes = safe_order_by(flexcubes, _FLEXCUBE_ALLOWED_COLUMNS, order_by, order_method)

        if page:
            flexcubes = flexcubes.offset((page - 1) * size)

        if size:
            flexcubes = flexcubes.limit(size)

        return flexcubes.all()

    @staticmethod
    def get_flexcube_by_id(flexcube_id: int) -> Flexcube:
        """
            Get a single flexcube from the database based on flexcube id.
            :param flexcube_id: Flexcube ID which uniquely identifies the flexcube.
            :return: The result of the database query
            """
        return Flexcube.query.get(flexcube_id)

    @staticmethod
    def add_flexcube(flexcube: Flexcube) -> bool:
        """
            Add a flexcube to database
            :param flexcube: Flexcube object representing an flexcube for the application.
            :return: True if the flexcube is inserted into the database, False otherwise.
        """
        db.session.add(flexcube)
        return BasicDao.safe_commit()

    @staticmethod
    def update_flexcube(flexcube_id: int, flexcube: Flexcube) -> bool:
        """
            Update flexcube in the database.
            :param flexcube_id: Flexcube ID which uniquely identifies the flexcube.
            :param flexcube: Flexcube object representing an flexcube for the application.
            :return: True if the flexcube is updated in the database, False otherwise.
        """
        db.session.execute(
            text("""
            UPDATE flexcube SET
                username=:username,
                password=:password,
                environment_id=:environment_id,
                flexcube_url=:flexcube_url,
                source=:source,
                ubscomp=:ubscomp,
                user_id=:user_id,
                branch=:branch,
                module_id=:module_id,
                service=:service,
                updated_by=:updated_by,
                updated_at=:updated_at
            WHERE flexcube_id=:flexcube_id
            """),
            {
                "username": flexcube.username,
                "password": flexcube.password,
                "environment_id": flexcube.environment_id,
                "flexcube_url": flexcube.flexcube_url,
                "source": flexcube.source,
                "ubscomp": flexcube.ubscomp,
                "user_id": flexcube.user_id,
                "branch": flexcube.branch,
                "module_id": flexcube.module_id,
                "service": flexcube.service,
                "updated_by": flexcube.updated_by,
                "updated_at": datetime.now(),
                "flexcube_id": flexcube_id,
            },
        )
        return BasicDao.safe_commit()
    
    @staticmethod
    def get_external_flexcube_date() -> str:
        """
        Fetch the current business date from external Flexcube Core Banking database (MM-DD-YYYY).
        """
        sql = "SELECT TO_CHAR(TODAY, 'mm-dd-yyyy') FROM MLV_CBS_CURRENT_DATE"
        con = None
        cur = None
        try:
            con = cx_Oracle.connect(
                user=settings.FLEXCUBE_DB_USERNAME,
                password=settings.FLEXCUBE_DB_PASSWORD,
                dsn=settings.FLEXCUBE_DB_DSN, 
                encoding="UTF-8",
            )
            cur = con.cursor()
            cur.execute(sql)
            row = cur.fetchone()
            return row[0] if row else None
        except cx_Oracle.DatabaseError as e:
            print(f"[Flexcube] External DB error: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if con:
                con.close()
                
    @staticmethod
    def fetch_account_balances(
        *,
        ccy: t.Optional[str] = None,
        customer_account_number: t.Optional[str] = None,
        account_class: t.Optional[str] = None,
        branch_code: t.Optional[str] = None,
        order_by: t.Optional[str] = None,
        order_method: t.Optional[str] = "ASC",
        page: int = 1,
        size: int = 10,
    ) -> t.List[t.Tuple]:
        """
        Query DBA_VW_ACC_AVAILABLE safely with bind variables and allowlisted ordering.
        Returns rows as tuples in the order:
        (BRANCH_CODE, CUST_AC_NO, AC_DESC, CCY, ACCOUNT_CLASS, AVAILABLE_BALANCE, CURRENT_BALANCE)
        """
        base_sql = (
            "SELECT BRANCH_CODE, CUST_AC_NO, AC_DESC, CCY, ACCOUNT_CLASS, "
            "AVAILABLE_BALANCE, CURRENT_BALANCE "
            "FROM DBA_VW_ACC_AVAILABLE"
        )

        where: t.List[str] = []
        binds: t.Dict[str, t.Any] = {}

        if customer_account_number:
            where.append("CUST_AC_NO = :cust_ac_no")
            binds["cust_ac_no"] = customer_account_number

        if account_class:
            where.append("ACCOUNT_CLASS = :account_class")
            binds["account_class"] = account_class

        if branch_code:
            where.append("BRANCH_CODE = :branch_code")
            binds["branch_code"] = branch_code

        if ccy:
            where.append("UPPER(CCY) = :ccy")
            binds["ccy"] = ccy.upper()

        sql = base_sql
        if where:
            sql += " WHERE " + " AND ".join(where)

        # --- ORDER BY validation ---
        if order_by:
            col = order_by.strip().upper()
            if col not in ALLOWED_ORDER_BY:
                raise ValueError(f"Invalid orderBy: {order_by}")
            method = (order_method or "ASC").strip().upper()
            if method not in ALLOWED_ORDER_METHOD:
                raise ValueError(f"Invalid orderMethod: {order_method}")
            sql += f" ORDER BY {col} {method}"
        else:
            # Safe default ordering for stable pagination
            sql += " ORDER BY CUST_AC_NO ASC"

        # --- Pagination ---
        page = max(int(page or 1), 1)
        size = max(int(size or 10), 1)
        offset = (page - 1) * size
        sql += " OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY"
        binds["offset"] = offset
        binds["limit"] = size

        with cx_Oracle.connect(
            user=settings.FLEXCUBE_DB_USERNAME,
            password=settings.FLEXCUBE_DB_PASSWORD,
            dsn=settings.FLEXCUBE_DB_DSN,
            encoding="UTF-8",
        ) as con:
            with con.cursor() as cur:
                cur.arraysize = max(size, 100)
                cur.execute(sql, binds)
                return cur.fetchall()