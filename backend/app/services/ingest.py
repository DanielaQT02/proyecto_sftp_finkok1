from app.services.base import BaseService

class IngestService(BaseService):
    def __init__(self, db):
        super().__init__(db)

ingest_service = IngestService