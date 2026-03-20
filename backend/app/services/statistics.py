from typing import List

from app.models.statistics import StampingStatistics
from app.models.user import User as UserModel
from app.repositories.business import BusinessRepository
from app.repositories.statistics import StampingStatisticsRepository
from app.schemas.statistics import StampingStatisticsCreate
from app.services.base import BaseService


class StampingStatisticsService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.business_repo = BusinessRepository(db)
        self.statistics_repo = StampingStatisticsRepository(db)

    async def get_statistics(
        self,
        business_id: int,
        limit: int,
        current_user: UserModel
    ) -> List[StampingStatistics]:
        business = await self._get_or_404(self.business_repo.get, business_id)

        if current_user.role in ["superuser", "admin", "soporte", "cobranza"]:
            return await self.statistics_repo.list_by_business(business_id, limit=limit)

        if current_user.role == "cliente":
            self._allow_superuser_admin_or_owner(
                current_user,
                business.account.user_id,
                "No autorizado para ver estadísticas de esta empresa"
            )
            return await self.statistics_repo.list_by_business(business_id, limit=limit)

        self._forbidden("No tienes permiso para ver estadísticas")

    async def create_statistics(
        self,
        stat_data: StampingStatisticsCreate,
        current_user: UserModel
    ) -> StampingStatistics:
        await self._get_or_404(self.business_repo.get, stat_data.business_id)

        self._require_roles(
            current_user,
            ["superuser", "admin"],
            "No tienes permiso para crear estadísticas"
        )

        return await self.statistics_repo.create(stat_data.dict())