from app.repositories.error import ErrorStampingRepository
from app.services.base import BaseService

class ErrorService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.repo = ErrorStampingRepository(db)

error_service = ErrorService