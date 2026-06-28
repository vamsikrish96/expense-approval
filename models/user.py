from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    FINANCE = "finance"


class User(BaseModel):
    oid: str
    preferred_username: str
    name: str
    roles: list[str]

    @property
    def has_employee_role(self) -> bool:
        return UserRole.EMPLOYEE.value in self.roles

    @property
    def has_manager_role(self) -> bool:
        return UserRole.MANAGER.value in self.roles

    @property
    def has_finance_role(self) -> bool:
        return UserRole.FINANCE.value in self.roles

    def has_role(self, role: UserRole) -> bool:
        return role.value in self.roles
