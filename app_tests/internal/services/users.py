class UsersService:
    def __init__(self, session):
        self.session = session

    def create_user(self, json_):
        return self.session.post("/api/users/", json=json_)

    def get_user(self, id_):
        return self.session.get(
            f"/api/users/{id_}",
        )

    def get_users(self, page=1, size=10):
        return self.session.get(
            "/api/users/",
            params={"page": page, "size": size},
        )

    def update_user(self, id_, json_):
        return self.session.patch(
            f"/api/users/{id_}",
            json=json_,
        )

    def delete_user(self, id_):
        return self.session.delete(
            f"/api/users/{id_}",
        )

    def clear_users(self):
        return self.session.delete("/api/users/clear")

    def get_status(self):
        return self.session.get("/api/status")
