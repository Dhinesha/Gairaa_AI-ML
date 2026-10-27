from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import EmployeeService
from app.core.deps import get_current_user


router = APIRouter(
    prefix="/employees",
    tags=["Employees"],  
)


def get_employee_service(db: Session = Depends(get_db)) -> EmployeeService:
    return EmployeeService(db)

@router.get(
    "/",
    response_model=list[EmployeeResponse],
    summary="Get all employees",
)
def get_all_employees(
    service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user)
):
    return service.get_all_employees()


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get employee by ID",
)
def get_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user)
):
    
    return service.get_employee_by_id(employee_id)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
)
def create_employee(
    employee: EmployeeCreate,
    service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user)
):

    return service.create_employee(employee)


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update an employee",
)
def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user)
):
    return service.update_employee(employee_id, employee)


@router.delete(
    "/{employee_id}",
    summary="Delete an employee",
)
def delete_employee(
    employee_id: int,
    service: EmployeeService = Depends(get_employee_service),
    current_user: dict = Depends(get_current_user)
):
    return service.delete_employee(employee_id)
