"""
Django app for unique/conditional constraint validation.

This app provides application-level validation for constraints,
which is useful for database backends that don't support them natively.
"""

default_app_config = 'universal_constraints.apps.UniqueConstraintsConfig'
