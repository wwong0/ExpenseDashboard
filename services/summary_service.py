from sqlalchemy import func, extract
from datetime import date

from models import db, Expense, Category, Tag, expense_tag




def get_expense_summary_by_category(user_id: int, start_date: date, end_date: date) -> list[dict]:
    """
    Generates a summary of expenses grouped by category for a given user and date range.

    Args:
        user_id: The ID of the user.
        start_date: The start of the date range for the summary.
        end_date: The end of the date range for the summary.

    Returns:
        A list of dictionaries, where each dictionary contains the category name,
        the total amount spent, and the number of transactions.
    """
    summary_query = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total_amount'),
        func.count(Expense.id).label('count')
    ).join(Category, Expense.category_id == Category.id).filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date,
        Expense.active_status == True
    ).group_by(
        Category.name
    ).order_by(
        func.sum(Expense.amount).desc()
    )

    results = summary_query.all()

    summary_data = [
        {
            "category_name": name,
            "total_amount": float(total), # The sum will be a Decimal, convert to float for JSON
            "count": count
        }
        for name, total, count in results
    ]

    return summary_data

def get_spending_over_time(user_id: int, start_date: date, end_date: date):
    """Generates a time-series summary of total spending per day for a given user and date range.

    Args:
        user_id: The ID of the user.
        start_date: The start of the date range for the summary.
        end_date: The end of the date range for the summary.

    Returns:
        A list of dictionaries, where each dictionary contains the date and the total amount spent
        on that date.
    """
    results = db.session.query(
        Expense.date,
        func.sum(Expense.amount).label('total_amount')
    ).filter(
        Expense.user_id == user_id,
        Expense.date.between(start_date, end_date)
    ).group_by(
        Expense.date
    ).order_by(
        Expense.date.asc()
    ).all()

    return [
        {"date": str(d), "amount": float(total)}
        for d, total in results
    ]

def get_monthly_summary_by_category(user_id: int, year: int, month: int):
    """Generates a summary of spending grouped by category for a specific month.

    Args:
        user_id: The ID of the user.
        year: The year for which to retrieve the summary.
        month: The month for which to retrieve the summary.

    Returns:
        A list of dictionaries, where each dictionary contains the category name
        and the total amount spent in that category for the specified month.
    """
    results = db.session.query(
        Category.name,
        func.sum(Expense.amount).label('total_amount')
    ).join(Category).filter(
        Expense.user_id == user_id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month
    ).group_by(
        Category.name
    ).order_by(
        func.sum(Expense.amount).desc()
    ).all()

    return [{"category": name, "amount": float(total)} for name, total in results]

def get_top_tags(user_id: int, start_date: date, end_date: date, limit: int = 10):
    """
    Finds the most frequently used tags for a user in a given period.

    Args:
        user_id: The ID of the user.
        start_date: The start of the date range for the summary.
        end_date: The end of the date range for the summary.
        limit: The maximum number of top tags to return.

    Returns:
        A list of dictionaries, where each dictionary contains the tag name
        and its usage count.
    """

    results = db.session.query(
        Tag.name,
        func.count(expense_tag.c.expense_id).label('usage_count')
    ).join(
        expense_tag, Tag.id == expense_tag.c.tag_id
    ).join(
        Expense, expense_tag.c.expense_id == Expense.id
    ).filter(
        Expense.user_id == user_id,
        Expense.date.between(start_date, end_date)
    ).group_by(
        Tag.name
    ).order_by(
        func.count(expense_tag.c.expense_id).desc()
    ).limit(limit).all()

    return [{"tag": name, "count": count} for name, count in results]