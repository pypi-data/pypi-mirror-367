"""
Tests for universal_constraints.utils module.
"""

from django.test import TestCase, override_settings
from django.db import models
from django.db.models import UniqueConstraint, Q
from unittest.mock import patch, MagicMock

from universal_constraints.utils import (
    should_process_model_for_database,
    get_database_constraint_status,
    collect_models_for_database,
    should_process_model
)
from universal_constraints.constraint_converter import has_universal_constraints


class UtilsTestModel(models.Model):
    """Test model for utils testing."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'tests'
        constraints = [
            UniqueConstraint(
                fields=['email'],
                condition=Q(is_active=True),
                name='utils_unique_active_email'
            )
        ]


class UtilsTestModelNoConstraints(models.Model):
    """Test model without constraints."""
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'tests'


class ShouldProcessModelForDatabaseTest(TestCase):
    """Test the should_process_model_for_database function."""
    
    def test_default_database_routing(self):
        """Test routing when router returns None (default behavior)."""
        with patch('django.db.router') as mock_router:
            mock_router.db_for_read.return_value = None
            mock_router.db_for_write.return_value = None
            
            # Should process for 'default' database only
            self.assertTrue(should_process_model_for_database(UtilsTestModel, 'default'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'other'))
    
    def test_specific_database_routing_read(self):
        """Test routing when router specifies read database."""
        with patch('django.db.router') as mock_router:
            mock_router.db_for_read.return_value = 'specific_db'
            mock_router.db_for_write.return_value = None
            
            # Should process for the specified read database
            self.assertTrue(should_process_model_for_database(UtilsTestModel, 'specific_db'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'default'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'other'))
    
    def test_specific_database_routing_write(self):
        """Test routing when router specifies write database."""
        with patch('django.db.router') as mock_router:
            mock_router.db_for_read.return_value = None
            mock_router.db_for_write.return_value = 'write_db'
            
            # Should process for the specified write database
            self.assertTrue(should_process_model_for_database(UtilsTestModel, 'write_db'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'default'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'other'))
    
    def test_both_read_write_routing(self):
        """Test routing when router specifies both read and write databases."""
        with patch('django.db.router') as mock_router:
            mock_router.db_for_read.return_value = 'read_db'
            mock_router.db_for_write.return_value = 'write_db'
            
            # Should process for both read and write databases
            self.assertTrue(should_process_model_for_database(UtilsTestModel, 'read_db'))
            self.assertTrue(should_process_model_for_database(UtilsTestModel, 'write_db'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'default'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'other'))
    
    def test_same_read_write_database(self):
        """Test routing when read and write point to same database."""
        with patch('django.db.router') as mock_router:
            mock_router.db_for_read.return_value = 'same_db'
            mock_router.db_for_write.return_value = 'same_db'
            
            # Should process for the specified database
            self.assertTrue(should_process_model_for_database(UtilsTestModel, 'same_db'))
            self.assertFalse(should_process_model_for_database(UtilsTestModel, 'default'))


class GetDatabaseConstraintStatusTest(TestCase):
    """Test the get_database_constraint_status function."""
    
    @override_settings(DATABASES={
        'test_db': {
            'ENGINE': 'universal_constraints.backend',
            'WRAPPED_ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    })
    def test_remove_constraints_with_wrapper(self):
        """Test status when REMOVE_DB_CONSTRAINTS=True and using wrapper."""
        db_settings = {'REMOVE_DB_CONSTRAINTS': True}
        status = get_database_constraint_status('test_db', db_settings)
        self.assertEqual(status, "constraints removed from DB schema")
    
    @override_settings(DATABASES={
        'test_db': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    })
    def test_remove_constraints_without_wrapper(self):
        """Test status when REMOVE_DB_CONSTRAINTS=True but not using wrapper."""
        db_settings = {'REMOVE_DB_CONSTRAINTS': True}
        status = get_database_constraint_status('test_db', db_settings)
        self.assertEqual(status, "constraints kept in DB schema (no wrapper)")
    
    @override_settings(DATABASES={
        'test_db': {
            'ENGINE': 'universal_constraints.backend',
            'WRAPPED_ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    })
    def test_keep_constraints_with_wrapper(self):
        """Test status when REMOVE_DB_CONSTRAINTS=False even with wrapper."""
        db_settings = {'REMOVE_DB_CONSTRAINTS': False}
        status = get_database_constraint_status('test_db', db_settings)
        self.assertEqual(status, "constraints kept in DB schema")
    
    @override_settings(DATABASES={
        'test_db': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'test_db',
        }
    })
    def test_keep_constraints_default(self):
        """Test default status (keep constraints)."""
        db_settings = {}  # No REMOVE_DB_CONSTRAINTS setting
        status = get_database_constraint_status('test_db', db_settings)
        self.assertEqual(status, "constraints kept in DB schema")
    
    def test_missing_database_config(self):
        """Test behavior when database config is missing."""
        db_settings = {'REMOVE_DB_CONSTRAINTS': True}
        status = get_database_constraint_status('nonexistent_db', db_settings)
        self.assertEqual(status, "constraints kept in DB schema (no wrapper)")


class CollectModelsForDatabaseTest(TestCase):
    """Test the collect_models_for_database function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_constraint_settings = MagicMock()
    
    @patch('universal_constraints.utils.apps.get_models')
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_collect_models_basic(self, mock_should_process, mock_get_models):
        """Test basic model collection."""
        # Mock apps.get_models to return our test models
        mock_get_models.return_value = [UtilsTestModel, UtilsTestModelNoConstraints]
        
        # Mock should_process_model_for_database to return True for both
        mock_should_process.return_value = True
        
        # Mock constraint_settings.should_process_app to return True
        self.mock_constraint_settings.should_process_app.return_value = True
        
        models = collect_models_for_database('test_db', self.mock_constraint_settings)
        
        # Should only return models with constraints
        self.assertEqual(len(models), 1)
        self.assertIn(UtilsTestModel, models)
        self.assertNotIn(UtilsTestModelNoConstraints, models)
    
    @patch('universal_constraints.utils.apps.get_models')
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_collect_models_app_filtering(self, mock_should_process, mock_get_models):
        """Test model collection with app filtering."""
        mock_get_models.return_value = [UtilsTestModel]
        mock_should_process.return_value = True
        
        # Mock constraint_settings to exclude the app
        self.mock_constraint_settings.should_process_app.return_value = False
        
        models = collect_models_for_database('test_db', self.mock_constraint_settings)
        
        # Should return empty list due to app filtering
        self.assertEqual(len(models), 0)
    
    @patch('universal_constraints.utils.apps.get_models')
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_collect_models_database_routing_filtering(self, mock_should_process, mock_get_models):
        """Test model collection with database routing filtering."""
        mock_get_models.return_value = [UtilsTestModel]
        
        # Mock should_process_model_for_database to return False (wrong database)
        mock_should_process.return_value = False
        
        self.mock_constraint_settings.should_process_app.return_value = True
        
        models = collect_models_for_database('test_db', self.mock_constraint_settings)
        
        # Should return empty list due to database routing
        self.assertEqual(len(models), 0)
    
    @patch('universal_constraints.utils.apps.get_models')
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_collect_models_no_constraints(self, mock_should_process, mock_get_models):
        """Test model collection when models have no constraints."""
        mock_get_models.return_value = [UtilsTestModelNoConstraints]
        mock_should_process.return_value = True
        self.mock_constraint_settings.should_process_app.return_value = True
        
        models = collect_models_for_database('test_db', self.mock_constraint_settings)
        
        # Should return empty list since model has no constraints
        self.assertEqual(len(models), 0)


class ShouldProcessModelTest(TestCase):
    """Test the should_process_model function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_constraint_settings = MagicMock()
    
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_should_process_model_both_true(self, mock_should_process_db):
        """Test when both constraint_settings and database routing return True."""
        self.mock_constraint_settings.should_process_model.return_value = True
        mock_should_process_db.return_value = True
        
        result = should_process_model(UtilsTestModel, 'test_db', self.mock_constraint_settings)
        
        self.assertTrue(result)
        self.mock_constraint_settings.should_process_model.assert_called_once_with(UtilsTestModel, 'test_db')
        mock_should_process_db.assert_called_once_with(UtilsTestModel, 'test_db')
    
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_should_process_model_constraint_settings_false(self, mock_should_process_db):
        """Test when constraint_settings returns False."""
        self.mock_constraint_settings.should_process_model.return_value = False
        mock_should_process_db.return_value = True
        
        result = should_process_model(UtilsTestModel, 'test_db', self.mock_constraint_settings)
        
        self.assertFalse(result)
        self.mock_constraint_settings.should_process_model.assert_called_once_with(UtilsTestModel, 'test_db')
        # should_process_model_for_database should NOT be called when constraint_settings returns False
        mock_should_process_db.assert_not_called()
    
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_should_process_model_database_routing_false(self, mock_should_process_db):
        """Test when database routing returns False."""
        self.mock_constraint_settings.should_process_model.return_value = True
        mock_should_process_db.return_value = False
        
        result = should_process_model(UtilsTestModel, 'test_db', self.mock_constraint_settings)
        
        self.assertFalse(result)
        self.mock_constraint_settings.should_process_model.assert_called_once_with(UtilsTestModel, 'test_db')
        mock_should_process_db.assert_called_once_with(UtilsTestModel, 'test_db')
    
    @patch('universal_constraints.utils.should_process_model_for_database')
    def test_should_process_model_both_false(self, mock_should_process_db):
        """Test when both constraint_settings and database routing return False."""
        self.mock_constraint_settings.should_process_model.return_value = False
        mock_should_process_db.return_value = False
        
        result = should_process_model(UtilsTestModel, 'test_db', self.mock_constraint_settings)
        
        self.assertFalse(result)
        self.mock_constraint_settings.should_process_model.assert_called_once_with(UtilsTestModel, 'test_db')
        # should_process_model_for_database should NOT be called when constraint_settings returns False
        mock_should_process_db.assert_not_called()


class UtilsIntegrationTest(TestCase):
    """Integration tests for utils functions working together."""
    
    @patch('universal_constraints.utils.apps.get_models')
    def test_integration_with_real_constraint_settings(self, mock_get_models):
        """Test utils functions with real constraint settings."""
        from universal_constraints.settings import constraint_settings
        
        mock_get_models.return_value = [UtilsTestModel, UtilsTestModelNoConstraints]
        
        with patch('django.db.router') as mock_router:
            mock_router.db_for_read.return_value = None
            mock_router.db_for_write.return_value = None
            
            # Test collect_models_for_database with real settings
            models = collect_models_for_database('default', constraint_settings)
            
            # Should collect models with constraints that aren't in excluded apps
            # The exact result depends on the current constraint_settings configuration
            self.assertIsInstance(models, list)
            
            # Test should_process_model with real settings
            if models:  # If any models were collected
                result = should_process_model(models[0], 'default', constraint_settings)
                self.assertIsInstance(result, bool)
