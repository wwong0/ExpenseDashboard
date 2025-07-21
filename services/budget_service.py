from sqlalchemy.orm import selectinload
from flask_sqlalchemy.pagination import Pagination

from models import db, Budget
from services.expense_service import get_category_by_id
from validation_schemas.schemas import CreateBudgetSchema, UpdateBudgetSchema
from services import NotFoundError

class BudgetAlreadyExistsError(Exception):
    """Custom exception raised when a user tries to register with a username that already exists."""
    pass

def get_budget_by_id(user_id: int, budget_id: int):
    """Retrieves a single budget by its ID.

    Args:
        user_id: The ID of the user who owns the budget.
        budget_id: The ID of the budget to retrieve.

    Returns:
        The Budget object if found.

    Raises:
        NotFoundError: If no budget with the given ID is found for the user.
    """
    budget = Budget.query.options(
        selectinload(Budget.category)).filter_by(user_id=user_id, id=budget_id).first()
    if not budget:
        raise NotFoundError(f'Budget with id {budget_id} not found for user {user_id}')
    return budget

def get_budget_by_year_month(user_id: int, year: int, month: int):
    """Retrieves a single budget by its year and month.

    Args:
        user_id: The ID of the user who owns the budget.
        year: The year of the budget.
        month: The month of the budget.

    Returns:
        The Budget object if found.

    Raises:
        NotFoundError: If no budget with the given ID is found for the user.
    """
    budget = Budget.query.options(
        selectinload(Budget.category)).filter_by(user_id=user_id, year=year, month=month).first()
    if not budget:
        raise NotFoundError(f'Budget for {month}/{year} not found for user {user_id}')
    return budget

def find_budget_by_year_month(user_id: int, year: int, month: int):
    """Retrieves a single budget by its year and month or None if not found

    Args:
        user_id: The ID of the user who owns the budget.
        year: The year of the budget.
        month: The month of the budget.

    Returns:
        The Budget object if found or None if not found
    """
    budget = Budget.query.options(
        selectinload(Budget.category)).filter_by(user_id=user_id, year=year, month=month).first()
    return budget

def get_all_budgets(user_id: int, page: int = 1, per_page: int = 20) -> Pagination:
    """Retrieves a paginated list of budgets for a given user.

    Args:
        user_id: The ID of the user whose budgets are to be retrieved.
        page: The page number to retrieve.
        per_page: The number of items to retrieve per page.

    Returns:
        A Pagination object containing the user's Budget objects for the
        requested page, along with pagination metadata.
    """
    query = Budget.query.options(
        selectinload(Budget.category)
    ).filter_by(user_id=user_id)

    query = query.order_by(Budget.year.desc(), Budget.month.desc(), Budget.id.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)


def create_budget(user_id: int, data: CreateBudgetSchema):
    """Creates a new budget for a user.

    Args:
        user_id: The ID of the user creating the budget.
        data: A CreateBudgetSchema object with the expense details.

    Returns:
        The newly created Budget object.
    """

    if find_budget_by_year_month(user_id, data.year, data.month):
        raise BudgetAlreadyExistsError(f'Budget for {data.month}/{data.year} already exists')

    category = get_category_by_id(user_id, data.category_id)

    new_budget = Budget(user_id=user_id,
                        amount=data.amount,
                        year=data.year,
                        month=data.month,
                        category=category)

    db.session.add(new_budget)
    db.session.commit()
    return new_budget

def update_budget(user_id : int, budget_id: int, data: UpdateBudgetSchema):
    """Updates an existing budget record.

       Args:
           user_id: The ID of the user owning the budget.
           budget_id: The ID of the budget to update.
           data: An UpdateBudgetSchema object with the fields to update.

       Returns:
           The updated budget object.
       """

    budget = get_budget_by_id(user_id, budget_id)
    update_data = data.model_dump(exclude_unset=True)

    if 'category_id' in update_data:
        budget.category = get_category_by_id(user_id, update_data['category_id'])
        update_data.pop('category_id')

    for key, value in update_data.items():
        setattr(budget, key, value)

    db.session.commit()
    return budget

def delete_budget(user_id: int, budget_id: int) -> bool:
    """Deletes a budget record from the database.

    Args:
        user_id: The ID of the user owning the budget.
        budget_id: The ID of the budget to delete.

    Returns:
        True if the budget was successfully deleted.
    """

    budget = get_budget_by_id(user_id, budget_id)
    db.session.delete(budget)
    db.session.commit()

    return True
