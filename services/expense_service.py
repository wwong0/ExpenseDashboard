from sqlalchemy.orm import selectinload
from flask_sqlalchemy.pagination import Pagination

from models import db, Expense, Category, Tag
from validation_schemas.schemas import CreateExpenseSchema, UpdateExpenseSchema
from services import NotFoundError

def get_all_expenses(user_id: int, page: int = 1, per_page: int = 20) -> Pagination:
    """Retrieves a paginated list of expenses for a given user.

    Eagerly loads related categories and tags to prevent N+1 query problems.

    Args:
        user_id: The ID of the user whose expenses are to be retrieved.
        page: The page number to retrieve.
        per_page: The number of items to retrieve per page.

    Returns:
        A Pagination object containing the user's Expense objects for the
        requested page, along with pagination metadata.
    """

    query = Expense.query.options(
        selectinload(Expense.category),
        selectinload(Expense.tags)
    ).filter_by(user_id=user_id)

    query = query.order_by(Expense.date.desc(), Expense.id.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_expense_by_id(user_id: int, expense_id: int) -> Expense:
    """Retrieves a single expense by its ID.

    Args:
        user_id: The ID of the user who owns the expense.
        expense_id: The ID of the expense to retrieve.

    Returns:
        The Expense object if found.

    Raises:
        NotFoundError: If no expense with the given ID is found for the user.
    """
    expense = Expense.query.options(
        selectinload(Expense.category),
        selectinload(Expense.tags)
    ).filter_by(user_id=user_id, id=expense_id).first()
    if not expense:
        raise NotFoundError(f'Expense with id {expense_id} under user_id {user_id} not found')
    return expense

def get_all_categories(user_id: int, page: int = 1, per_page: int = 20) -> Pagination:
    """Retrieves a paginated list of categories for a given user.

    Args:
        user_id: The ID of the user whose categories are to be retrieved.
        page: The page number to retrieve.
        per_page: The number of items to retrieve per page.

    Returns:
        A Pagination object containing the user's Category objects for the
        requested page, along with pagination metadata.
    """
    query = Category.query.filter_by(user_id=user_id)

    query = query.order_by(Category.name)

    return query.paginate(page=page, per_page=per_page, error_out=False)

def get_category_by_id(user_id: int, category_id: int | None) -> Category | None:
    """Retrieves a single category by its ID, ensuring it belongs to the user.

    Args:
        user_id: The ID of the user who owns the category.
        category_id: The ID of the category to retrieve, or None.

    Returns:
        The Category object if found, otherwise None if category_id is None.

    Raises:
        NotFoundError: If a category_id is provided but no matching category
            is found for the user.
    """
    if category_id is None:
        return None
    category = Category.query.filter_by(user_id=user_id, id=category_id).first()
    if not category:
        raise NotFoundError(f'Category with id {category_id} not found')
    return category

def create_category(user_id: int, name: str):
    """Creates a new category for a user.

    Args:
        user_id: The ID of the user creating the category.
        name: The name of the category.

    Returns:
        The newly created Category object.
    """
    new_category = Category(user_id=user_id, name=name)
    db.session.add(new_category)
    db.session.commit()

    return new_category

def update_category(user_id: int, category_id: int, name: str):
    """Updates an existing category.

    Args:
        user_id: The ID of the user who owns the category.
        category_id: The ID of the category to update.
        name: The new name for the category.

    Returns:
        The updated Category object.

    Raises:
        NotFoundError: If no category with the given ID is found for the user.
    """
    category = get_category_by_id(user_id, category_id)
    category.name = name
    db.session.commit()
    return category

def delete_category(user_id: int, category_id: int) -> bool:
    """Deletes a category from the database.

    Args:
        user_id: The ID of the user who owns the category.
        category_id: The ID of the category to delete.

    Returns:
        True if the category was successfully deleted.

    Raises:
        NotFoundError: If no category with the given ID is found for the user.
    """
    category = get_category_by_id(user_id, category_id)
    db.session.delete(category)
    db.session.commit()
    return True

def get_all_tags(user_id: int, page: int = 1, per_page: int = 20) -> Pagination:
    """Retrieves all tags for a given user.

    Args:
        user_id: The ID of the user whose tags are to be retrieved.
        page: The page number to retrieve.
        per_page: The number of items to retrieve per page.

    Returns:
        A Pagination object containing the user's Tag objects for the
        requested page, along with pagination metadata.
    """
    query = Tag.query.filter_by(user_id=user_id)

    query = query.order_by(Tag.name)

    return query.paginate(page=page, per_page=per_page, error_out=False)

def validate_tags(user_id : int, tag_ids : set[int]):
    validation_query = Tag.query.with_entities(Tag.id).filter(
        Tag.id.in_(tag_ids),
        Tag.user_id == user_id
    )
    fetched_ids = {row.id for row in validation_query.all()}
    if len(fetched_ids) != len(tag_ids):
        invalid_ids = tag_ids - fetched_ids
        raise NotFoundError(f"One or more invalid tag ids: {sorted(list(invalid_ids))}")

    return fetched_ids

def get_tags_by_ids(user_id: int, tag_ids: set[int]) -> list[Tag]:
    """Retrieves a list of tags by their IDs, ensuring they belong to the user.

    Args:
        user_id: The ID of the user who owns the tags.
        tag_ids: A set of tag IDs to retrieve.

    Returns:
        A list of Tag objects.

    Raises:
        NotFoundError: If any of the provided tag IDs are invalid or do not
         belong to the user.
    """
    if not tag_ids:
        return []

    fetched_ids = validate_tags(user_id, tag_ids)

    query = Tag.query.filter(Tag.id.in_(fetched_ids)).order_by(Tag.name)
    return query.all()

def get_tag_by_id(user_id: int, tag_id: int) -> Tag:
    """Retrieves a single tag by its ID, ensuring it belongs to the user.

    Args:
        user_id: The ID of the user who owns the category.
        tag_id: The ID of the category to retrieve, or None.

    Returns:
        The Tag object if found, otherwise None.

    Raises:
        NotFoundError: If a tag_id is provided but no matching category
            is found for the user.
    """

    tag = Tag.query.filter_by(user_id=user_id, id=tag_id).first()
    if not tag:
        raise NotFoundError(f'Tag with id {tag_id} not found')
    return tag

def create_tag(user_id: int, name: str):
    """Creates a new tag for a user.

    Args:
        user_id: The ID of the user creating the tag.
        name: The name of the tag.

    Returns:
        The newly created Tag object.
    """
    new_tag = Tag(user_id=user_id, name=name)
    db.session.add(new_tag)
    db.session.commit()

    return new_tag

def update_tag(user_id: int, tag_id: int, name: str):
    """Updates an existing tag.

    Args:
        user_id: The ID of the user who owns the tag.
        tag_id: The ID of the tag to update.
        name: The new name for the tag.

    Returns:
        The updated Tag object.

    Raises:
        NotFoundError: If no tag with the given ID is found for the user.
    """
    tag = get_tag_by_id(user_id, tag_id)
    tag.name = name
    db.session.commit()
    return tag

def delete_tag(user_id: int, tag_id: int) -> bool:
    """Deletes a tag from the database.

    Args:
        user_id: The ID of the user who owns the tag.
        tag_id: The ID of the tag to delete.

    Returns:
        True if the tag was successfully deleted.

    Raises:
        NotFoundError: If no tag with the given ID is found for the user.
    """
    tag = get_tag_by_id(user_id, tag_id)
    db.session.delete(tag)
    db.session.commit()
    return True

def create_expense(user_id: int, data: CreateExpenseSchema) -> Expense:
    """Creates a new expense record in the database.

    Args:
        user_id: The ID of the user creating the expense.
        data: A CreateExpenseSchema object with the expense details.

    Returns:
        The newly created Expense object.
    """
    category = get_category_by_id(user_id, data.category_id)
    tags = get_tags_by_ids(user_id, data.tag_ids)

    new_expense = Expense(
        name = data.name,
        user_id=user_id,
        amount=data.amount,
        description=data.description,
        date=data.date,
        active_status=data.active_status,
        merchant=data.merchant,
        category=category,
        tags=tags
    )

    db.session.add(new_expense)
    db.session.commit()

    return new_expense

def update_expense(user_id: int, expense_id: int, data: UpdateExpenseSchema) -> Expense:
    """Updates an existing expense record.

    Args:
        user_id: The ID of the user owning the expense.
        expense_id: The ID of the expense to update.
        data: An UpdateExpenseSchema object with the fields to update.

    Returns:
        The updated Expense object.
    """
    expense = get_expense_by_id(user_id, expense_id)
    update_data = data.model_dump(exclude_unset=True)

    if 'category_id' in update_data:
        expense.category = get_category_by_id(user_id, update_data['category_id'])
        update_data.pop('category_id')

    if 'tag_ids' in update_data:
        expense.tags = get_tags_by_ids(user_id, update_data['tag_ids'])
        update_data.pop('tag_ids')

    for key, value in update_data.items():
            setattr(expense, key, value)

    db.session.commit()
    return expense


def delete_expense(user_id: int, expense_id: int) -> bool:
    """Deletes an expense record from the database.

    Args:
        user_id: The ID of the user owning the expense.
        expense_id: The ID of the expense to delete.

    Returns:
        True if the expense was successfully deleted.
    """
    expense = get_expense_by_id(user_id, expense_id)
    db.session.delete(expense)
    db.session.commit()

    return True

