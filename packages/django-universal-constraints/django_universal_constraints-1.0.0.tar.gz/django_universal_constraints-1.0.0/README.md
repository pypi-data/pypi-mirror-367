# Django Universal Constraints

Application-level constraint validation for Django backends that don't support conditional/unique constraints.

## Problem & Solution

Some Django database backends (e.g., `django-ydb-backend`) lack support for conditional/unique constraints, causing migrations to fail when models define `UniqueConstraint`. This library provides transparent application-level validation that works with any Django backend.

**Solution**: Automatic constraint interception during app startup, with validation via Django's `pre_save` signal system.

## Technical Architecture

### App Startup Integration
- Constraints are discovered and converted during Django app initialization (`apps.py` ready method)
- Django's `UniqueConstraint` and `unique_together` definitions are automatically converted to application-level validators (`UniversalConstraint`)
- Original model definitions remain unchanged

### Signal-Based Validation
- `pre_save` signal intercepts all model saves before database write
- Constraint validation occurs via additional SELECT queries
- Validation respects Django's database routing system

### Database Constraint Handling
Two operational modes:

1. **With Backend Wrapper**: Database constraints are intercepted during migrations and removed from schema
2. **Without Wrapper**: Database constraints remain (may cause errors on unsupported backends)

### Performance Characteristics
- **Additional Queries**: 1-2 SELECT queries per save operation for constraint validation
- **Race Condition Protection**: Optional `select_for_update()` adds database locking overhead
- **Memory Overhead**: Minimal (constraint metadata stored per model class)

## Installation

```bash
pip install django-universal-constraints
```

## Configuration

### Required: INSTALLED_APPS
**Critical**: `universal_constraints` must be placed LAST in `INSTALLED_APPS`, after all applications that define models:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... your apps with models
    'myapp',
    'anotherapp',
    # Must be last:
    'universal_constraints',
]
```

### Optional: Per-Database Settings
```python
UNIVERSAL_CONSTRAINTS = {
    'database_alias': {
        'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        'RACE_CONDITION_PROTECTION': True,  # Default: True
        'REMOVE_DB_CONSTRAINTS': True,      # Default: True (requires wrapper)
        'LOG_LEVEL': 'INFO',
    }
}
```

### Backend Wrapper (for REMOVE_DB_CONSTRAINTS)
```python
DATABASES = {
    'default': {
        'ENGINE': 'universal_constraints.backend',
        'WRAPPED_ENGINE': 'your.actual.backend',  # e.g., 'django.db.backends.sqlite3'
        'NAME': 'db.sqlite3',
        # ... other backend-specific settings
    }
}
```

## Usage (Simple)
After adding `universal_constraints` to `INSTALLED_APPS` and configuring your database settings, the auto-discovery system automatically runs during Django startup. No additional setup is required - your existing model constraints will be automatically converted to application-level validation.

## Usage (Advanced)

### Programmatic Constraint Addition
```python
from universal_constraints.validators import add_universal_constraint

add_universal_constraint(
    User,
    fields=['username'],
    condition=Q(is_active=True),
    name='unique_active_username'
) # Adds a UniversalConstraint for the User model. If Users have is_active=True, then usernames must be unique
```

### Multi-Database Configuration
```python
DATABASES = {
    'postgres_db': {
        'ENGINE': 'django.db.backends.postgresql',
        # PostgreSQL supports constraints natively
    },
    'ydb_database': {
        'ENGINE': 'universal_constraints.backend',
        'WRAPPED_ENGINE': 'ydb_backend.backend',
        # YDB constraints handled at application level
    }
}

UNIVERSAL_CONSTRAINTS = {
    # No entry for 'postgres_db' - uses native constraints
    'ydb_database': {
        'REMOVE_DB_CONSTRAINTS': True,
        'RACE_CONDITION_PROTECTION': True,
    }
}
```

## Race Condition Protection

### When to Enable
- **High Concurrency**: Multiple processes/threads modifying same constraint fields
- **Critical Data Integrity**: When constraint violations must be prevented

### How It Works
- Uses `select_for_update()` to create database row locks
- Prevents race conditions across different processes/transactions
- Blocks concurrent validation until transaction completes

### Performance Impact
- **Additional Overhead**: Database locking adds latency
- **Recommendation**: Enable for critical constraints, disable for high-throughput scenarios
- **Fallback**: Gracefully degrades to non-protected validation if locking fails

```python
UNIVERSAL_CONSTRAINTS = {
    'default': {
        'RACE_CONDITION_PROTECTION': True,  # Enable for critical data
    }
}
```

## Implementation Limitations

### Q-Object Evaluation
Supports common Django field lookups:
- `exact`, `isnull`, `in`, `gt`, `gte`, `lt`, `lte`
- **Limitation**: Complex lookups fall back to "assume condition applies"
- **Behavior**: Conservative approach prevents false negatives

### Performance vs Native Constraints
- **Application-level**: 1-2 additional SELECT queries per save
- **Database-level**: Zero query overhead, handled by database engine
- **Trade-off**: Compatibility vs performance

## Management Commands

### Constraint Discovery
```bash
python manage.py discover_constraints
python manage.py discover_constraints --format=json
```

## Supported Backends

- ✅ SQLite (`django.db.backends.sqlite3`)
- ✅ PostgreSQL (`django.db.backends.postgresql`)
- ✅ MySQL (`django.db.backends.mysql`)
- ✅ YDB (`django-ydb-backend`)
- ✅ Any Django-compatible backend

## Testing (and development)

Run the test suite:

```bash
uv sync
uv run tests/runtests.py
```

## Troubleshooting

### Common Issues
- **"No such table" errors**: Ensure `universal_constraints` is last in `INSTALLED_APPS`
- **Constraints not validated**: Check database is configured in `UNIVERSAL_CONSTRAINTS`
- **Migration failures**: Use backend wrapper with `REMOVE_DB_CONSTRAINTS=True`

### Debug Logging
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'universal_constraints': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```