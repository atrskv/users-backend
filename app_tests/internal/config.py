import os


class API:
    def __init__(self, env):
        self.users_service = {
            "dev": f"{os.getenv('DEV_URL')}",
            "beta": "foo",
            "rc": "bar",
        }[env]

        ...

        """self.other_service = (
            {
                "dev": "",
                "beta": "",
                "rc": "",
            }[env],
        )
        """
