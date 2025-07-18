import logging
from typing import Any, Dict, List
from .user_group_repository import get_user_group_repository

logger = logging.getLogger(__name__)

class UserGroupService:
    def __init__(self):
        self.repo = get_user_group_repository()

    def get_user_groups(self) -> List[Dict[str, Any]]:
        return self.repo.get_user_groups()

    def create_user_group(self, data: Dict[str, Any]) -> str:
        return self.repo.create_user_group(data)

    def update_user_group(self, doc_id: str, data: Dict[str, Any]) -> bool:
        return self.repo.update_user_group(doc_id, data)

    def get_user_group(self, doc_id: str) -> Dict[str, Any] | None:
        return self.repo.get_user_group(doc_id)

    def delete_user_group(self, doc_id: str) -> bool:
        return self.repo.delete_user_group(doc_id)

    def get_groups_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        records = self.repo.get_user_groups()
        return [r for r in records if (r.get('userId') == user_id or r.get('userEmail') == user_id) and r.get('status') != 'deleted']

_service: UserGroupService | None = None

def get_user_group_service() -> UserGroupService:
    global _service
    if _service is None:
        _service = UserGroupService()
    return _service
