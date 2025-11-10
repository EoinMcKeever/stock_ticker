from fastapi import FastAPI


class Dashboard:
    def __init__(self):
        self.app = FastAPI()

    def update_dashboard(self):
        @self.app.get("/update_dashboard")



