from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy extension
db = SQLAlchemy()


class User(db.Model):
    """Represents a user of the application."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


# Association table for the many-to-many relationship between Expense and Tag
expense_tag = db.Table('expense_tag',
    db.Column('expense_id', db.Integer, db.ForeignKey('expense.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)


class Expense(db.Model):
    """Represents a single expense record."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    active_status = db.Column(db.Boolean, nullable=False, default=True)

    # Foreign key for the one-to-many relationship with Category
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    # Relationship to easily access the associated Category object
    category = db.relationship('Category', back_populates='expenses')
    # Relationship to access associated Tag objects via the expense_tag table
    tags = db.relationship('Tag', secondary=expense_tag, back_populates='expenses')


class Category(db.Model):
    """Represents a category that can be assigned to an expense."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(24), nullable=False)

    # Back-reference to access all expenses associated with this category
    expenses = db.relationship('Expense', back_populates='category')


class Tag(db.Model):
    """Represents a tag that can be assigned to an expense."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(24), nullable=False)

    # Back-reference to access all expenses associated with this tag
    expenses = db.relationship('Expense', secondary=expense_tag, back_populates='tags')