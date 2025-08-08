"""
Application-level universal constraint validation for Django ORM.

This module provides a generic solution for validating universal constraints
at the application level, suitable for backends that don't support them natively.
"""

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
import logging

logger = logging.getLogger('universal_constraints.validators')


class UniversalConstraint:
    """
    Represents a constraint that can be validated at the application level.
    
    Args:
        fields: List of field names that should be unique together
        condition: Q object representing the condition when the constraint applies
        name: Optional name for the constraint (for error messages)
    """
    
    def __init__(self, fields, condition=None, name=None):
        self.fields = fields
        self.condition = condition
        if name:
            self.name = name
        elif condition:
            self.name = f"unique_{'_'.join(fields)}_conditional"
        else:
            self.name = f"unique_{'_'.join(fields)}"
    
    def __str__(self):
        condition_str = f" WHERE {self.condition}" if self.condition else ""
        return f"{self.name}: UNIQUE({', '.join(self.fields)}){condition_str}"
    
    def __repr__(self):
        return f"<UniversalConstraint: {self.name} on {self.fields}>"
    
    def validate(self, instance, use_race_protection=True):
        """
        Validate the constraint against the given model instance.
        
        Args:
            instance: Model instance to validate
            use_race_protection: Whether to use select_for_update() for race condition protection.
        
        Raises ValidationError if the constraint is violated.
        """
        # Only validate if the condition applies to this instance
        if not self._condition_applies(instance):
            return
        
        # Determine if we should use race condition protection
        if use_race_protection:
            self._validate_with_race_protection(instance)
        else:
            self._validate_without_race_protection(instance)
    
    def _validate_with_race_protection(self, instance):
        """Validate with race condition protection using select_for_update()."""
        logger.debug(f"Validating constraint {self.name} with race protection")
        
        try:
            with transaction.atomic():
                # Build the query to check for existing instances
                queryset = instance.__class__.objects.select_for_update()
                
                if self.condition:
                    queryset = queryset.filter(self.condition)
                
                # Filter by the unique fields
                field_filters = {}
                for field in self.fields:
                    field_filters[field] = getattr(instance, field)
                
                queryset = queryset.filter(**field_filters)
                
                # Exclude the current instance if it's being updated
                if instance.pk is not None:
                    queryset = queryset.exclude(pk=instance.pk)
                
                # Check if any matching instances exist
                if queryset.exists():
                    field_names = ', '.join(self.fields)
                    condition_str = f" when {self.condition}" if self.condition else ""
                    raise ValidationError(
                        f"Universal constraint violated: {field_names} must be unique{condition_str}",
                        code='universal_constraint_violation'
                    )
        
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.warning(f"Race protection failed for constraint {self.name}: {e}")
            # Fallback to non-protected validation
            self._validate_without_race_protection(instance)
    
    def _validate_without_race_protection(self, instance):
        """Validate without race condition protection (faster but less safe)."""
        logger.debug(f"Validating constraint {self.name} without race protection")
        
        # Build the query to check for existing instances
        queryset = instance.__class__.objects.all()
        
        if self.condition:
            queryset = queryset.filter(self.condition)
        
        # Filter by the unique fields
        field_filters = {}
        for field in self.fields:
            field_filters[field] = getattr(instance, field)
        
        queryset = queryset.filter(**field_filters)
        
        # Exclude the current instance if it's being updated
        if instance.pk is not None:
            queryset = queryset.exclude(pk=instance.pk)
        
        # Check if any matching instances exist
        if queryset.exists():
            field_names = ', '.join(self.fields)
            condition_str = f" when {self.condition}" if self.condition else ""
            raise ValidationError(
                f"Universal constraint violated: {field_names} must be unique{condition_str}",
                code='universal_constraint_violation'
            )
    
    def _condition_applies(self, instance):
        """Check if the condition applies to the given instance."""
        # If there's no condition, the constraint always applies
        if self.condition is None:
            return True
        
        # Otherwise, evaluate the condition for this instance
        return self._evaluate_condition_for_instance(instance)
    
    def _evaluate_condition_for_instance(self, instance):
        """Evaluate the condition for a model instance that might not be saved yet."""
        # If no condition, always applies
        if self.condition is None:
            return True
            
        # Evaluate the Q object against the instance
        try:
            return self._evaluate_q_object(self.condition, instance)
        except Exception:
            # Fallback: assume condition applies if we can't evaluate it
            return True
    
    def _evaluate_q_object(self, q_obj, instance):
        """Recursively evaluate a Q object against a model instance."""
        try:
            if hasattr(q_obj, 'children'):
                # Handle Q objects with children (AND/OR operations)
                results = []
                for child in q_obj.children:
                    if isinstance(child, models.Q):
                        results.append(self._evaluate_q_object(child, instance))
                    else:
                        # Handle individual lookups
                        results.append(self._evaluate_lookup(child, instance))
                
                # Apply the connector (AND/OR)
                if q_obj.connector == models.Q.AND:
                    return all(results)
                else:  # OR
                    return any(results)
            else:
                # Single condition
                return self._evaluate_lookup(q_obj, instance)
        except (AttributeError, TypeError, ValueError) as e:
            logger.warning(
                f"Failed to evaluate Q object condition for constraint {self.name}: {e}. "
                f"Assuming condition applies to be safe."
            )
            # Fallback: assume condition applies if we can't evaluate it
            return True
        except Exception as e:
            logger.error(
                f"Unexpected error evaluating Q object condition for constraint {self.name}: {e}. "
                f"Assuming condition applies to be safe."
            )
            # Fallback: assume condition applies if we can't evaluate it
            return True
    
    def _evaluate_lookup(self, lookup, instance):
        """Evaluate a single field lookup against a model instance."""
        field_name, value = lookup
        
        # Handle simple field lookups
        if '__' not in field_name:
            return getattr(instance, field_name) == value
        
        # Handle field lookups with operators
        field_parts = field_name.split('__')
        field_value = getattr(instance, field_parts[0])
        
        if len(field_parts) == 2:
            operator = field_parts[1]
            if operator == 'exact':
                return field_value == value
            elif operator == 'isnull':
                return (field_value is None) == value
            elif operator == 'in':
                return field_value in value
            elif operator == 'gt':
                return field_value > value
            elif operator == 'gte':
                return field_value >= value
            elif operator == 'lt':
                return field_value < value
            elif operator == 'lte':
                return field_value <= value
        
        # Default to True for unsupported lookups
        return True


class UniversalConstraintValidatorMixin:
    """
    Mixin for Django models that adds support for universal constraint validation.
    
    Usage:
        class MyModel(UniversalConstraintValidatorMixin, models.Model):
            name = models.CharField(max_length=100)
            is_active = models.BooleanField(default=True)
            
            class Meta:
                conditional_universal_constraints = [
                    UniversalConstraint(
                        fields=['name'],
                        condition=models.Q(is_active=True),
                        name='unique_active_name'
                    )
                ]
    """
    
    def clean(self):
        """Override clean to validate universal constraints."""
        super().clean()
        self._validate_universal_constraints()
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation runs before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def _validate_universal_constraints(self):
        """Validate all universal constraints defined on the model."""
        constraints = getattr(self.__class__, '_universal_constraints', [])
        
        for constraint in constraints:
            constraint.validate(self)


@receiver(pre_save)
def validate_universal_constraints(sender, instance, **kwargs):
    """
    Signal handler that automatically validates universal constraints
    for any model that defines them, respecting database routing.
    
    This provides a completely automatic solution - just define constraints as a class attribute.
    """
    # Determine which database this instance will be saved to
    from django.db import router
    using = kwargs.get('using') or router.db_for_write(sender, instance=instance)
    
    # Get database-specific settings
    from .settings import constraint_settings
    
    # Only validate if universal constraints are enabled for this database
    if not constraint_settings.is_database_enabled(using):
        return
    
    # Check if the model has universal constraints defined
    constraints = getattr(sender, '_universal_constraints', None)
    
    if constraints:
        # Get database-specific race condition protection setting
        use_race_protection = constraint_settings.get_setting(
            using, 'RACE_CONDITION_PROTECTION', True
        )
        
        for constraint in constraints:
            constraint.validate(instance, use_race_protection=use_race_protection)


def add_universal_constraint(model_class, fields, condition=None, name=None):
    """
    Utility function to dynamically add a universal constraint to a model.
    
    This can be useful for adding constraints to existing models without modifying their code.
    
    Args:
        model_class: The Django model class
        fields: List of field names that should be unique together
        condition: Q object representing the condition (optional)
        name: Optional name for the constraint
    """
    constraint = UniversalConstraint(fields, condition, name)
    
    # Add to the model class if it doesn't exist
    if not hasattr(model_class, '_universal_constraints'):
        model_class._universal_constraints = []
    
    model_class._universal_constraints.append(constraint)
