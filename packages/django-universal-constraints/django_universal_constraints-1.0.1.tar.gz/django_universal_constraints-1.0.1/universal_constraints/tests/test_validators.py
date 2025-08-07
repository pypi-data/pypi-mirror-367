"""
Tests for the validators module.
"""

from django.test import TestCase, TransactionTestCase
from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError
from django.core.management.color import no_style
from django.db import connection
from unittest.mock import patch

from universal_constraints.validators import (
    UniversalConstraint,
    UniversalConstraintValidatorMixin,
    add_universal_constraint
)


# Test models - only used for testing the library
class Product(models.Model):
    """Test model for universal constraints."""
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'universal_constraints'


class User(UniversalConstraintValidatorMixin, models.Model):
    """Test model using the mixin approach."""
    email = models.EmailField()
    username = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'universal_constraints'


class Document(models.Model):
    """Test model with complex conditional constraints."""
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        default='draft'
    )
    author = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'universal_constraints'


class UniversalConstraintTests(TestCase):
    """Test the UniversalConstraint class."""
    
    def test_create_constraint_with_condition(self):
        """Test creating a constraint with a condition."""
        constraint = UniversalConstraint(
            fields=['email'],
            condition=models.Q(is_active=True),
            name='unique_active_email'
        )
        
        self.assertEqual(constraint.fields, ['email'])
        self.assertEqual(constraint.name, 'unique_active_email')
        self.assertIsNotNone(constraint.condition)
    
    def test_create_constraint_without_condition(self):
        """Test creating a constraint without a condition."""
        constraint = UniversalConstraint(
            fields=['name', 'category'],
            condition=None,
            name='unique_name_category'
        )
        
        self.assertEqual(constraint.fields, ['name', 'category'])
        self.assertEqual(constraint.name, 'unique_name_category')
        self.assertIsNone(constraint.condition)
    
    def test_constraint_str_representation(self):
        """Test string representation of constraint."""
        constraint = UniversalConstraint(
            fields=['email'],
            condition=models.Q(is_active=True),
            name='unique_active_email'
        )
        
        str_repr = str(constraint)
        self.assertIn('unique_active_email', str_repr)
        self.assertIn('email', str_repr)
    
    def test_constraint_repr(self):
        """Test repr of constraint."""
        constraint = UniversalConstraint(
            fields=['email'],
            condition=models.Q(is_active=True),
            name='unique_active_email'
        )
        
        repr_str = repr(constraint)
        self.assertIn('UniversalConstraint', repr_str)
        self.assertIn('unique_active_email', repr_str)


class UniversalConstraintValidationTests(TransactionTestCase):
    """Test the UniversalConstraint validation."""
    
    def setUp(self):
        """Create database tables for test models."""
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Product)
            schema_editor.create_model(User)
            schema_editor.create_model(Document)
    
    def tearDown(self):
        """Clean up database tables."""
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Product)
            schema_editor.delete_model(User)
            schema_editor.delete_model(Document)
    
    def test_validate_conditional_constraint_pass(self):
        """Test validation passes when no conflicts exist."""
        constraint = UniversalConstraint(
            fields=['name'],
            condition=models.Q(is_active=True),
            name='unique_active_name'
        )
        
        # Create a test instance using existing Product model
        instance = Product(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Should not raise any exception
        try:
            constraint.validate(instance)
        except ValidationError:
            self.fail("Validation should have passed")
    
    def test_validate_conditional_constraint_fail(self):
        """Test validation fails when conflicts exist."""
        constraint = UniversalConstraint(
            fields=['name'],
            condition=models.Q(is_active=True),
            name='unique_active_name'
        )
        
        # Create an existing instance
        existing = Product.objects.create(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Try to create another instance with same name and is_active=True
        instance = Product(
            name='Test Product',
            is_active=True,
            category='B'
        )
        
        with self.assertRaises(ValidationError):
            constraint.validate(instance)
    
    def test_validate_conditional_constraint_condition_not_met(self):
        """Test validation passes when condition is not met."""
        constraint = UniversalConstraint(
            fields=['name'],
            condition=models.Q(is_active=True),
            name='unique_active_name'
        )
        
        # Create an existing instance
        existing = Product.objects.create(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Try to create another instance with same name but is_active=False
        instance = Product(
            name='Test Product',
            is_active=False,  # Condition not met
            category='B'
        )
        
        # Should not raise any exception
        try:
            constraint.validate(instance)
        except ValidationError:
            self.fail("Validation should have passed when condition is not met")
    
    def test_validate_non_conditional_constraint_fail(self):
        """Test validation fails for non-conditional constraints."""
        constraint = UniversalConstraint(
            fields=['name', 'category'],
            condition=None,
            name='unique_name_category'
        )
        
        # Create an existing instance
        existing = Product.objects.create(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Try to create another instance with same name and category
        instance = Product(
            name='Test Product',
            is_active=False,
            category='A'  # Same category
        )
        
        with self.assertRaises(ValidationError):
            constraint.validate(instance)
    
    def test_validate_update_same_instance(self):
        """Test validation passes when updating the same instance."""
        constraint = UniversalConstraint(
            fields=['name'],
            condition=models.Q(is_active=True),
            name='unique_active_name'
        )
        
        # Create an existing instance
        existing = Product.objects.create(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Update the same instance
        existing.category = 'B'
        
        # Should not raise any exception
        try:
            constraint.validate(existing)
        except ValidationError:
            self.fail("Validation should have passed when updating same instance")


class SignalHandlerTests(TestCase):
    """Test the signal handler for automatic validation."""
    
    def setUp(self):
        # Store original constraints
        self.original_constraints = getattr(Product, '_universal_constraints', None)
        # Add test constraints to the Product model
        Product._universal_constraints = [
            UniversalConstraint(
                fields=['name'],
                condition=models.Q(is_active=True),
                name='unique_active_name'
            )
        ]
    
    def tearDown(self):
        # Restore original constraints
        if self.original_constraints is not None:
            Product._universal_constraints = self.original_constraints
        elif hasattr(Product, '_universal_constraints'):
            delattr(Product, '_universal_constraints')
    
    def test_signal_handler_with_constraints(self):
        """Test the signal handler with constraints."""
        # Create an existing instance
        existing = Product.objects.create(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Try to create another instance with same name and is_active=True
        instance = Product(
            name='Test Product',
            is_active=True,
            category='B'
        )
        
        # This should trigger the signal and raise ValidationError
        with self.assertRaises(ValidationError):
            instance.save()
    
    def test_signal_handler_without_constraints(self):
        """Test the signal handler without constraints."""
        # Remove constraints
        delattr(Product, '_universal_constraints')
        
        instance = Product(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Should not raise any exception
        try:
            instance.save()
        except ValidationError:
            self.fail("Validation should have passed when no constraints exist")
    
    def test_signal_handler_passes(self):
        """Test the signal handler passes when no conflicts."""
        instance = Product(
            name='Unique Product',
            is_active=True,
            category='A'
        )
        
        # Should not raise any exception
        try:
            instance.save()
        except ValidationError:
            self.fail("Validation should have passed")


class IntegrationTests(TestCase):
    """Integration tests for the validator system."""
    
    def setUp(self):
        # Store original constraints
        self.original_constraints = getattr(Product, '_universal_constraints', None)
    
    def tearDown(self):
        # Restore original constraints
        if self.original_constraints is not None:
            Product._universal_constraints = self.original_constraints
        elif hasattr(Product, '_universal_constraints'):
            delattr(Product, '_universal_constraints')
    
    def test_full_validation_workflow(self):
        """Test the complete validation workflow."""
        # Set up constraints
        constraints = [
            UniversalConstraint(
                fields=['name'],
                condition=models.Q(is_active=True),
                name='unique_active_name'
            ),
            UniversalConstraint(
                fields=['name', 'category'],
                condition=None,
                name='unique_name_category'
            )
        ]
        
        Product._universal_constraints = constraints
        
        # Create first instance
        instance1 = Product.objects.create(
            name='Test Product',
            is_active=True,
            category='A'
        )
        
        # Test 1: Try to create conflicting instance (should fail)
        instance2 = Product(
            name='Test Product',
            is_active=True,
            category='B'
        )
        
        with self.assertRaises(ValidationError):
            instance2.save()
        
        # Test 2: Create non-conflicting instance (should pass)
        instance3 = Product(
            name='Different Product',
            is_active=True,
            category='B'
        )
        
        instance3.save()
        
        # Test 3: Create instance with same name but inactive (should pass for first constraint)
        instance4 = Product(
            name='Test Product',
            is_active=False,  # Condition not met for first constraint
            category='C'
        )
        
        instance4.save()
        
        # Test 4: Try to create instance with same name+category (should fail)
        instance5 = Product(
            name='Test Product',
            is_active=False,
            category='A'  # Same as instance1
        )
        
        with self.assertRaises(ValidationError):
            instance5.save()
    
    def test_complex_conditions(self):
        """Test validation with complex conditions."""
        # Set up constraint with complex condition
        constraints = [
            UniversalConstraint(
                fields=['name'],
                condition=models.Q(is_active=True) & models.Q(category='premium'),
                name='unique_premium_active_name'
            )
        ]
        
        Product._universal_constraints = constraints
        
        # Create first instance
        instance1 = Product.objects.create(
            name='Premium Product',
            is_active=True,
            category='premium'
        )
        
        # Test 1: Same name, active but not premium (should pass)
        instance2 = Product(
            name='Premium Product',
            is_active=True,
            category='basic'  # Not premium
        )
        
        instance2.save()
        
        # Test 2: Same name, premium but not active (should pass)
        instance3 = Product(
            name='Premium Product',
            is_active=False,  # Not active
            category='premium'
        )
        
        instance3.save()
        
        # Test 3: Same name, active and premium (should fail)
        instance4 = Product(
            name='Premium Product',
            is_active=True,
            category='premium'
        )
        
        with self.assertRaises(ValidationError):
            instance4.save()
