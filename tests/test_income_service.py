import pytest
from decimal import Decimal
import datetime

from services import income_service, NotFoundError
from validation_schemas.schemas import CreateIncomeSchema, UpdateIncomeSchema
from models import Income

def test_create_income_success(seeded_test_db):
    """
    GIVEN a user and valid income data
    WHEN the create_income service is called
    THEN a new Income object should be created in the database
    """
    # GIVEN
    user = seeded_test_db['user1']
    income_data = CreateIncomeSchema(
        source='Freelance',
        amount=Decimal('500.00'),
        date=datetime.date(2025, 7, 15)
    )

    # WHEN
    new_income = income_service.create_income(user_id=user.id, data=income_data)

    # THEN
    assert new_income is not None
    assert new_income.user_id == user.id
    assert new_income.source == 'Freelance'
    assert new_income.amount == Decimal('500.00')
    assert Income.query.count() == 2 # 1 from seed, 1 from this test

def test_get_all_incomes(seeded_test_db):
    """
    GIVEN a user with an existing income
    WHEN the get_all_incomes service is called
    THEN it should return a Pagination object with the correct income
    """
    # GIVEN
    user1_id = seeded_test_db['user1'].id
    user1_income = seeded_test_db['user1_income1']

    # WHEN
    pagination = income_service.get_all_incomes(user_id=user1_id)

    # THEN
    assert pagination.total == 1
    assert len(pagination.items) == 1
    assert pagination.items[0] == user1_income

def test_get_income_by_id_permission_denied(seeded_test_db):
    """
    GIVEN user A's income
    WHEN user B tries to get it
    THEN a NotFoundError should be raised
    """
    # GIVEN
    user2_id = seeded_test_db['user2'].id
    user1_income_id = seeded_test_db['user1_income1'].id

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        income_service.get_income_by_id(user_id=user2_id, income_id=user1_income_id)

def test_update_income_success(seeded_test_db):
    """
    GIVEN an existing income
    WHEN the update_income service is called with new data
    THEN the income record should be updated in the database
    """
    # GIVEN
    user1_id = seeded_test_db['user1'].id
    income_to_update = seeded_test_db['user1_income1']
    update_data = UpdateIncomeSchema(source='Updated Source', amount=Decimal('2500.00'))

    # WHEN
    updated_income = income_service.update_income(
        user_id=user1_id,
        income_id=income_to_update.id,
        data=update_data
    )

    # THEN
    assert updated_income.source == 'Updated Source'
    assert updated_income.amount == Decimal('2500.00')

def test_delete_income_success(seeded_test_db):
    """
    GIVEN an existing income
    WHEN the delete_income service is called
    THEN the income should be removed from the database
    """
    # GIVEN
    user1_id = seeded_test_db['user1'].id
    income_to_delete = seeded_test_db['user1_income1']
    assert Income.query.count() == 1

    # WHEN
    result = income_service.delete_income(user_id=user1_id, income_id=income_to_delete.id)

    # THEN
    assert result is True
    assert Income.query.count() == 0