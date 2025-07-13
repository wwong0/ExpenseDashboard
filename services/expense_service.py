from sqlalchemy.orm import selectinload
from models import db, Expense, Category, Tag
from validation_schemas.schemas import CreateExpenseSchema, UpdateExpenseSchema
from services import NotFoundError

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
    expense = Expense.query.filter_by(user_id=user_id, id=expense_id).first()
    if not expense:
        raise NotFoundError(f'Expense with id {expense_id} under user_id {user_id} not found')
    return expense

def get_all_expenses(user_id: int) -> list[Expense]:
    """Retrieves all expenses for a given user.

    Eagerly loads related categories and tags to prevent N+1 query problems.

    Args:
        user_id: The ID of the user whose expenses are to be retrieved.

    Returns:
        A list of the user's Expense objects.
    """

    #TODO: this should be paginated
    return Expense.query.options(
        selectinload(Expense.category),
        selectinload(Expense.tags)
    ).filter_by(user_id=user_id).all()


def get_all_categories(user_id: int) -> list[Category]:
    """Retrieves all categories for a given user.

    Args:
        user_id: The ID of the user whose categories are to be retrieved.

    Returns:
        A list of the user's Category objects.
    """
    return Category.query.filter_by(user_id=user_id).all()


def get_all_tags(user_id: int) -> list[Tag]:
    """Retrieves all tags for a given user.

    Args:
        user_id: The ID of the user whose tags are to be retrieved.

    Returns:
        A list of the user's Tag objects.
    """
    return Tag.query.filter_by(user_id=user_id).all()



def get_category_by_id(user_id: int, category_id: int | None) -> Category | None:
    """Retrieves a single category by its ID, ensuring it belongs to the user.

    Args:
        user_id: The ID of the user who owns the category.
        category_id: The ID of the category to retrieve, or None.

    Returns:
        The Category object if found, otherwise None.

    Raises:
        NotFoundError: If a category_id is provided but no matching category
            is found for the user.
    """
    if not category_id:
        return None
    category = Category.query.filter_by(user_id=user_id, id=category_id).first()
    if not category:
        raise NotFoundError(f'Category with id {category_id} not found')
    return category


def get_tags_by_id(user_id: int, tag_ids: set[int]) -> list[Tag]:
    """Retrieves a list of tags by their IDs, ensuring they belong to the user.

    Args:
        user_id: The ID of the user who owns the tags.
        tag_ids: A set of tag IDs to retrieve.

    Returns:
        A list of Tag objects.

    Raises:
        NotFoundError: If any of the provided tag IDs are not found because they are
         invalid or do not belong to the user.
    """
    if not tag_ids:
        return []
    tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()

    if len(tags) != len(tag_ids):
        fetched_ids = {tag.id for tag in tags}
        invalid_ids = tag_ids - fetched_ids
        raise NotFoundError(f"One or more invalid tag ids: {sorted(list(invalid_ids))}")
    return tags


def create_expense(user_id: int, data: CreateExpenseSchema) -> Expense:
    """Creates a new expense record in the database.

    Args:
        user_id: The ID of the user creating the expense.
        data: A CreateExpenseSchema object with the expense details.

    Returns:
        The newly created Expense object.
    """
    category = get_category_by_id(user_id, data.category_id)
    tags = get_tags_by_id(user_id, data.tag_ids)

    new_expense = Expense(
        name = data.name,
        user_id=user_id,
        amount=data.amount,
        description=data.description,
        date=data.date,
        active_status=data.active_status,
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

    for key, value in update_data.items():
        if key == 'category_id':
            expense.category = get_category_by_id(user_id, value)
        elif key == 'tag_ids':
            expense.tags = get_tags_by_id(user_id, value)
        else:
            setattr(expense, key, value)

    db.session.commit()
    return expense


def delete_expense(user_id: int, expense_id: int) -> None:
    """Deletes an expense record from the database.

    Args:
        user_id: The ID of the user owning the expense.
        expense_id: The ID of the expense to delete.
    """
    expense = get_expense_by_id(user_id, expense_id)
    db.session.delete(expense)
    db.session.commit()