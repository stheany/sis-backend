from functools import wraps

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from application.utils.responseMessage import get_const


class rbac:
    """Role-Based Access Control (RBAC) — permissions verified server-side via JWT + DB."""

    def check_allowed_access(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Imported inside the wrapper to avoid circular imports at module load time
            from application.dao.userRoleDao import UserRoleDao
            from application.dao.permissionDao import PermissionDao
            from application.models.action import Action

            # Identity is extracted from the verified JWT — cannot be forged by the client
            user_id = get_jwt_identity()

            # Admin bypass — trust comes from the signed token, not a header
            if user_id is not None and int(user_id) == get_const('ADMIN_USER_ID'):
                return func(*args, **kwargs)

            # Load the role assigned to this user
            user_role = UserRoleDao.get_user_role_by_users_login_sis_id(
                users_login_sis_id=user_id
            )
            if not user_role:
                return jsonify({
                    "title": "Unauthorized",
                    "status": 401,
                    "message": "No role assigned to this user.",
                }), 401

            # Load all permissions for that role and collect allowed action URLs
            permissions = PermissionDao.get_permissions_by_role_id(role_id=user_role.role_id)
            action_ids = [p.action_id for p in permissions if p.action_id is not None]

            allowed_urls: set = set()
            if action_ids:
                actions = Action.query.filter(Action.action_id.in_(action_ids)).all()
                allowed_urls = {a.url for a in actions if a.url}

            if request.path in allowed_urls:
                return func(*args, **kwargs)

            return jsonify({
                "title": "Unauthorized",
                "status": 401,
                "message": "Invalid user access for the requested resources!",
            }), 401

        return wrapper
