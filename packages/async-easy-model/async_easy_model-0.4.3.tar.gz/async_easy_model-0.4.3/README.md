# async-easy-model

A simplified SQLModel-based ORM for async database operations in Python. async-easy-model provides a clean, intuitive interface for common database operations while leveraging the power of SQLModel and SQLAlchemy.

<p align="center">
  <img src="https://img.shields.io/pypi/v/async-easy-model" alt="PyPI Version">
  <img src="https://img.shields.io/pypi/pyversions/async-easy-model" alt="Python Versions">
  <img src="https://img.shields.io/github/license/puntorigen/easy_model" alt="License">
</p>

## Features

- 🚀 Easy-to-use async database operations with standardized methods
- 🔄 Intuitive APIs with sensible defaults for rapid development
- 📊 Dictionary-based CRUD operations (select, insert, update, delete)
- 🔗 Enhanced relationship handling with eager loading and nested operations
- 🔍 Powerful query methods with flexible ordering support
- ⚙️ Automatic relationship detection and bidirectional setup
- 📱 Support for PostgreSQL, SQLite, and MySQL databases
- 🛠️ Built on top of SQLModel and SQLAlchemy for robust performance
- 📝 Type hints for better IDE support
- 🕒 Automatic `id`, `created_at` and `updated_at` fields provided by default
- ⏰ **PostgreSQL DateTime Compatibility**: Automatic timezone-aware to timezone-naive datetime conversion for PostgreSQL TIMESTAMP WITHOUT TIME ZONE columns
- 🔄 Automatic schema migrations for evolving database models
- 📊 Visualization of database schema using Mermaid ER diagrams
- 📋 **JSON Column Support**: Native support for JSON columns with proper serialization in migrations

## Installation

```bash
pip install async-easy-model
```

## Basic Usage

```python
from async_easy_model import EasyModel, init_db, db_config, Field
from typing import Optional
from datetime import datetime

# Configure your database
db_config.configure_sqlite("database.db")

# Define your model
class User(EasyModel, table=True):
    #no need to specify id, created_at or updated_at since EasyModel provides them by default
    username: str = Field(unique=True)
    email: str

# Initialize your database
async def setup():
    await init_db()

# Use it in your async code
async def main():
    await setup()
    # Create a new user
    user = await User.insert({
        "username": "john_doe",
        "email": "john@example.com"
    })
    
    # Get user ID
    print(f"New user id: {user.id}")
```

## CRUD Operations

First, let's define some models that we'll use throughout the examples:

```python
from async_easy_model import EasyModel, Field
from typing import Optional, List
from datetime import datetime

class User(EasyModel, table=True):
    username: str = Field(unique=True)
    email: str
    is_active: bool = Field(default=True)
    
class Post(EasyModel, table=True):
    title: str
    content: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
class Comment(EasyModel, table=True):
    text: str
    post_id: Optional[int] = Field(default=None, foreign_key="post.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
class Department(EasyModel, table=True):
    name: str = Field(unique=True)
    
class Product(EasyModel, table=True):
    name: str
    price: float
    sales: int = Field(default=0)
    
class Book(EasyModel, table=True):
    title: str
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")
    
class Author(EasyModel, table=True):
    name: str
```

### Create (Insert)

```python
# Insert a single record
user = await User.insert({
    "username": "john_doe",
    "email": "john@example.com"
})

# Insert multiple records
users = await User.insert([
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"}
])

# Insert with nested relationships
new_post = await Post.insert({
    "title": "My Post",
    "content": "Content here",
    "user": {"username": "jane_doe"},  # Will automatically link to existing user
    "comments": [  # Create multiple comments in a single transaction
        {"text": "Great post!", "user": {"username": "reader1"}},
        {"text": "Thanks for sharing", "user": {"username": "reader2"}}
    ]
})
# Access nested data without requerying
print(f"Post by {new_post.user.username} with {len(new_post.comments)} comments")

# Insert with nested one-to-many relationships 
publisher = await Publisher.insert({
    "name": "Example Publisher",
    "books": [  # List of nested objects
        {
            "title": "Python Mastery",
            "genres": [
                {"name": "Programming"},
                {"name": "Education"}
            ]
        },
        {"title": "Data Science Handbook"}
    ]
})
# Access nested relationships immediately
print(f"Publisher: {publisher.name} with {len(publisher.books)} books")
print(f"First book genres: {[g.name for g in publisher.books[0].genres]}")
```

### Read (Retrieve)

```python
# Select by ID
user = await User.select({"id": 1})

# Select with criteria
users = await User.select({"is_active": True}, all=True)

# Select first matching record
first_user = await User.select({"is_active": True}, first=True)

# Select all records
all_users = await User.select({}, all=True)

# Select with wildcard pattern matching
gmail_users = await User.select({"email": "*@gmail.com"}, all=True)

# Select with ordering
recent_users = await User.select({}, order_by="-created_at", all=True)

# Select with limit
latest_posts = await Post.select({}, order_by="-created_at", limit=5)
# Note: limit > 1 automatically sets all=True

# Select with multiple ordering fields
sorted_users = await User.select({}, order_by=["last_name", "first_name"], all=True)

# Select with relationship ordering
posts_by_author = await Post.select({}, order_by="user.username", all=True)
```

### Update

```python
# Update by ID
user = await User.update({"is_active": False}, 1)

# Update by criteria
count = await User.update(
    {"is_active": False},
    {"last_login": None}  # Set all users without login to inactive
)

# Update with relationships
await User.update(
    {"department": {"name": "Sales"}},  # Update department relationship
    {"username": "john_doe"}
)
```

### Delete

```python
# Delete by ID
success = await User.delete(1)

# Delete by criteria
deleted_count = await User.delete({"is_active": False})

# Delete with compound criteria
await Post.delete({"user": {"username": "john_doe"}, "is_published": False})
```

## Database Schema Visualization

The package includes a `ModelVisualizer` class that makes it easy to generate Entity-Relationship (ER) diagrams for your database models using Mermaid syntax.

```python
from async_easy_model import EasyModel, init_db, db_config, ModelVisualizer

# Initialize your models and database
await init_db()

# Create a visualizer
visualizer = ModelVisualizer()

# Generate a Mermaid ER diagram
er_diagram = visualizer.mermaid()
print(er_diagram)

# Generate a shareable link to view the diagram online
er_link = visualizer.mermaid_link()
print(er_link)

# Customize the diagram title
visualizer.set_title("My Project Database Schema")
custom_diagram = visualizer.mermaid()
```

### Example Mermaid ER Diagram Output

```mermaid
---
title: EasyModel Table Schemas
config:
    layout: elk
---
erDiagram
    author {
        number id PK
        string name "required"
        string email
    }
    book {
        number id PK
        string title "required"
        number author_id FK
        string isbn
        number published_year
        author author "virtual"
        tag[] tags "virtual"
    }
    tag {
        number id PK
        string name "required"
        book[] books "virtual"
    }
    book_tag {
        number id PK
        number book_id FK "required"
        number tag_id FK "required"
        book book "virtual"
        tag tag "virtual"
    }
    review {
        number id PK
        number book_id FK "required"
        number rating "required"
        string comment
        string reviewer_name "required"
        book book "virtual"
    }
    book ||--o{ author : "author_id"
    book_tag ||--o{ book : "book_id"
    book_tag ||--o{ tag : "tag_id"
    book }o--o{ tag : "many-to-many"
    review ||--o{ book : "book_id"
```

The diagram automatically:
- Shows all tables with their fields and data types
- Identifies primary keys (PK) and foreign keys (FK)
- Shows required fields and virtual relationships
- Visualizes relationships between tables with proper cardinality
- Properly handles many-to-many relationships

## Convenient Query Methods

async-easy-model provides simplified methods for common query patterns:

```python
# Get all records with relationships loaded (default)
users = await User.all()

# Get all records ordered by a field (ascending)
users = await User.all(order_by="username")

# Get all records ordered by a field (descending)
newest_users = await User.all(order_by="-created_at")

# Get all records ordered by multiple fields
sorted_users = await User.all(order_by=["last_name", "first_name"])

# Get all records ordered by relationship fields
books = await Book.all(order_by="author.name")

# Get the first record 
user = await User.first()

# Get the most recently created user
newest_user = await User.first(order_by="-created_at")

# Get a limited number of records
recent_users = await User.limit(10)

# Get a limited number of records with ordering
top_products = await Product.limit(5, order_by="-sales")
```

## SQLAlchemy/SQLModel Compatibility Layer

**New in v0.4.3**: async-easy-model now includes a compatibility layer that allows you to use familiar SQLAlchemy query patterns alongside EasyModel's simplified API. This enables smooth migration from existing SQLAlchemy/SQLModel code and provides a familiar interface for developers coming from SQLAlchemy backgrounds.

### Query Builder Pattern

The compatibility layer provides a `query()` method that returns an AsyncQuery builder, allowing you to chain filter operations just like SQLAlchemy:

```python
from async_easy_model import EasyModel, Field
from async_easy_model.compat import AsyncQuery  # For IDE type hints (optional)

class User(EasyModel, table=True):
    username: str = Field(index=True)
    email: str
    age: int
    is_active: bool = Field(default=True)

# Use the query builder pattern
users = await User.query().filter(User.age > 25).all()
user = await User.query().filter_by(username="john").first()

# Chain multiple operations
active_adults = await (
    User.query()
    .filter(User.age >= 18)
    .filter(User.is_active == True)
    .order_by(User.username)
    .limit(10)
    .all()
)

# IDE Support Tip (Optional):
# For full IDE autocomplete, add a type annotation:
query: AsyncQuery[User] = User.query()  # Optional - only for IDE support
filtered = query.filter(User.age > 25)  # IDE will show all available methods
```

### Available Methods

The compatibility layer provides all common SQLAlchemy patterns:

#### Query Building Methods
- `filter()` - Filter using SQLAlchemy expressions
- `filter_by()` - Filter using keyword arguments
- `order_by()` - Sort results
- `limit()` - Limit number of results
- `offset()` - Skip results
- `join()` - Join related tables

#### Terminal Methods (async)
- `all()` - Get all matching records
- `first()` - Get first matching record
- `one()` - Get exactly one record (raises if not found)
- `one_or_none()` - Get one record or None
- `count()` - Count matching records
- `exists()` - Check if any records match

#### Instance Methods
```python
user = await User.find(1)
await user.save()           # Save changes to database
await user.refresh()        # Refresh from database
await user.delete_instance() # Delete this record
```

#### Class Methods
```python
# Create new record
user = await User.create(username="jane", email="jane@example.com")

# Find records
user = await User.find(1)  # By ID
user = await User.find_by(username="john")  # By field

# Bulk operations
users = await User.bulk_create([
    {"username": "user1", "email": "user1@example.com"},
    {"username": "user2", "email": "user2@example.com"}
])

# Check existence
exists = await User.exists(username="john")

# Count records
count = await User.count()
```

### SQLAlchemy Statement Builders

For advanced use cases, you can access SQLAlchemy statement builders:

```python
# Get SQLAlchemy select statement
stmt = User.select_stmt().where(User.age > 25)

# Use with session
async with User.session() as session:
    result = await session.execute(stmt)
    users = result.scalars().all()
```

### Mixed Usage Example

You can freely mix EasyModel's simplified API with SQLAlchemy patterns:

```python
# EasyModel style
users = await User.select({"age": {"$gt": 25}})

# SQLAlchemy compatibility style
users = await User.query().filter(User.age > 25).all()

# Both work seamlessly together!
```

## Enhanced Relationship Handling

Using the models defined earlier, here's how to work with relationships:

```python
# Load all relationships automatically
post = await Post.select({"id": 1})
print(post.user.username)  # Access related objects directly

# Load specific relationships
post = await Post.get_with_related(1, ["user", "comments"])

# Load relationships after fetching
post = await Post.select({"id": 1}, include_relationships=False)
await post.load_related(["user", "comments"])

# Insert with nested relationships
new_post = await Post.insert({
    "title": "My Post",
    "content": "Content here",
    "user": {"username": "jane_doe"},  # Will automatically link to existing user
    "comments": [  # Create multiple comments in a single transaction
        {"text": "Great post!", "user": {"username": "reader1"}},
        {"text": "Thanks for sharing", "user": {"username": "reader2"}}
    ]
})
# Access nested data without requerying
print(f"Post by {new_post.user.username} with {len(new_post.comments)} comments")

# Convert to dictionary with nested relationships
post_dict = post.to_dict(include_relationships=True, max_depth=2)
```

## Automatic Relationship Detection

The package can automatically detect and set up bidirectional relationships between models:

```python
class User(EasyModel, table=True):
    username: str

class Post(EasyModel, table=True):
    title: str
    user_id: int = Field(foreign_key="user.id")

# After init_db():
# - post.user relationship is automatically available
# - user.posts relationship is automatically available
```

## Database Configuration

```python
# SQLite Configuration
db_config.configure_sqlite("database.db")
db_config.configure_sqlite(":memory:")  # In-memory database

# PostgreSQL Configuration
db_config.configure_postgres(
    user="your_user",
    password="your_password",
    host="localhost",
    port="5432",
    database="your_database"
)

# MySQL Configuration
db_config.configure_mysql(
    user="your_user",
    password="your_password",
    host="localhost",
    port="3306",
    database="your_database"
)

# Custom Connection URL
db_config.set_connection_url("postgresql+asyncpg://user:password@localhost:5432/database")
```

### Configurable Default for Relationship Loading

**New in v0.3.9**: You can now set a global default for `include_relationships` behavior across all query methods:

```python
# Configure with default_include_relationships=False for better performance
db_config.configure_sqlite("database.db", default_include_relationships=False)

# Or for PostgreSQL
db_config.configure_postgres(
    user="your_user",
    password="your_password",
    host="localhost",
    port="5432",
    database="your_database",
    default_include_relationships=False  # Set global default
)

# Or for MySQL
db_config.configure_mysql(
    user="your_user",
    password="your_password",
    host="localhost",
    port="3306",
    database="your_database",
    default_include_relationships=False  # Set global default
)
```

**Benefits:**
- **Performance**: Set `default_include_relationships=False` to avoid loading relationships by default, improving query performance
- **Flexibility**: Still override per method call with explicit `True` or `False` values
- **Backward Compatible**: Defaults to `True` if not specified, maintaining existing behavior

**Usage Examples:**
```python
# With default_include_relationships=False configured:
users = await User.all()  # No relationships loaded (faster)
users_with_rels = await User.all(include_relationships=True)  # Override to load relationships

# With default_include_relationships=True configured (default behavior):
users = await User.all()  # Relationships loaded
users_no_rels = await User.all(include_relationships=False)  # Override to skip relationships
```

### Database Initialization Options

**New in v0.4.1**: The `init_db()` function now supports configurable auto-relationships handling:

```python
# Default behavior (auto-detect auto-relationships availability)
await init_db()

# Force enable auto-relationships (will warn if not available)
await init_db(has_auto_relationships=True)

# Force disable auto-relationships
await init_db(has_auto_relationships=False)

# Combined with other parameters
await init_db(
    migrate=True,
    model_classes=[User, Post, Comment],
    has_auto_relationships=False
)
```

**Benefits:**
- **Control**: Explicitly enable or disable auto-relationships functionality
- **Reliability**: Auto-relationships errors now issue warnings instead of stopping database initialization
- **Flexibility**: Can be combined with migration control and specific model classes
- **Robust**: Database initialization continues even if auto-relationships fail

**Parameter Priority:**
1. Explicit `has_auto_relationships` parameter (if provided)
2. Auto-detection of auto-relationships availability (default)
3. Fallback to available functionality

## Documentation

For more detailed documentation, please visit the [GitHub repository](https://github.com/puntorigen/easy-model) or refer to the [DOCS.md](https://github.com/puntorigen/easy-model/blob/master/DOCS.md) file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
