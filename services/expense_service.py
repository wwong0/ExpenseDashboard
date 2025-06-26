from sqlalchemy.orm import selectinload
from models import db, Expense, Category, Tag
from validation_schemas.schemas import CreateExpenseSchema, UpdateExpenseSchema
from services import NotFoundError



def get_all_expenses(user_id):
    return Expense.query.options(
        selectinload(Expense.category),
        selectinload(Expense.tags)).filter_by(user_id=user_id).all()

def get_all_categories(user_id):
    return Category.query.filter_by(user_id=user_id).all()

def get_all_tags(user_id):
    return Tag.query.filter_by(user_id=user_id).all()

def get_expense_by_id(user_id, expense_id):
    expense = Expense.query.filter_by(user_id=user_id, id=expense_id).first()
    if not expense:
        raise NotFoundError('Expense not found')
    return expense

def get_category_by_id(user_id, category_id):
    category = Category.query.filter_by(user_id=user_id, id=category_id).first()
    if not category:
        raise NotFoundError('Category not found')
    return category

def get_tags_by_id(user_id, tag_ids : list[int]):
    tags = Tag.query.filter(Tag.id.in_(tag_ids), Tag.user_id == user_id).all()
    if len(tags) != len(tag_ids):
        fetched_ids = {tag.id for tag in tags}
        invalid_ids = set(tag_ids) - fetched_ids
        raise ValueError(f"One or more invalid tag ids: {invalid_ids}")
    return tags

def create_expense(user_id, data : CreateExpenseSchema):
    category = get_category_by_id(user_id, data.category_id)

    tags = get_tags_by_id(user_id, data.tag_ids)

    new_expense = Expense(
        user_id = user_id,
        amount = data.amount,
        description = data.description,
        date = data.date,
        active_status = data.active_status,
        category = category,
        tags = tags
    )

    db.session.add(new_expense)
    db.session.commit()

    return new_expense

def update_expense(user_id, expense_id, data : UpdateExpenseSchema):
    expense = get_expense_by_id(user_id, expense_id)

    update_data = data.model_dump(exclude_unset = True)

    for key, value in update_data.items():
        if key == 'category_id':
            category = get_category_by_id(user_id, value)
            expense.category = category
        elif key == 'tag_ids':
            tags = get_tags_by_id(user_id, value)
            expense.tags = tags
        else:
            setattr(expense, key, value)

    db.session.commit()
    return expense

def delete_expense(user_id, expense_id):
    expense = get_expense_by_id(user_id, expense_id)

    db.session.delete(expense)
    db.session.commit()

    return True
