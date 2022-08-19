from aiohttp_auth.permissions import Permission
from aiohttp_auth.autz.policy import acl
from app.my_test_app.database.handlers import login
from app.my_test_app.database.connection import get_connection


class ACLAutzPolicy(acl.AbstractACLAutzPolicy):
    """
    Класс обрабатывает привилегии пользователей
    """

    def __init__(self, context=None):
        super().__init__(context)

    async def acl_groups(self, user_identity):
        """
        Функция возвращает привилегии пользователя после успешной аутентификации
        """
        user_data = await login(user_identity, await get_connection())
        privilege = user_data.get("privileges", None)

        if privilege is None:
            return tuple()

        if not user_data["blocked"]:
            return privilege,
        return "blocked",


# Пользователи и их привилегии
context = [
           (Permission.Allow, 'readonly', {'read'}),
           (Permission.Deny, 'readonly', {'create', 'update', 'delete', 'block'}),
           (Permission.Allow, 'admin', {'read', 'create', 'update', 'delete', 'block', 'unblock'}),
           (Permission.Deny, 'block', {'read', 'create', 'update', 'delete', 'block', 'unblock'})
]