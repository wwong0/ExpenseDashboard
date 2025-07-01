import pytest
from services import expense_service, NotFoundError
from validation_schemas.schemas import CreateExpenseSchema
from models import User, Expense, Category, Tag
from datetime import date


def test_create_expense_success(test_db):
    """
    GIVEN a user and a valid expense data schema
    WHEN the create_expense service is called
    THEN a new Expense object should be created in the database with correct attributes
    """
    # GIVEN
    # Create and commit the user first to get a valid ID.
    user = User(username='testuser', password_hash='hashed_password')
    test_db.session.add(user)
    test_db.session.commit()

    cat = Category(name='Food', user_id=user.id)
    test_db.session.add(cat)
    test_db.session.commit()

    expense_data = CreateExpenseSchema(
        amount=12.50,
        description='Lunch',
        category_id=cat.id,
        date=date(2025, 7, 1),
        active_status=True
    )

    # WHEN
    new_expense = expense_service.create_expense(user_id=user.id, data=expense_data)

    # THEN
    assert new_expense is not None
    assert new_expense.id is not None
    assert new_expense.amount == 12.50
    assert new_expense.description == "Lunch"
    assert new_expense.user_id == user.id
    assert new_expense.category.name == 'Food'
    assert new_expense.category_id == cat.id

    retrieved_expense = Expense.query.filter_by(id=new_expense.id).one()
    assert retrieved_expense.amount == 12.50
    assert Expense.query.count() == 1


def test_create_expense_with_invalid_category_id_fails(test_db):
    """
    GIVEN a user and expense data with a non-existent category_id
    WHEN the create_expense service is called
    THEN a NotFoundError should be raised
    """
    # GIVEN
    user = User(username='testuser', password_hash='hashed_password')
    test_db.session.add(user)
    test_db.session.commit()

    invalid_category_id = 999

    expense_data = CreateExpenseSchema(
        amount=50.00,
        description='Office Supplies',
        category_id=invalid_category_id,  # This ID does not exist
        date=date(2025, 7, 2)
    )

    # WHEN / THEN
    # Use pytest.raises to assert that a specific exception is thrown
    with pytest.raises(NotFoundError) as excinfo:
        expense_service.create_expense(user_id=user.id, data=expense_data)

    assert f"Category with id {invalid_category_id} not found" in str(excinfo.value)
    assert Expense.query.count() == 0  # Ensure no expense was created