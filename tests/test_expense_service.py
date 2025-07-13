import pytest
from freezegun import freeze_time
import datetime
from unittest.mock import patch, MagicMock

from services import expense_service, NotFoundError
from tests.conftest import seeded_test_db
from validation_schemas.schemas import CreateExpenseSchema, UpdateExpenseSchema
from models import User, Expense, Category, Tag

def test_get_expense_by_id_permission_denied(seeded_test_db):
    """
    GIVEN two users, where user A creates an expense
    WHEN user B tries to get user A's expense by its ID
    THEN a NotFoundError should be raised
    """
    # GIVEN
    user_b = seeded_test_db['user2']
    expense_a = seeded_test_db['user1_expense1']

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        expense_service.get_expense_by_id(user_id=user_b.id, expense_id=expense_a.id)

#todo: get_all_expenses test

def test_get_all_categories(seeded_test_db):
    """
    GIVEN a valid user id
    WHEN the get_all_categories service is called
    THEN a list of all categories belonging to that user should be returned
    """
    user_id = seeded_test_db['user1'].id
    categories = expense_service.get_all_categories(user_id)
    assert len(categories) == 2
    assert seeded_test_db['user1_cat1'] in categories
    assert seeded_test_db['user1_cat2'] in categories

def test_get_all_tags(seeded_test_db):
    """
    GIVEN a valid user id
    WHEN the get_all_tags service is called
    THEN a list of all tags belonging to that user should be returned
    """
    user_id = seeded_test_db['user1'].id
    tags = expense_service.get_all_tags(user_id)
    assert len(tags) == 2
    assert seeded_test_db['user1_tag1'] in tags
    assert seeded_test_db['user1_tag2'] in tags

def test_get_category_by_id_success(seeded_test_db):
    """
    GIVEN a valid user id and category id belonging to that user
    WHEN the get_category_by_id service is called
    THEN the corresponding category should be returned
    """
    user_id = seeded_test_db['user1'].id
    category = expense_service.get_category_by_id(user_id, seeded_test_db['user1_cat1'].id)
    assert category == seeded_test_db['user1_cat1']

def test_get_category_by_id_not_found(seeded_test_db):
    """
    GIVEN a user id and category id that does not belong to that user
    WHEN the get_category_by_id service is called
    THEN a NotFoundError should be raised
    """
    user_id = seeded_test_db['user2'].id
    with pytest.raises(NotFoundError):
        category = expense_service.get_category_by_id(user_id, seeded_test_db['user1_cat1'].id)

def test_get_tags_by_id_success(seeded_test_db):
    """
    GIVEN a user id and set of tags that belong to that user
    WHEN the get_tags_by_id service is called
    THEN a list of corresponding tags should be returned
    """
    user_id = seeded_test_db['user1'].id
    tags = expense_service.get_tags_by_id(user_id, {seeded_test_db['user1_tag1'].id, seeded_test_db['user1_tag2'].id})
    assert len(tags) == 2
    assert tags == [seeded_test_db['user1_tag1'], seeded_test_db['user1_tag2']]

def test_get_tags_by_id_not_found(seeded_test_db):
    """
    GIVEN a user id and set of tags where one or is invalid
    WHEN the get_tags_by_id service is called
    THEN a NotFoundError should be raised
    """
    user_id = seeded_test_db['user1'].id
    with pytest.raises(NotFoundError):
        tags = expense_service.get_tags_by_id(user_id,
                                              {seeded_test_db['user1_tag1'].id, seeded_test_db['user2_tag1'].id})

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
        name='Taco Bell',
        amount=12.50,
        description='Lunch',
        category_id=cat.id,
        date=datetime.date(2025, 7, 1),
        active_status=True
    )

    # WHEN
    new_expense = expense_service.create_expense(user_id=user.id, data=expense_data)

    # THEN
    #expense data is correct
    assert new_expense is not None
    assert new_expense.id is not None
    assert new_expense.user_id == user.id
    assert new_expense.name == 'Taco Bell'
    assert new_expense.amount == 12.50
    assert new_expense.date == datetime.date(2025, 7, 1)
    assert new_expense.description == "Lunch"
    assert new_expense.active_status == True
    assert new_expense.category.name == 'Food'
    assert new_expense.category_id == cat.id
    assert len(new_expense.tags) == 0

    retrieved_expense = Expense.query.filter_by(id=new_expense.id).one()
    assert retrieved_expense is not None
    assert retrieved_expense.amount == 12.50
    assert Expense.query.count() == 1

@freeze_time("2025-07-12 12:00:00")
def test_create_expense_with_optional_fields_omitted_success(test_db):
    """
    GIVEN a user and valid expense data where optional fields (description, category_id, tag_ids) are omitted
    WHEN the create_expense service is called
    THEN the expense should be created with default values for those fields
    """
    # GIVEN
    user = User(username='testuser', password_hash='hashed_password')
    test_db.session.add(user)
    test_db.session.commit()

    expense_data = CreateExpenseSchema(
        name = 'lotion',
        amount = 12
    )
    # WHEN
    new_expense = expense_service.create_expense(user_id=user.id, data=expense_data)

    # THEN
    assert new_expense.name == 'lotion'
    assert new_expense.amount == 12
    assert new_expense.description is None
    assert new_expense.category_id is None
    assert new_expense.active_status is True
    assert new_expense.date == datetime.date(2025, 7, 12)
    assert len(new_expense.tags) == 0
    assert Expense.query.count() == 1


def test_create_expense_with_tags_success(test_db):
    """
    GIVEN a user, category, and tags exist in the database
    WHEN the create_expense service is called with valid tag_ids
    THEN a new Expense is created and correctly associated with the tags
    """
    # GIVEN
    user = User(username='testuser', password_hash='hashed_password')
    test_db.session.add(user)
    test_db.session.commit()
    cat = Category(name='Work', user_id=user.id)
    user1_tag1 = Tag(name='project-alpha', user_id=user.id)
    user1_tag2 = Tag(name='client-acme', user_id=user.id)
    test_db.session.add_all([cat, user1_tag1, user1_tag2])
    test_db.session.commit()

    expense_data = CreateExpenseSchema(
        name = 'food',
        amount=250.00,
        description='Team Dinner',
        category_id=cat.id,
        tag_ids={user1_tag1.id, user1_tag2.id}
    )

    # WHEN
    new_expense = expense_service.create_expense(user_id=user.id, data=expense_data)

    # THEN
    assert new_expense is not None
    assert len(new_expense.tags) == 2
    assert {tag.name for tag in new_expense.tags} == {'project-alpha', 'client-acme'}
    assert Expense.query.count() == 1

@patch('services.expense_service.get_tags_by_id')
@patch('services.expense_service.get_category_by_id')
@patch('services.expense_service.db.session')
def test_create_expense_handles_category_not_found(mock_db_session, mock_get_category_by_id, mock_get_tags_by_id):
    """
    GIVEN a call to create_expense
    WHEN the dependency get_category_by_id raises a NotFoundError
    THEN create_expense should propagate the error and not commit to the database
    """
    # GIVEN
    invalid_category_id = 999
    mock_get_category_by_id.side_effect = NotFoundError(f'Category with id {invalid_category_id} not found')
    mock_get_tags_by_id.return_value = []

    expense_data = CreateExpenseSchema(
        name='pens',
        amount=50.00,
        description='Office Supplies',
        category_id=invalid_category_id,
        date=datetime.date(2025, 7, 2)
    )

    # WHEN
    with pytest.raises(NotFoundError) as excinfo:
        expense_service.create_expense(user_id=1, data=expense_data)

    # THEN
    assert f"Category with id {invalid_category_id} not found" in str(excinfo.value)
    mock_get_category_by_id.assert_called_once_with(1, invalid_category_id)
    mock_db_session.commit.assert_not_called()


@patch('services.expense_service.get_tags_by_id')
@patch('services.expense_service.get_category_by_id')
@patch('services.expense_service.db.session')
def test_create_expense_handles_tags_invalid(mock_db_session, mock_get_category_by_id, mock_get_tags_by_id):
    """
    GIVEN a call to create_expense
    WHEN the dependency get_tags_by_id raises a NotFoundError
    THEN create_expense should propagate the error and not commit to the database
    """
    # GIVEN
    invalid_tag_ids = {1, 2, 3}
    mock_get_category_by_id.return_value = MagicMock()
    mock_get_tags_by_id.side_effect = NotFoundError(f"One or more invalid tag ids: {sorted(list(invalid_tag_ids))}")

    expense_data = CreateExpenseSchema(
        name='pens',
        amount=50.00,
        description='Office Supplies',
        category_id=1,
        tag_ids= invalid_tag_ids,
        date=datetime.date(2025, 7, 2)
    )

    # WHEN
    with pytest.raises(NotFoundError) as excinfo:
        expense_service.create_expense(user_id=1, data=expense_data)

    # THEN
    assert f"One or more invalid tag ids: {sorted(list(invalid_tag_ids))}" in str(excinfo.value)
    mock_get_tags_by_id.assert_called_once_with(1, invalid_tag_ids)
    mock_db_session.commit.assert_not_called()

@pytest.mark.parametrize(
    "field_to_update, new_value",
    [
        ("name", "A Brand New Name"),
        ("amount", 150.75),
        ("description", "An updated description"),
        ("description", None),
        ("category_id", None),
        ('category_id', lambda db : db['user1_cat1'].id),
        ("tag_ids", set()),
        ("tag_ids", lambda db: {db['user1_tag1'].id, db['user1_tag2'].id})
    ]
)
def test_update_expense_one_field_success(seeded_test_db, field_to_update, new_value):
    """
    GIVEN an existing expense in the database
    WHEN the update_expense service is called
    THEN the expense should be updated in the database
    """
    # GIVEN
    user = seeded_test_db['user1']
    original_expense = seeded_test_db['user1_expense1']

    if callable(new_value):
        new_value = new_value(seeded_test_db)

    update_data = UpdateExpenseSchema(**{field_to_update: new_value})

    # WHEN
    updated_expense = expense_service.update_expense(
        user_id=user.id,
        expense_id=original_expense.id,
        data=update_data
    )

    # THEN
    if field_to_update == 'tag_ids':
        expected_value = sorted(list(new_value))
        assert [tag.id for tag in getattr(updated_expense, 'tags')] == expected_value
    else:
        expected_value = new_value
        assert getattr(updated_expense, field_to_update) == expected_value


def test_update_expense_with_invalid_category_fails(seeded_test_db):
    """
    GIVEN an existing expense
    WHEN the update_expense service is called with a non-existent category_id
    THEN a NotFoundError should be raised
    """
    # GIVEN
    user = seeded_test_db['user1']
    original_expense = seeded_test_db['user1_expense1']

    # WHEN / THEN
    update_data = UpdateExpenseSchema(
        category_id=999,  # An invalid category_id
    )
    with pytest.raises(NotFoundError) as excinfo:
        expense_service.update_expense(user.id, original_expense.id, update_data)


def test_delete_expense_success(seeded_test_db):
    """
    GIVEN an existing expense owned by a user
    WHEN the delete_expense service is called by that user
    THEN the expense should be removed from the database
    """
    # GIVEN
    user = seeded_test_db['user1']
    expense = seeded_test_db['user1_expense1']

    # WHEN
    expense_service.delete_expense(user_id=user.id, expense_id=expense.id)

    # THEN
    deleted_expense = seeded_test_db['db'].session.query(Expense).filter_by(id=expense.id).first()
    assert deleted_expense is None

def test_delete_expense_permission_denied(seeded_test_db):
    """
    GIVEN an expense created by user_a
    WHEN user_b attempts to delete it
    THEN a NotFoundError should be raised and the expense should not be deleted
    """
    # GIVEN
    user1 = seeded_test_db['user1']
    user2 = seeded_test_db['user2']
    expense = seeded_test_db['user1_expense1']

    # WHEN / THEN
    with pytest.raises(NotFoundError):
        expense_service.delete_expense(user_id=user2.id, expense_id=expense.id)
