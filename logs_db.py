from typing import Union, List

from tinydb import TinyDB, Query
from tinydb.operations import increment


class LogsDB:
    def __init__(self, persistent_data_path: str = ".persistent_data"):
        # Create DB
        self.db = TinyDB(f'{persistent_data_path}/logs_db.json')
        # Create tables
        self.users_db = self.db.table("users")
        self.total_messages_db = self.db.table("total_messages")
        self.error_expressions_db = self.db.table("error_expressions")
        # Setup tables
        self.total_messages_db.insert({
            "total_messages": 0,
            "good_expressions": 0,
            "error_expressions": 0,
        })

    def _increment_total_messages(self) -> None:
        self.total_messages_db.update(increment("total_messages"))

    def _increment_good_expressions(self) -> None:
        self.total_messages_db.update(increment("good_expressions"))

    def _increment_error_expressions(self) -> None:
        self.total_messages_db.update(increment("error_expressions"))

    def add_expression_for_user(
        self,
        user: str,
        expression: Union[str, List[str]],
        result: Union[str, List[str]],
    ) -> None:
        current_user_data = self.users_db.get(Query().user_id == user)
        self._increment_good_expressions()
        self._increment_total_messages()
        if current_user_data is None:
            # That's the first expression for the current user, so create it on DB
            self.users_db.insert({
                "user_id": user,
                "num_of_expressions": 1,
                "expressions": [{
                    "expression": expression,
                    "result": result,
                }]
            })
        else:
            # The user already exists, so update their info on DB
            current_user_data["num_of_expressions"] += 1
            current_user_data["expressions"].append({
                    "expression": expression,
                    "result": result,
                })
            self.users_db.upsert(current_user_data, Query().user_id == user)

    def add_error_expression(self, expression: str) -> None:
        self._increment_error_expressions()
        self._increment_total_messages()
        if not self.error_expressions_db.contains(
            Query().error_expression == expression
        ):
            self.error_expressions_db.insert({"error_expression": expression})

    def _get_total_users(self) -> int:
        return len(self.users_db)

    def _get_total_messages(self) -> int:
        return self.total_messages_db.all()[0]["total_messages"]

    def _get_good_expressions(self) -> int:
        return self.total_messages_db.all()[0]["good_expressions"]

    def _get_error_expression(self) -> int:
        return self.total_messages_db.all()[0]["error_expression"]

    def get_stats(self):
        return {
            "total_users": self._get_total_users(),
            "total_messages": self._get_total_messages(),
            "good_expressions": self._get_good_expressions(),
            "error_expression": self._get_error_expression(),
        }
