"""
Tests for universal_constraints.constraint_converter module.
"""

from django.test import TestCase
from django.db import models
from django.db.models import Q, UniqueConstraint

from universal_constraints.constraint_converter import (
    ConstraintConverter,
    has_convertible_constraints
)
from universal_constraints.validators import UniversalConstraint


class TestModelWithConstraints(models.Model):
    """Test model with various constraint types."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50)
    
    class Meta:
        app_label = 'tests'
        constraints = [
            UniqueConstraint(
                fields=['email'],
                condition=Q(is_active=True),
                name='converter_unique_active_email'
            ),
            UniqueConstraint(
                fields=['name', 'category'],
                name='unique_name_category'
            ),
        ]
        unique_together = [('name', 'is_active')]


class TestModelWithoutConstraints(models.Model):
    """Test model without constraints."""
    name = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'tests'


class TestModelWithUniqueTogetherOnly(models.Model):
    """Test model with only unique_together."""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    
    class Meta:
        app_label = 'tests'
        unique_together = [('name', 'category')]


class ConstraintConverterTest(TestCase):
    """Test the ConstraintConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = ConstraintConverter()
    
    def test_converter_initialization(self):
        """Test converter initialization."""
        self.assertEqual(self.converter.converted_count, 0)
        self.assertEqual(self.converter.skipped_count, 0)
        self.assertEqual(len(self.converter.warnings), 0)
    
    def test_convert_model_constraints_with_conditional(self):
        """Test converting model with conditional constraints."""
        # Create a fresh model class to avoid test pollution
        class FreshTestModelWithConstraints(models.Model):
            name = models.CharField(max_length=100)
            email = models.EmailField()
            is_active = models.BooleanField(default=True)
            category = models.CharField(max_length=50)
            
            class Meta:
                app_label = 'tests'
                constraints = [
                    UniqueConstraint(
                        fields=['email'],
                        condition=Q(is_active=True),
                        name='unique_active_email'
                    ),
                    UniqueConstraint(
                        fields=['name', 'category'],
                        name='unique_name_category'
                    ),
                ]
                unique_together = [('name', 'is_active')]
        
        constraints = self.converter.convert_model_constraints(FreshTestModelWithConstraints)
        
        # Should convert conditional constraint
        conditional_constraints = [c for c in constraints if c.condition is not None]
        self.assertEqual(len(conditional_constraints), 1)
        
        constraint = conditional_constraints[0]
        self.assertEqual(constraint.fields, ['email'])
        self.assertEqual(constraint.name, 'unique_active_email')
        self.assertIsNotNone(constraint.condition)
        
        # Check that constraint was added to model
        self.assertTrue(hasattr(FreshTestModelWithConstraints, '_universal_constraints'))
        model_constraints = FreshTestModelWithConstraints._universal_constraints
        self.assertEqual(len(model_constraints), 3)  # All 3 constraints should be converted
    
    def test_convert_model_constraints_with_unique_together(self):
        """Test converting model with unique_together (always converts)."""
        constraints = self.converter.convert_model_constraints(TestModelWithConstraints)
        
        # Should always convert unique_together to app-level validation
        unique_together_constraints = [
            c for c in constraints 
            if c.fields == ['name', 'is_active'] and c.condition is None
        ]
        self.assertEqual(len(unique_together_constraints), 1)
        
        constraint = unique_together_constraints[0]
        self.assertEqual(constraint.fields, ['name', 'is_active'])
        self.assertEqual(constraint.name, 'unique_together_name_is_active')
        self.assertIsNone(constraint.condition)
    
    def test_convert_model_without_constraints(self):
        """Test converting model without constraints."""
        constraints = self.converter.convert_model_constraints(TestModelWithoutConstraints)
        
        self.assertEqual(len(constraints), 0)
        self.assertEqual(self.converter.converted_count, 0)
    
    def test_convert_unique_together_only(self):
        """Test converting model with only unique_together."""
        constraints = self.converter.convert_model_constraints(TestModelWithUniqueTogetherOnly)
        
        self.assertEqual(len(constraints), 1)
        constraint = constraints[0]
        self.assertEqual(constraint.fields, ['name', 'category'])
        self.assertEqual(constraint.name, 'unique_together_name_category')
        self.assertIsNone(constraint.condition)
    
    def test_convert_all_constraints(self):
        """Test that ALL UniqueConstraints are converted to app-level validation."""
        constraints = self.converter.convert_model_constraints(TestModelWithConstraints)
        
        # Should convert ALL constraints: conditional + non-conditional + unique_together
        self.assertEqual(len(constraints), 3)
        
        # Find the non-conditional UniqueConstraint
        non_conditional_unique = [
            c for c in constraints 
            if c.fields == ['name', 'category'] and c.condition is None
        ]
        self.assertEqual(len(non_conditional_unique), 1)
        
        # Find the conditional UniqueConstraint
        conditional_unique = [
            c for c in constraints 
            if c.fields == ['email'] and c.condition is not None
        ]
        self.assertEqual(len(conditional_unique), 1)
        
        # Find the unique_together constraint
        unique_together = [
            c for c in constraints 
            if c.fields == ['name', 'is_active'] and c.condition is None
        ]
        self.assertEqual(len(unique_together), 1)
    
    
    def test_get_stats(self):
        """Test getting conversion statistics."""
        # Convert a model to generate some stats
        self.converter.convert_model_constraints(TestModelWithConstraints)
        
        stats = self.converter.get_stats()
        
        self.assertIn('converted', stats)
        self.assertIn('skipped', stats)
        self.assertIn('warnings', stats)
        self.assertIsInstance(stats['converted'], int)
        self.assertIsInstance(stats['skipped'], int)
        self.assertIsInstance(stats['warnings'], int)
    
    def test_get_warnings(self):
        """Test getting conversion warnings."""
        warnings = self.converter.get_warnings()
        self.assertIsInstance(warnings, list)
    
    def test_reset_stats(self):
        """Test resetting conversion statistics."""
        # Create a fresh model to avoid test pollution
        class FreshStatsTestModel(models.Model):
            name = models.CharField(max_length=100)
            email = models.EmailField()
            is_active = models.BooleanField(default=True)
            
            class Meta:
                app_label = 'tests'
                constraints = [
                    UniqueConstraint(
                        fields=['email'],
                        condition=Q(is_active=True),
                        name='unique_active_email'
                    ),
                ]
                unique_together = [('name', 'is_active')]
        
        # Generate some stats
        self.converter.convert_model_constraints(FreshStatsTestModel)
        
        # Verify stats exist
        self.assertGreater(self.converter.converted_count, 0)
        
        # Reset
        self.converter.reset_stats()
        
        # Verify stats are reset
        self.assertEqual(self.converter.converted_count, 0)
        self.assertEqual(self.converter.skipped_count, 0)
        self.assertEqual(len(self.converter.warnings), 0)
    
    def test_convert_unique_constraint_to_universal(self):
        """Test converting UniqueConstraint to UniversalConstraint."""
        unique_constraint = UniqueConstraint(
            fields=['email'],
            condition=Q(is_active=True),
            name='unique_active_email'
        )
        
        constraint = self.converter._convert_constraint(unique_constraint, TestModelWithoutConstraints)
        
        self.assertIsInstance(constraint, UniversalConstraint)
        self.assertEqual(constraint.fields, ['email'])
        self.assertEqual(constraint.name, 'unique_active_email')
        self.assertIsNotNone(constraint.condition)
    
    def test_convert_unique_together_to_universal(self):
        """Test converting unique_together to UniversalConstraint."""
        fields = ['name', 'category']
        
        constraint = self.converter._convert_unique_together(fields, TestModelWithoutConstraints)
        
        self.assertIsInstance(constraint, UniversalConstraint)
        self.assertEqual(constraint.fields, ['name', 'category'])
        self.assertEqual(constraint.name, 'unique_together_name_category')
        self.assertIsNone(constraint.condition)
    
    def test_constraint_conversion_logic(self):
        """Test constraint conversion decision logic."""
        # Conditional constraint should always be converted
        constraint = UniqueConstraint(
            fields=['email'],
            condition=Q(is_active=True),
            name='conditional'
        )
        converted = self.converter._convert_constraint(constraint, TestModelWithoutConstraints)
        self.assertIsNotNone(converted)
        
        # Non-conditional constraint should ALSO be converted (core library functionality)
        regular_constraint = UniqueConstraint(
            fields=['name'],
            name='regular'
        )
        converted = self.converter._convert_constraint(regular_constraint, TestModelWithoutConstraints)
        self.assertIsNotNone(converted)  # Should be converted regardless of remove_db_constraints
        
        # All converters should convert all UniqueConstraints
        another_converter = ConstraintConverter()
        converted = another_converter._convert_constraint(regular_constraint, TestModelWithoutConstraints)
        self.assertIsNotNone(converted)
        
        # Non-unique constraint should not be converted
        check_constraint = models.CheckConstraint(
            check=Q(age__gte=0),
            name='check_age'
        )
        converted = self.converter._convert_constraint(check_constraint, TestModelWithoutConstraints)
        self.assertIsNone(converted)


class UtilityFunctionTest(TestCase):
    """Test utility functions."""
    
    def test_has_convertible_constraints_with_constraints(self):
        """Test has_convertible_constraints with model that has constraints."""
        # Create a fresh model class to avoid test pollution
        class FreshTestModel(models.Model):
            name = models.CharField(max_length=100)
            email = models.EmailField()
            is_active = models.BooleanField(default=True)
            category = models.CharField(max_length=50)
            
            class Meta:
                app_label = 'tests'
                constraints = [
                    UniqueConstraint(
                        fields=['email'],
                        condition=Q(is_active=True),
                        name='unique_active_email'
                    ),
                    UniqueConstraint(
                        fields=['name', 'category'],
                        name='unique_name_category'
                    ),
                ]
                unique_together = [('name', 'is_active')]
        
        self.assertTrue(has_convertible_constraints(FreshTestModel))
    
    def test_has_convertible_constraints_with_unique_together(self):
        """Test has_convertible_constraints with model that has unique_together."""
        # Create a fresh model class to avoid test pollution
        class FreshUniqueTogetherModel(models.Model):
            name = models.CharField(max_length=100)
            category = models.CharField(max_length=50)
            
            class Meta:
                app_label = 'tests'
                unique_together = [('name', 'category')]
        
        self.assertTrue(has_convertible_constraints(FreshUniqueTogetherModel))
    
    def test_has_convertible_constraints_without_constraints(self):
        """Test has_convertible_constraints with model that has no constraints."""
        self.assertFalse(has_convertible_constraints(TestModelWithoutConstraints))
