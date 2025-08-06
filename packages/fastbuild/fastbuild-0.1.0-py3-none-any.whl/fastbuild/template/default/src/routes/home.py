from fastapi import APIRouter

class HomeRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/", self.index, methods=["GET"])
        
    def index(self):
        return {"message": "Hello World!"}