from app.services.base import BaseService

class ResultsService(BaseService):
    def __init__(self, db):
        super().__init__(db)

results_service = ResultsService