"""
Test runner for django-universal-constraints.

This script sets up a minimal Django environment and runs all tests.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    
    # Create database tables for test models
    from django.core.management import execute_from_command_line
    from django.db import connection
    
    # Create tables for test models
    with connection.schema_editor() as schema_editor:
        from tests.test_validators import ValidatorTestModel, ValidatorTestModelWithConstraints
        from tests.test_constraint_converter import TestModelWithConstraints, TestModelWithoutConstraints, TestModelWithUniqueTogetherOnly
        from tests.test_auto_discovery import (
            AutoDiscoveryTestModel, AutoDiscoveryTestModelWithUniqueTogetherOnly
        )
        from tests.test_management_commands import (
            ManagementCommandTestModel, ManagementCommandTestModelWithUniqueTogetherOnly
        )
        from tests.test_apps import AppsTestModel
        
        # Create tables for all test models
        test_models = [
            ValidatorTestModel,
            ValidatorTestModelWithConstraints,
            TestModelWithConstraints,
            TestModelWithoutConstraints,
            TestModelWithUniqueTogetherOnly,
            AutoDiscoveryTestModel,
            AutoDiscoveryTestModelWithUniqueTogetherOnly,
            ManagementCommandTestModel,
            ManagementCommandTestModelWithUniqueTogetherOnly,
            AppsTestModel,
        ]
        
        for model in test_models:
            try:
                schema_editor.create_model(model)
            except Exception as e:
                # Table might already exist, continue
                pass
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))
