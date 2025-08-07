"""
Tests for universal_constraints.validators module.
"""

from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint

from universal_constraints.validators import (
    UniversalConstraint,
    UniversalConstraintValidatorMixin,
    validate_universal_constraints,
    add_universal_constraint
)


class ValidatorTestModel(models.Model):
    """Test model for constraint validation."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        app_label = 'tests'


class ValidatorTestModelWithConstraints(models.Model):
    """Test model with predefined constraints."""
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        app_label = 'tests'
    
    # Add constraints after class definition
    _universal_constraints = [
        UniversalConstraint(
            fields=['name'],
            condition=Q(is_active=True),
            name='unique_active_name'
        )
    ]


class UniversalConstraintTest(TestCase):
    """Test the UniversalConstraint class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.constraint = UniversalConstraint(
            fields=['email'],
            condition=Q(is_active=True),
            name='validator_unique_active_email'
        )
    
    def test_constraint_creation(self):
        """Test constraint creation and properties."""
        self.assertEqual(self.constraint.fields, ['email'])
        self.assertEqual(self.constraint.name, 'validator_unique_active_email')
        self.assertIsNotNone(self.constraint.condition)
    
    def test_constraint_without_condition(self):
        """Test constraint creation without condition."""
        constraint = UniversalConstraint(fields=['name'])
        self.assertEqual(constraint.fields, ['name'])
        self.assertEqual(constraint.name, 'unique_name')
        self.assertIsNone(constraint.condition)
    
    def test_constraint_auto_naming(self):
        """Test automatic constraint naming."""
        # With condition
        constraint = UniversalConstraint(
            fields=['name', 'email'],
            condition=Q(is_active=True)
        )
        self.assertEqual(constraint.name, 'unique_name_email_conditional')
        
        # Without condition
        constraint = UniversalConstraint(fields=['name', 'email'])
        self.assertEqual(constraint.name, 'unique_name_email')
    
    def test_string_representation(self):
        """Test string representation of constraint."""
        str_repr = str(self.constraint)
        self.assertIn('validator_unique_active_email', str_repr)
        self.assertIn('UNIQUE(email)', str_repr)
        self.assertIn('WHERE', str_repr)
    
    def test_condition_evaluation_simple(self):
        """Test simple condition evaluation."""
        instance = ValidatorTestModel(email='test@example.com', is_active=True)
        self.assertTrue(self.constraint._condition_applies(instance))
        
        instance.is_active = False
        self.assertFalse(self.constraint._condition_applies(instance))
    
    def test_condition_evaluation_complex(self):
        """Test complex condition evaluation."""
        constraint = UniversalConstraint(
            fields=['email'],
            condition=Q(is_active=True) & Q(category='premium'),
            name='complex_constraint'
        )
        
        # Both conditions true
        instance = ValidatorTestModel(email='test@example.com', is_active=True, category='premium')
        self.assertTrue(constraint._condition_applies(instance))
        
        # One condition false
        instance.category = 'basic'
        self.assertFalse(constraint._condition_applies(instance))
        
        # Other condition false
        instance.category = 'premium'
        instance.is_active = False
        self.assertFalse(constraint._condition_applies(instance))
    
    def test_condition_evaluation_or(self):
        """Test OR condition evaluation."""
        constraint = UniversalConstraint(
            fields=['email'],
            condition=Q(is_active=True) | Q(category='premium'),
            name='or_constraint'
        )
        
        # First condition true
        instance = ValidatorTestModel(email='test@example.com', is_active=True, category='basic')
        self.assertTrue(constraint._condition_applies(instance))
        
        # Second condition true
        instance.is_active = False
        instance.category = 'premium'
        self.assertTrue(constraint._condition_applies(instance))
        
        # Both false
        instance.category = 'basic'
        self.assertFalse(constraint._condition_applies(instance))
    
    def test_field_lookups(self):
        """Test various field lookup operators."""
        # Test isnull
        constraint = UniversalConstraint(
            fields=['email'],
            condition=Q(category__isnull=True),
            name='null_constraint'
        )
        
        instance = ValidatorTestModel(email='test@example.com', category=None)
        self.assertTrue(constraint._condition_applies(instance))
        
        instance.category = 'premium'
        self.assertFalse(constraint._condition_applies(instance))
        
        # Test in
        constraint = UniversalConstraint(
            fields=['email'],
            condition=Q(category__in=['premium', 'gold']),
            name='in_constraint'
        )
        
        instance.category = 'premium'
        self.assertTrue(constraint._condition_applies(instance))
        
        instance.category = 'basic'
        self.assertFalse(constraint._condition_applies(instance))
    
    def test_validation_without_race_protection(self):
        """Test constraint validation without race condition protection."""
        # Create first instance
        instance1 = ValidatorTestModel.objects.create(
            name='Test',
            email='test@example.com',
            is_active=True
        )
        
        # Try to create second instance with same email (should fail)
        instance2 = ValidatorTestModel(
            name='Test2',
            email='test@example.com',
            is_active=True
        )
        
        with self.assertRaises(ValidationError) as cm:
            self.constraint.validate(instance2, use_race_protection=False)
        
        self.assertIn('unique', str(cm.exception).lower())
    
    def test_validation_condition_not_applies(self):
        """Test validation when condition doesn't apply."""
        # Create first instance
        ValidatorTestModel.objects.create(
            name='Test',
            email='test@example.com',
            is_active=True
        )
        
        # Create second instance with same email but inactive (should pass)
        instance2 = ValidatorTestModel(
            name='Test2',
            email='test@example.com',
            is_active=False
        )
        
        # Should not raise ValidationError
        self.constraint.validate(instance2, use_race_protection=False)
    
    def test_validation_exclude_current_instance(self):
        """Test that validation excludes the current instance when updating."""
        # Create instance
        instance = ValidatorTestModel.objects.create(
            name='Test',
            email='test@example.com',
            is_active=True
        )
        
        # Update same instance (should pass)
        instance.name = 'Updated Test'
        self.constraint.validate(instance, use_race_protection=False)
    
    def test_validation_with_race_protection(self):
        """Test constraint validation with race condition protection."""
        # Create first instance
        ValidatorTestModel.objects.create(
            name='Test',
            email='test@example.com',
            is_active=True
        )
        
        # Try to create second instance with same email (should fail)
        instance2 = ValidatorTestModel(
            name='Test2',
            email='test@example.com',
            is_active=True
        )
        
        with self.assertRaises(ValidationError):
            self.constraint.validate(instance2, use_race_protection=True)


class UniversalConstraintValidatorMixinTest(TestCase):
    """Test the UniversalConstraintValidatorMixin."""
    
    def test_mixin_validation_in_clean(self):
        """Test that mixin validates constraints in clean method."""
        # Create a simple test model that extends the mixin
        class TestModelWithMixin(UniversalConstraintValidatorMixin, ValidatorTestModel):
            class Meta:
                proxy = True
                app_label = 'tests'
            
            _universal_constraints = [
                UniversalConstraint(
                    fields=['name'],
                    condition=Q(is_active=True),
                    name='unique_active_name'
                )
            ]
        
        # Create first instance using the base model
        ValidatorTestModel.objects.create(name='Test', is_active=True)
        
        # Try to create second instance with same name using the mixin
        instance2 = TestModelWithMixin(name='Test', is_active=True)
        
        with self.assertRaises(ValidationError):
            instance2.clean()


class SignalHandlerTest(TestCase):
    """Test the signal handler for automatic validation."""
    
    def test_signal_handler_function_directly(self):
        """Test the signal handler function directly."""
        # Create first instance with the model that has constraints
        ValidatorTestModelWithConstraints.objects.create(name='Test', is_active=True)
        
        # Test the signal handler function directly
        from unittest.mock import patch
        
        with patch('universal_constraints.settings.constraint_settings') as mock_settings:
            # Mock settings to enable validation
            mock_settings.is_database_enabled.return_value = True
            mock_settings.get_setting.return_value = False  # No race protection
            
            # The signal handler should validate if constraints exist
            # Create a second instance with the same name (should violate constraint)
            duplicate_instance = ValidatorTestModelWithConstraints(name='Test', is_active=True)
            
            with self.assertRaises(ValidationError):
                validate_universal_constraints(
                    sender=ValidatorTestModelWithConstraints,
                    instance=duplicate_instance,
                    using='default'
                )
    
    def test_signal_handler_disabled_database(self):
        """Test that signal handler skips validation for disabled databases."""
        from unittest.mock import patch
        
        instance = ValidatorTestModelWithConstraints(name='Test', is_active=True)
        
        with patch('universal_constraints.settings.constraint_settings') as mock_settings:
            # Mock settings to disable validation
            mock_settings.is_database_enabled.return_value = False
            
            # Should not raise ValidationError when disabled
            validate_universal_constraints(
                sender=ValidatorTestModelWithConstraints,
                instance=instance,
                using='default'
            )
    
    def test_signal_handler_no_constraints(self):
        """Test signal handler with model that has no constraints."""
        from unittest.mock import patch
        
        instance = ValidatorTestModel(name='Test', is_active=True)
        
        with patch('universal_constraints.settings.constraint_settings') as mock_settings:
            mock_settings.is_database_enabled.return_value = True
            
            # Should not raise ValidationError when no constraints exist
            validate_universal_constraints(
                sender=ValidatorTestModel,
                instance=instance,
                using='default'
            )


class UtilityFunctionTest(TestCase):
    """Test utility functions."""
    
    def setUp(self):
        """Set up test fixtures and ensure clean model state."""
        # Store original state of the model class
        self.original_constraints = getattr(ValidatorTestModel, '_universal_constraints', None)
        
        # Ensure the model starts clean for each test
        if hasattr(ValidatorTestModel, '_universal_constraints'):
            delattr(ValidatorTestModel, '_universal_constraints')
    
    def tearDown(self):
        """Clean up after each test."""
        # Remove any constraints added during the test
        if hasattr(ValidatorTestModel, '_universal_constraints'):
            delattr(ValidatorTestModel, '_universal_constraints')
        
        # Restore original state if it existed
        if self.original_constraints is not None:
            ValidatorTestModel._universal_constraints = self.original_constraints
    
    def test_add_universal_constraint(self):
        """Test adding constraints dynamically to models."""
        # Initially no constraints
        self.assertFalse(hasattr(ValidatorTestModel, '_universal_constraints'))
        
        # Add constraint
        add_universal_constraint(
            ValidatorTestModel,
            fields=['name'],
            condition=Q(is_active=True),
            name='dynamic_constraint'
        )
        
        # Check constraint was added
        self.assertTrue(hasattr(ValidatorTestModel, '_universal_constraints'))
        constraints = ValidatorTestModel._universal_constraints
        self.assertEqual(len(constraints), 1)
        self.assertEqual(constraints[0].name, 'dynamic_constraint')
        self.assertEqual(constraints[0].fields, ['name'])
    
    def test_add_multiple_constraints(self):
        """Test adding multiple constraints to the same model."""
        # Clear any existing constraints from previous tests
        if hasattr(ValidatorTestModel, '_universal_constraints'):
            delattr(ValidatorTestModel, '_universal_constraints')
        
        add_universal_constraint(
            ValidatorTestModel,
            fields=['name'],
            name='constraint1'
        )
        
        add_universal_constraint(
            ValidatorTestModel,
            fields=['email'],
            name='constraint2'
        )
        
        constraints = ValidatorTestModel._universal_constraints
        self.assertEqual(len(constraints), 2)
        constraint_names = [c.name for c in constraints]
        self.assertIn('constraint1', constraint_names)
        self.assertIn('constraint2', constraint_names)
