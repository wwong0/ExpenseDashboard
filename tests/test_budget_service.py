import pytest
from decimal import Decimal

from services import budget_service, NotFoundError
from services.budget_service import BudgetAlreadyExistsError
from validation_schemas.schemas import CreateBudgetSchema, UpdateBudgetSchema
from models import User, Budget



def test_get_all_budgets(seeded_test_db):
    """
    GIVEN a user with two budgets in the database (from conftest)
    WHEN the get_all_budgets service is called with pagination
    THEN it should return a Pagination object with the correct items and metadata,
         ordered by year and month descending.
    """
    # GIVEN
    user1_id = seeded_test_db['user1'].id
    user1_expected_budgets = {
        seeded_test_db['user1_budget1'], # July 2025
        seeded_test_db['user1_budget2']  # August 2025
    }

    # WHEN: Paginate one item at a time
    pagination_page1 = budget_service.get_all_budgets(
        user_id=user1_id,
        page=1,
        per_page=1
    )

    pagination_page2 = budget_service.get_all_budgets(
        user_id=user1_id,
        page=2,
        per_page=1
    )

    # THEN: Verify the metadata and items
    assert pagination_page1.total == 2
    assert pagination_page1.pages == 2
    assert pagination_page1.page == 1
    assert pagination_page1.has_next is True
    assert len(pagination_page1.items) == 1

    assert pagination_page2.page == 2
    assert pagination_page2.has_prev is True
    assert len(pagination_page2.items) == 1

    # Check order (year desc, month desc): August budget should be first
    assert pagination_page1.items[0] == seeded_test_db['user1_budget2']
    assert pagination_page2.items[0] == seeded_test_db['user1_budget1']

    all_retrieved_budgets = set(pagination_page1.items + pagination_page2.items)
    assert all_retrieved_budgets == user1_expected_budgets


def test_get_budget_by_id_success(seeded_test_db):
    """
    GIVEN a user with a budget
    WHEN the get_budget_by_id service is called with the correct user and budget ID
    THEN it should return the correct Budget object
    """
    # GIVEN
    user1 = seeded_test_db['user1']
    budget1 = seeded_test_db['user1_budget1']

    # WHEN
    retrieved_budget = budget_service.get_budget_by_id(user_id=user1.id, budget_id=budget1.id)

    # THEN
    assert retrieved_budget == budget1


def test_get_budget_by_id_permission_denied(seeded_test_db):
    """
    GIVEN two users, where user A creates a budget
    WHEN user B tries to get user A's budget by its ID
    THEN a NotFoundError should be raised
    """
    # GIVEN
    user_b = seeded_test_db['user2']
    budget_a = seeded_test_db['user1_budget1']

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        budget_service.get_budget_by_id(user_id=user_b.id, budget_id=budget_a.id)


def test_get_budget_by_year_month_with_categorical_budget(seeded_test_db):
    """
    GIVEN a user with a categorical budget for a specific month
    WHEN get_budget_by_year_month is called for that month
    THEN it returns a dictionary with the categorical budget and no overall budget
    """
    # GIVEN
    user1_id = seeded_test_db['user1'].id
    categorical_budget = seeded_test_db['user1_budget1']

    # WHEN
    result = budget_service.get_budget_by_year_month(user_id=user1_id, year=2025, month=7)

    # THEN
    assert result['overall'] is None
    assert len(result['categorical']) == 1
    assert result['categorical'][0]['id'] == categorical_budget.id
    assert result['categorical'][0]['category']['id'] == categorical_budget.category_id


def test_get_budget_by_year_month_with_overall_budget(seeded_test_db):
    """
    GIVEN a user with an overall budget for a specific month
    WHEN get_budget_by_year_month is called for that month
    THEN it returns a dictionary with the overall budget and no categorical budgets
    """
    # GIVEN
    user1_id = seeded_test_db['user1'].id
    overall_budget = seeded_test_db['user1_budget2']

    # WHEN
    result = budget_service.get_budget_by_year_month(user_id=user1_id, year=2025, month=8)

    # THEN
    assert result['overall'] is not None
    assert result['overall']['id'] == overall_budget.id
    assert result['categorical'] == []


def test_get_budget_by_year_month_no_budgets(seeded_test_db):
    """
    GIVEN a user
    WHEN get_budget_by_year_month is called for a period with no budgets
    THEN it returns a dictionary with empty values
    """
    # GIVEN
    user1_id = seeded_test_db['user1'].id

    # WHEN
    result = budget_service.get_budget_by_year_month(user_id=user1_id, year=2025, month=1)

    # THEN
    assert result['overall'] is None
    assert result['categorical'] == []


def test_create_overall_budget_success(test_db):
    """
    GIVEN a user and valid data for an overall budget
    WHEN the create_budget service is called
    THEN a new Budget object is created with category_id=None
    """
    # GIVEN
    user = User(username='testuser', password_hash='hash')
    test_db.session.add(user)
    test_db.session.commit()

    budget_data = CreateBudgetSchema(amount=Decimal('1500.00'), year=2026, month=1, category_id=None)

    # WHEN
    new_budget = budget_service.create_budget(user_id=user.id, data=budget_data)

    # THEN
    assert new_budget.id is not None
    assert new_budget.user_id == user.id
    assert new_budget.amount == Decimal('1500.00')
    assert new_budget.year == 2026
    assert new_budget.month == 1
    assert new_budget.category_id is None
    assert Budget.query.count() == 1


def test_create_categorical_budget_success(seeded_test_db):
    """
    GIVEN a user, a category, and valid data for a categorical budget in a new month
    WHEN the create_budget service is called
    THEN a new Budget object is created and associated with the category
    """
    # GIVEN
    user = seeded_test_db['user1']
    category = seeded_test_db['user1_cat2']
    # Create for a non-conflicting period (e.g., Sep 2025)
    budget_data = CreateBudgetSchema(amount=300, year=2025, month=9, category_id=category.id)

    # WHEN
    new_budget = budget_service.create_budget(user_id=user.id, data=budget_data)

    # THEN
    assert new_budget.id is not None
    assert new_budget.user_id == user.id
    assert new_budget.amount == 300
    assert new_budget.year == 2025
    assert new_budget.month == 9
    assert new_budget.category_id == category.id
    assert new_budget.category == category


def test_create_budget_raises_for_conflicting_overall_budget(seeded_test_db):
    """
    GIVEN an overall budget exists for a user for Aug 2025 (from conftest)
    WHEN create_budget is called again for the same scope
    THEN BudgetAlreadyExistsError is raised
    """
    # GIVEN
    user = seeded_test_db['user1']
    # An overall budget for Aug 2025 already exists (`user1_budget2`)
    budget_data = CreateBudgetSchema(amount=500, year=2025, month=8, category_id=None)

    # WHEN / THEN
    with pytest.raises(BudgetAlreadyExistsError) as excinfo:
        budget_service.create_budget(user_id=user.id, data=budget_data)
    assert "Overall budget already exists for 2025-8" in str(excinfo.value)


def test_create_budget_raises_for_conflicting_categorical_budget(seeded_test_db):
    """
    GIVEN a categorical budget exists for a user, category, and month (from conftest)
    WHEN create_budget is called again for the same scope
    THEN BudgetAlreadyExistsError is raised
    """
    # GIVEN
    user = seeded_test_db['user1']
    category = seeded_test_db['user1_cat1']
    # A categorical budget for this user, category, and month already exists (`user1_budget1`)
    budget_data = CreateBudgetSchema(amount=100, year=2025, month=7, category_id=category.id)

    # WHEN / THEN
    with pytest.raises(BudgetAlreadyExistsError) as excinfo:
        budget_service.create_budget(user_id=user.id, data=budget_data)
    assert "Categorical budget already exists for 2025-7" in str(excinfo.value)


def test_update_budget_amount_success(seeded_test_db):
    """
    GIVEN an existing budget
    WHEN the update_budget service is called to change the amount
    THEN the budget's amount is updated successfully
    """
    # GIVEN
    user = seeded_test_db['user1']
    budget = seeded_test_db['user1_budget1'] # July categorical budget
    update_data = UpdateBudgetSchema(amount=Decimal('123.45'))

    # WHEN
    updated_budget = budget_service.update_budget(user.id, budget.id, update_data)

    # THEN
    assert updated_budget.amount == Decimal('123.45')
    assert updated_budget.year == 2025  # Should not change
    assert updated_budget.month == 7    # Should not change


def test_update_budget_raises_for_conflicting_scope(seeded_test_db):
    """
    GIVEN two budgets exist for a user in different scopes
    WHEN update_budget is called to move one budget into the other's scope
    THEN BudgetAlreadyExistsError is raised
    """
    # GIVEN
    user = seeded_test_db['user1']
    budget_to_update = seeded_test_db['user1_budget2'] # Overall, Aug 2025
    conflicting_category = seeded_test_db['user1_cat1']
    # A categorical budget for July 2025 with user1_cat1 already exists (`user1_budget1`)

    # Attempt to move the August overall budget to July and give it the conflicting category
    update_data = UpdateBudgetSchema(month=7, category_id=conflicting_category.id)

    # WHEN / THEN
    with pytest.raises(BudgetAlreadyExistsError):
        budget_service.update_budget(user.id, budget_to_update.id, update_data)


def test_update_budget_with_invalid_category_fails(seeded_test_db):
    """
    GIVEN an existing budget
    WHEN the update_budget service is called with a non-existent category_id
    THEN a NotFoundError should be raised
    """
    # GIVEN
    user = seeded_test_db['user1']
    budget = seeded_test_db['user1_budget1']
    update_data = UpdateBudgetSchema(category_id=999) # Invalid category

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        budget_service.update_budget(user.id, budget.id, update_data)


def test_delete_budget_success(seeded_test_db):
    """
    GIVEN an existing budget owned by a user
    WHEN the delete_budget service is called by that user
    THEN the budget should be removed from the database
    """
    # GIVEN
    user = seeded_test_db['user1']
    budget = seeded_test_db['user1_budget1']
    budget_id = budget.id
    assert Budget.query.get(budget_id) is not None

    # WHEN
    result = budget_service.delete_budget(user_id=user.id, budget_id=budget_id)

    # THEN
    assert result is True
    assert Budget.query.get(budget_id) is None


def test_delete_budget_permission_denied(seeded_test_db):
    """
    GIVEN a budget created by user_a
    WHEN user_b attempts to delete it
    THEN a NotFoundError should be raised and the budget should not be deleted
    """
    # GIVEN
    user2 = seeded_test_db['user2']
    budget1 = seeded_test_db['user1_budget1']
    budget_id = budget1.id

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        budget_service.delete_budget(user_id=user2.id, budget_id=budget_id)

    # Ensure the budget was not deleted
    assert Budget.query.get(budget_id) is not None