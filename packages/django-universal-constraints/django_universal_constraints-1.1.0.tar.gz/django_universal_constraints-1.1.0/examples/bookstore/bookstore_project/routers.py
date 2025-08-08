"""
Database router for the bookstore project.

This router demonstrates how to split models across multiple databases
to showcase different universal_constraints configurations.
"""


class DatabaseRouter:
    """
    A router to control all database operations on models for different
    databases to demonstrate universal_constraints functionality.
    """

    # Apps that should use the second_database
    other_apps = {'inventory', 'customers'}

    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if model._meta.app_label in self.other_apps:
            return 'second_database'
        return 'default'

    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if model._meta.app_label in self.other_apps:
            return 'second_database'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app or both in default."""
        db_set = {'default', 'second_database'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label in self.other_apps:
            return db == 'second_database'
        elif db == 'other_database':
            return False
        return db == 'default'
