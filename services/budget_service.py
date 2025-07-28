from sqlalchemy.orm import selectinload
from flask_sqlalchemy.pagination import Pagination

from models import db, Budget
from services.expense_service import get_category_by_id
from validation_schemas.schemas import CreateBudgetSchema, UpdateBudgetSchema, BudgetResponseSchema
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
    budgets = Budget.query.options(selectinload(Budget.category)).filter_by(
        user_id=user_id,
        year=year,
        month=month).all()
    result = {
        "overall": None,
        "categorical": []
    }

    for budget in budgets:
        serialized_budget = BudgetResponseSchema.model_validate(budget).model_dump()
        if budget.category_id is None:
            result["overall"] = serialized_budget
        else:
            result["categorical"].append(serialized_budget)

    return result

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


def _check_for_conflicting_budget(user_id: int, year: int, month: int, category_id: int | None,
                                  existing_budget_id: int | None = None):
    """
    Checks if a budget with the given scope already exists.
    If updating, allows the check to ignore the budget being updated.
    """
    query = Budget.query.filter_by(user_id=user_id, year=year, month=month, category_id=category_id)
    if existing_budget_id:
        query = query.filter(Budget.id != existing_budget_id)

    if query.first():
        scope = "Overall" if category_id is None else "Categorical"
        raise BudgetAlreadyExistsError(f"{scope} budget already exists for {year}-{month}")

def create_budget(user_id: int, data: CreateBudgetSchema):
    """Creates a new budget for a user.

    Args:
        user_id: The ID of the user creating the budget.
        data: A CreateBudgetSchema object with the expense details.

    Returns:
        The newly created Budget object.
    """

    _check_for_conflicting_budget(user_id, data.year, data.month, data.category_id)

    category = get_category_by_id(user_id, data.category_id)

    new_budget = Budget(user_id=user_id,
                        amount=data.amount,
                        year=data.year,
                        month=data.month,
                        category=category)

    db.session.add(new_budget)
    db.session.commit()
    return new_budget

def update_budget(user_id: int, budget_id: int, data: UpdateBudgetSchema):
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

    identity_changing = ('year' in update_data or
                         'month' in update_data or
                         'category_id' in update_data)

    if identity_changing:
        new_year = update_data.get('year', budget.year)
        new_month = update_data.get('month', budget.month)
        new_category_id = update_data.get('category_id', budget.category_id)
        _check_for_conflicting_budget(user_id, new_year, new_month, new_category_id, existing_budget_id= budget_id)

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
