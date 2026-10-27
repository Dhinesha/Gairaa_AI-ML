from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee_model import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.repositories.employee_repository import EmployeeRepository


class EmployeeService:

    def __init__(self, db: Session):
        self.repository = EmployeeRepository(db)

    def get_all_employees(self) -> list[Employee]:
        return self.repository.get_all()

    def get_employee_by_id(self, employee_id: int) -> Employee:

        employee = self.repository.get_by_id(employee_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with id {employee_id} not found",
            )
        return employee

    def create_employee(self, employee_data: EmployeeCreate) -> Employee:

        existing = self.repository.get_by_email(employee_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with email '{employee_data.email}' already exists",
            )

        new_employee = Employee(**employee_data.model_dump())
        return self.repository.create(new_employee)

    def update_employee(self, employee_id: int, employee_data: EmployeeUpdate) -> Employee:
        employee = self.get_employee_by_id(employee_id)

    
        if employee_data.email and employee_data.email != employee.email:
            existing = self.repository.get_by_email(employee_data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{employee_data.email}' is already taken",
                )
        update_data = employee_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(employee, field, value)

        return self.repository.update(employee)

    def delete_employee(self, employee_id: int) -> dict:
        employee = self.get_employee_by_id(employee_id)
        self.repository.delete(employee)
        return {"message": f"Employee '{employee.name}' deleted successfully"}
