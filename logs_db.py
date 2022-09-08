
class LogsDB:
    def __init__(self):
        self.db = {}
        self.total_messages = 0

    def add_on_db(self, user: str, expression: str, result: str) -> None:
        # Get current user data
        user_db = self.db.get(user, {})
        # Update expressions and results dictionary
        expressions_list = user_db.get("expressions", [])
        expressions_list.append({
            "expression": expression,
            "result": result,
        })
        user_db["expressions"] = expressions_list
        # Increase amount of messages for current user
        user_db["total_expressions"] = user_db.get("total_expressions", 0) + 1
        # Update current user
        self.db[user] = user_db
        # Update total messages
        self.total_messages += 1

    def get_total_users(self) -> int:
        return len(self.db.keys())

    def get_total_messages(self) -> int:
        return self.total_messages
