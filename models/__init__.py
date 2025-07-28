from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy extension
db = SQLAlchemy()


class User(db.Model):
    """Represents a user of the application."""
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    expenses = db.relationship('Expense', back_populates='user', cascade='all, delete-orphan')
    categories = db.relationship('Category', back_populates='user', cascade='all, delete-orphan')
    tags = db.relationship('Tag', back_populates='user', cascade='all, delete-orphan')
    incomes = db.relationship('Income', back_populates='user', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', back_populates='user', cascade='all, delete-orphan')


# Association table for the many-to-many relationship between Expense and Tag
expense_tag = db.Table('expense_tag',
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class Expense(db.Model):
    """Represents a single expense record."""
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    active_status = db.Column(db.Boolean, nullable=False, default=True)
    merchant = db.Column(db.String(50), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    user = db.relationship('User', back_populates='expenses')
    category = db.relationship('Category', back_populates='expenses')
    tags = db.relationship('Tag', secondary=expense_tag, back_populates='expenses')

class Category(db.Model):
    """Represents a category that can be assigned to an expense."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(24), nullable=False)

    user = db.relationship('User', back_populates='categories')
    expenses = db.relationship('Expense', back_populates='category')
    budgets = db.relationship('Budget', back_populates='category', cascade='all, delete-orphan')

class Tag(db.Model):
    """Represents a tag that can be assigned to an expense."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(24), nullable=False)

    user = db.relationship('User', back_populates='tags')
    expenses = db.relationship('Expense', secondary=expense_tag, back_populates='tags')

class Income(db.Model):
    """Represents a single income record."""
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='incomes')

class Budget(db.Model):
    """Represents a monthly budget for a specific category."""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    user = db.relationship('User', back_populates='budgets')
    category = db.relationship('Category', back_populates='budgets')

    __table_args__ = (db.UniqueConstraint('user_id', 'category_id', 'year', 'month', name='_user_category_month_uc'),)



