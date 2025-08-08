"""
Constraint conversion utilities.

This module handles conversion of Django's native unique constraints
to application-level universal constraints.
"""

import logging
from django.db import models
from django.db.models import UniqueConstraint
from .validators import UniversalConstraint

logger = logging.getLogger('universal_constraints.converter')


class ConstraintConverter:
    """Converts Django constraints to application-level constraints."""
    
    def __init__(self):
        self.converted_count = 0
        self.skipped_count = 0
        self.warnings = []
    
    def convert_model_constraints(self, model):
        """Convert all unique constraints for a given model."""
        logger.debug(f"Processing model: {model._meta.label}")
        
        converted_constraints = []
        
        # Convert Meta.constraints (UniqueConstraint objects)
        # Note: We keep the original constraints in the model Meta - the database backend
        # will handle them according to its capabilities (skip, add, etc.)
        if hasattr(model._meta, 'constraints'):
            for constraint in model._meta.constraints:
                converted = self._convert_constraint(constraint, model)
                if converted:
                    converted_constraints.append(converted)
        
        # Convert Meta.unique_together
        # Note: We keep the original unique_together - the database backend
        # will handle it according to its capabilities
        if hasattr(model._meta, 'unique_together') and model._meta.unique_together:
            for fields in model._meta.unique_together:
                converted = self._convert_unique_together(fields, model)
                if converted:
                    converted_constraints.append(converted)
        
        # Add converted constraints to model
        if converted_constraints:
            if not hasattr(model, '_universal_constraints'):
                model._universal_constraints = []
            model._universal_constraints.extend(converted_constraints)
            
            logger.info(
                f"Converted {len(converted_constraints)} constraint(s) for {model._meta.label}"
            )
        
        return converted_constraints
    
    def _convert_constraint(self, constraint, model):
        """Convert a UniqueConstraint to UniversalConstraint."""
        if not isinstance(constraint, UniqueConstraint):
            logger.debug(f"Skipping non-UniqueConstraint: {type(constraint).__name__}")
            self.skipped_count += 1
            return None
        
        try:
            condition = getattr(constraint, 'condition', None)
            fields = list(constraint.fields)
            name = getattr(constraint, 'name', None) or f"converted_{constraint.__class__.__name__}"
            
            converted = UniversalConstraint(
                fields=fields,
                condition=condition,
                name=name
            )
            
            constraint_type = "conditional" if condition else "non-conditional"
            logger.debug(
                f"Converted {constraint_type} UniqueConstraint '{name}' "
                f"on fields {fields} for {model._meta.label}"
            )
            
            self.converted_count += 1
            return converted
            
        except Exception as e:
            warning = f"Failed to convert constraint {constraint} on {model._meta.label}: {e}"
            logger.warning(warning)
            self.warnings.append(warning)
            self.skipped_count += 1
            return None
    
    def _convert_unique_together(self, fields, model):
        """Convert unique_together tuple to UniversalConstraint."""
        try:
            # Convert tuple/list to list
            field_list = list(fields)
            name = f"unique_together_{'_'.join(field_list)}"
            
            # ALWAYS convert unique_together to app-level validation
            # This is part of the core functionality
            converted = UniversalConstraint(
                fields=field_list,
                condition=None,  # unique_together is always non-conditional
                name=name
            )
            
            logger.debug(
                f"Converted unique_together {field_list} for {model._meta.label}"
            )
            
            self.converted_count += 1
            return converted
            
        except Exception as e:
            warning = f"Failed to convert unique_together {fields} on {model._meta.label}: {e}"
            logger.warning(warning)
            self.warnings.append(warning)
            self.skipped_count += 1
            return None
    
    def get_stats(self):
        """Get conversion statistics."""
        return {
            'converted': self.converted_count,
            'skipped': self.skipped_count,
            'warnings': len(self.warnings)
        }
    
    def get_warnings(self):
        """Get list of conversion warnings."""
        return self.warnings.copy()
    
    def reset_stats(self):
        """Reset conversion statistics."""
        self.converted_count = 0
        self.skipped_count = 0
        self.warnings = []

def has_convertible_constraints(model):
    """
    Check if a model has any constraints that can be converted.
    
    Args:
        model: Django model class
    
    Returns:
        bool: True if model has convertible constraints
    """
    # Check Meta.constraints for UniqueConstraint objects
    if hasattr(model._meta, 'constraints'):
        for constraint in model._meta.constraints:
            if isinstance(constraint, UniqueConstraint):
                return True
    
    # Check Meta.unique_together
    if hasattr(model._meta, 'unique_together') and model._meta.unique_together:
        return True
    
    return False


def get_constraint_info(model):
    """
    Get information about a model's unique constraints from both original and converted sources.
    
    This function checks both:
    1. Original constraints in model._meta.constraints and model._meta.unique_together
    2. Already converted constraints in model._universal_constraints
    
    Args:
        model: Django model class
    
    Returns:
        dict: Information about the model's constraints
    """
    info = {
        'model': model._meta.label,
        'constraints': [],
        'unique_together': [],
    }
    
    # Track constraint names and unique_together to avoid duplicates
    constraint_names = set()
    unique_together_sets = set()
    
    # First, handle converted constraints from auto-discovery
    if hasattr(model, '_universal_constraints'):
        for constraint in model._universal_constraints:
            constraint_name = getattr(constraint, 'name', 'unnamed')
            condition = getattr(constraint, 'condition', None)
            
            # Check if this is a converted unique_together
            if (not condition and constraint_name.startswith('unique_together_')):
                # Show converted unique_together as unique_together (not as UniqueConstraint)
                fields_tuple = tuple(sorted(constraint.fields))
                if fields_tuple not in unique_together_sets:
                    info['unique_together'].append(list(constraint.fields))
                    unique_together_sets.add(fields_tuple)
            else:
                # Regular UniqueConstraint (conditional or non-unique_together)
                if constraint_name not in constraint_names:
                    constraint_info = {
                        'name': constraint_name,
                        'fields': list(constraint.fields),
                        'condition': condition
                    }
                    info['constraints'].append(constraint_info)
                    constraint_names.add(constraint_name)
    
    # Then, handle original constraints (not yet converted)
    if hasattr(model._meta, 'constraints'):
        for constraint in model._meta.constraints:
            if isinstance(constraint, UniqueConstraint):
                constraint_name = getattr(constraint, 'name', 'unnamed')
                if constraint_name not in constraint_names:
                    constraint_info = {
                        'name': constraint_name,
                        'fields': list(constraint.fields),
                        'condition': getattr(constraint, 'condition', None)
                    }
                    info['constraints'].append(constraint_info)
                    constraint_names.add(constraint_name)
    
    # Finally, handle original unique_together (only if not already converted)
    if hasattr(model._meta, 'unique_together') and model._meta.unique_together:
        for fields in model._meta.unique_together:
            fields_tuple = tuple(sorted(fields))
            if fields_tuple not in unique_together_sets:
                info['unique_together'].append(list(fields))
                unique_together_sets.add(fields_tuple)
    
    return info
