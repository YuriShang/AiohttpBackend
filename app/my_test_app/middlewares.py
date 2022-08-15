from aiohttp_auth.autz.policy import acl
from app.my_test_app.db.db_handlers import login


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
        user_data = await login(user_identity)
        privilege = user_data.get("privileges", None)

        if privilege is None:
            return tuple()

        if not user_data["blocked"]:
            return privilege,
        return "blocked",
