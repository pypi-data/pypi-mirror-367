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
All constraints are handled at the application level only. The library provides app-level validation via Django signals, while leaving the original constraint definitions in your models unchanged.

**Database Backend Responsibility**: How constraints are handled at the database level depends entirely on the database backend being used:
- Some backends may skip unsupported constraints during migrations (no error)
- Some backends may add supported constraints to the database schema
- Some backends may raise errors for unsupported constraint types

This is now the responsibility of the individual database backend, not this library. The library focuses purely on providing reliable application-level validation that works consistently across all backends.

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
        'LOG_LEVEL': 'INFO',
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
    },
    'ydb_database': {
        'ENGINE': 'ydb_backend.backend',
    }
}

UNIVERSAL_CONSTRAINTS = {
    'postgres_db': {
        'RACE_CONDITION_PROTECTION': False,
    },
    'ydb_database': {
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
- **Migration failures**: May occur with backends that don't support conditional constraints

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
