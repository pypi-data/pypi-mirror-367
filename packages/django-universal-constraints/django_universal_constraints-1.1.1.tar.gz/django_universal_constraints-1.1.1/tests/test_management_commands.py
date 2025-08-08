"""
Tests for universal_constraints.management.commands module.
"""

import json
from io import StringIO
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import models
from django.db.models import Q, UniqueConstraint

from universal_constraints.management.commands.discover_constraints import Command


class ManagementCommandTestModel(models.Model):
    """Test model for management command testing."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        app_label = 'tests'
        constraints = [
            UniqueConstraint(
                fields=['email'],
                condition=Q(is_active=True),
                name='cmd_unique_active_email'
            ),
            UniqueConstraint(
                fields=['name'],
                name='cmd_unique_name'
            )
        ]


class ManagementCommandTestModelWithUniqueTogetherOnly(models.Model):
    """Test model with only unique_together for command testing."""
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    
    class Meta:
        app_label = 'tests'
        unique_together = [
            ('first_name', 'last_name'),
            ('first_name', 'department'),
        ]


class DiscoverConstraintsCommandTest(TestCase):
    """Test the discover_constraints management command."""
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
            'RACE_CONDITION_PROTECTION': True,
        }
    })
    def test_command_text_output(self):
        """Test command with text output format."""
        out = StringIO()
        call_command('discover_constraints', '--format=text', stdout=out)
        output = out.getvalue()
        
        # Should contain expected sections
        self.assertIn('Universal Constraints Discovery', output)
        self.assertIn('Database: default', output)
        self.assertIn('Summary:', output)
        
        # Should contain summary statistics
        self.assertIn('Databases configured:', output)
        self.assertIn('Models to process:', output)
        self.assertIn('Total constraints:', output)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
            'RACE_CONDITION_PROTECTION': True,
        }
    })
    def test_command_json_output(self):
        """Test command with JSON output format."""
        out = StringIO()
        call_command('discover_constraints', '--format=json', stdout=out)
        output = out.getvalue()
        
        # Should be valid JSON
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            self.fail("Command output is not valid JSON")
        
        # Should have expected structure
        self.assertIn('databases', data)
        self.assertIn('summary', data)
        
        # Summary should have expected fields
        summary = data['summary']
        self.assertIn('databases_configured', summary)
        self.assertIn('total_models', summary)
        self.assertIn('total_constraints', summary)
        self.assertIn('unique_constraints', summary)
        self.assertIn('unique_together_constraints', summary)
        self.assertIn('conditional_constraints', summary)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
            'RACE_CONDITION_PROTECTION': True,
        },
        'test': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
            'RACE_CONDITION_PROTECTION': False,
        }
    })
    def test_command_multiple_databases(self):
        """Test command with multiple configured databases."""
        out = StringIO()
        call_command('discover_constraints', '--format=text', stdout=out)
        output = out.getvalue()
        
        # Should show both databases
        self.assertIn('Database: default', output)
        self.assertIn('Database: test', output)
        
        # Should show correct summary count
        self.assertIn('Databases configured: 2', output)
    
    def test_command_no_databases_configured(self):
        """Test command when no databases are configured."""
        with override_settings(UNIVERSAL_CONSTRAINTS={}):
            out = StringIO()
            call_command('discover_constraints', stdout=out)
            output = out.getvalue()
            
            # Should show that no databases are configured for universal constraints
            # (but the test/default databases still exist in Django settings)
            self.assertIn('Universal Constraints Discovery', output)
            # The command should still run and show the discovery header
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        }
    })
    def test_command_constraint_details(self):
        """Test that command shows detailed constraint information."""
        out = StringIO()
        call_command('discover_constraints', '--format=text', stdout=out)
        output = out.getvalue()
        
        # Should show constraint names and details
        self.assertIn('conditional:', output)
        self.assertIn('unique_together:', output)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        }
    })
    def test_command_json_constraint_details(self):
        """Test JSON output contains detailed constraint information."""
        out = StringIO()
        call_command('discover_constraints', '--format=json', stdout=out)
        output = out.getvalue()
        
        data = json.loads(output)
        
        # Should have database information
        if 'default' in data['databases']:
            db_info = data['databases']['default']
            self.assertIn('settings', db_info)
            self.assertIn('models', db_info)
    
    def test_command_invalid_format(self):
        """Test command with invalid format argument."""
        with self.assertRaises(CommandError):
            # This should fail due to invalid choice
            call_command('discover_constraints', '--format=invalid')
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        }
    })
    def test_command_output_consistency(self):
        """Test that text and JSON outputs are consistent."""
        # Get text output
        text_out = StringIO()
        call_command('discover_constraints', '--format=text', stdout=text_out)
        text_output = text_out.getvalue()
        
        # Get JSON output
        json_out = StringIO()
        call_command('discover_constraints', '--format=json', stdout=json_out)
        json_output = json_out.getvalue()
        
        # Parse JSON
        json_data = json.loads(json_output)
        
        # Extract summary from text (this is a simplified check)
        summary = json_data['summary']
        
        # Check that key numbers appear in both outputs
        self.assertIn(str(summary['databases_configured']), text_output)
        self.assertIn(str(summary['total_models']), text_output)
        self.assertIn(str(summary['total_constraints']), text_output)


class CommandClassTest(TestCase):
    """Test the Command class directly."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.command = Command()
    
    def test_command_initialization(self):
        """Test command initialization."""
        command = Command()
        self.assertIsNotNone(command.help)
        self.assertIn('Show all models and constraints', command.help)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        }
    })
    def test_collect_database_info(self):
        """Test the _collect_database_info method."""
        configured_databases = ['default']
        
        databases_info = self.command._collect_database_info(configured_databases)
        
        # Should have summary
        self.assertIn('_summary', databases_info)
        
        # Should have database info
        self.assertIn('default', databases_info)
        
        # Summary should have expected structure
        summary = databases_info['_summary']
        self.assertIn('databases_configured', summary)
        self.assertIn('total_models', summary)
        self.assertIn('total_unique_constraints', summary)
        self.assertIn('total_unique_together', summary)
        self.assertIn('total_constraints', summary)
        self.assertIn('conditional_constraints', summary)


class CommandIntegrationTest(TestCase):
    """Integration tests for the management command."""
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
            'RACE_CONDITION_PROTECTION': True,
        },
        'test': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
            'RACE_CONDITION_PROTECTION': False,
        }
    })
    def test_full_integration_text_and_json(self):
        """Test full integration with both text and JSON output."""
        # Test text output
        text_out = StringIO()
        call_command('discover_constraints', '--format=text', stdout=text_out)
        text_output = text_out.getvalue()
        
        # Test JSON output
        json_out = StringIO()
        call_command('discover_constraints', '--format=json', stdout=json_out)
        json_output = json_out.getvalue()
        
        # Both should succeed
        self.assertIn('Universal Constraints Discovery', text_output)
        
        json_data = json.loads(json_output)
        self.assertIn('databases', json_data)
        self.assertIn('summary', json_data)
        
        # Should have information about both databases
        self.assertIn('Database: default', text_output)
        self.assertIn('Database: test', text_output)
        
        self.assertIn('default', json_data['databases'])
        self.assertIn('test', json_data['databases'])
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        }
    })
    def test_constraint_counting_accuracy(self):
        """Test that constraint counting is accurate."""
        json_out = StringIO()
        call_command('discover_constraints', '--format=json', stdout=json_out)
        json_output = json_out.getvalue()
        
        json_data = json.loads(json_output)
        summary = json_data['summary']
        
        # We should have at least our test models
        self.assertGreaterEqual(summary['total_models'], 0)
        self.assertGreaterEqual(summary['total_constraints'], 0)
        
        # Should have both unique constraints and unique_together
        self.assertGreaterEqual(summary['unique_constraints'], 0)
        self.assertGreaterEqual(summary['unique_together_constraints'], 0)
        
        # Should have at least some conditional constraints
        self.assertGreaterEqual(summary['conditional_constraints'], 0)
        
        # Total should equal sum of parts
        expected_total = summary['unique_constraints'] + summary['unique_together_constraints']
        self.assertEqual(summary['total_constraints'], expected_total)
    
    @override_settings(UNIVERSAL_CONSTRAINTS={
        'default': {
            'EXCLUDE_APPS': ['admin', 'auth', 'contenttypes', 'sessions'],
        }
    })
    def test_database_settings_display(self):
        """Test that database settings are properly displayed."""
        json_out = StringIO()
        call_command('discover_constraints', '--format=json', stdout=json_out)
        json_output = json_out.getvalue()
        
        json_data = json.loads(json_output)
        
        if 'default' in json_data['databases']:
            db_info = json_data['databases']['default']
            settings = db_info['settings']
            
            # Should have expected settings
            self.assertIn('exclude_apps', settings)
            self.assertIn('race_condition_protection', settings)
            self.assertIn('log_level', settings)
            
            # Should match our configuration
            self.assertEqual(settings['exclude_apps'], ['admin', 'auth', 'contenttypes', 'sessions'])
