from flask_sqlalchemy.pagination import Pagination

from models import db, Income
from validation_schemas.schemas import CreateIncomeSchema, UpdateIncomeSchema
from services import NotFoundError

def create_income(user_id: int, data: CreateIncomeSchema) -> Income:
    """Creates a new income record for a user."""
    new_income = Income(
        user_id=user_id,
        amount=data.amount,
        date=data.date,
        source=data.source,
        description=data.description
    )
    db.session.add(new_income)
    db.session.commit()
    return new_income

def get_income_by_id(user_id: int, income_id: int) -> Income:
    """Retrieves a single income by its ID."""
    income = Income.query.filter_by(user_id=user_id, id=income_id).first()
    if not income:
        raise NotFoundError(f'Income with id {income_id} not found')
    return income

def get_all_incomes(user_id: int, page: int = 1, per_page: int = 20) -> Pagination:
    """Retrieves a paginated list of incomes for a given user.

    Args:
        user_id: The ID of the user whose incomes are to be retrieved.
        page: The page number to retrieve.
        per_page: The number of items to retrieve per page.

    Returns:
        A Pagination object containing the user's Income objects for the
        requested page, along with pagination metadata.

    """
    query = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)

def update_income(user_id: int, income_id: int, data: UpdateIncomeSchema):
    """Updates an existing income record.

   Args:
       user_id: The ID of the user owning the income.
       income_id: The ID of the income to update.
       data: An UpdateIncomeSchema object with the fields to update.

   Returns:
       The updated income object.

    """
    income = get_income_by_id(user_id, income_id)
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(income, key, value)

    db.session.commit()
    return income

def delete_income(user_id: int, income_id: int) -> bool:
    """Deletes an income record from the database.

    Args:
        user_id: The ID of the user owning the income.
        income_id: The ID of the income to delete.

    Returns:
        True if the income was successfully deleted.

    """
    income = get_income_by_id(user_id, income_id)
    db.session.delete(income)
    db.session.commit()
    return True