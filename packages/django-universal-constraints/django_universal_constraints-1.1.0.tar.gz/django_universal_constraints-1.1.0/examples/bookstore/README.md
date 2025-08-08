# Bookstore Example - Django Universal Constraints

This example demonstrates a complete Django project using `django-universal-constraints` with real-world constraint scenarios across multiple apps.

The bookstore includes a single, comprehensive End-to-End test that demonstrates all constraint types working together in a realistic scenario across two databases with some routing.

## Project Structure

```
bookstore/
├── manage.py                    # Django management script
├── bookstore_project/          # Main Django project
│   ├── settings.py             # Project settings with universal constraints
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI configuration
├── books/                      # Books and authors management
│   ├── models.py               # Author, Book, BookEdition, Review models
│   ├── admin.py                # Django admin integration
│   ├── views.py                # Web views
│   └── urls.py                 # App URLs
├── inventory/                  # Stock and location management
│   ├── models.py               # Location, Stock models
│   ├── admin.py                # Admin interface
│   └── urls.py                 # App URLs
├── customers/                  # Customer and order management
│   ├── models.py               # Customer, Order models
│   ├── admin.py                # Admin interface
│   └── urls.py                 # App URLs
└── bookstore.sqlite3           # SQLite database (created after migration)
```

## Constraint Examples

### Books App Constraints

**Author Model:**
- Active authors must have unique email addresses
- Inactive authors can share email addresses

**Book Model:**
- Published books must have unique ISBN numbers
- Each author can only have one book with the same title

**BookEdition Model:**
- Only one active edition per format per book
- Multiple inactive editions allowed

**Review Model:**
- One published review per book per reviewer
- Multiple draft reviews allowed

### Inventory App Constraints

**Location Model:**
- Active locations must have unique names
- Inactive locations can share names

**Stock Model:**
- One active stock record per book per location
- Historical stock records preserved

### Customers App Constraints

**Customer Model:**
- Verified customers need unique email addresses
- Active customers need unique usernames

**Order Model:**
- One active order per customer per order number
- Completed orders can share order numbers

## Try It

```bash
uv sync
uv run manage.py test test_bookstore_e2e
```

**What the E2E test demonstrates:**
- ✅ **Conditional Constraints**: Author emails (active only), Stock records (active only)
- ✅ **Non-conditional Constraints**: Book ISBNs, Location codes
- ✅ **unique_together Constraints**: Book title+author, Customer data, Orders
- ✅ **Multi-Database Routing**: Books on 'default', Inventory+Customers on 'second_database'
- ✅ **Real-world Scenarios**: Complete bookstore workflow with constraint validation

The test tells a complete story:
1. **Author Management**: Create authors, test email uniqueness for active authors only
2. **Book Management**: Create books, test ISBN uniqueness and title+author combinations
3. **Inventory Management**: Create locations and stock, test conditional stock constraints
4. **Customer Management**: Create customers, test username+email and phone uniqueness
5. **Order Management**: Create orders, test order_number+customer combinations

**No test isolation needed** - it's one continuous story that builds up data and shows how constraints protect data integrity across all models and databases.
