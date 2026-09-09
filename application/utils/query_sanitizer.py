"""
Utility for safe ORDER BY parameter handling.
Prevents SQL injection by whitelisting allowed column names and sort directions.
"""
from sqlalchemy.orm.attributes import InstrumentedAttribute


def safe_order_by(query, allowed_columns: dict, order_by, order_method: str):
    """
    Apply ORDER BY to a SQLAlchemy query using a whitelist of allowed columns.

    :param query: SQLAlchemy query object
    :param allowed_columns: dict mapping uppercase column name strings to model column attributes
    :param order_by: raw orderBy value from request (string or SQLAlchemy column attribute)
    :param order_method: raw orderMethod value from request ("asc" / "desc")
    :return: query with safe ORDER BY applied
    """
    if not order_by and not order_method:
        return query

    direction = str(order_method or "ASC").upper().strip()
    if direction not in {"ASC", "DESC"}:
        direction = "ASC"

    # If already a SQLAlchemy column attribute (e.g. default=Model.col), use it directly
    if isinstance(order_by, InstrumentedAttribute):
        col_attr = order_by
    else:
        col_key = str(order_by).upper().strip()
        col_attr = allowed_columns.get(col_key)
        if col_attr is None:
            # Unknown column — fall back to the first (PK) instead of injecting raw input
            col_attr = next(iter(allowed_columns.values()))

    return query.order_by(col_attr.asc() if direction == "ASC" else col_attr.desc())
