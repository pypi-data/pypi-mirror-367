"""
Management command to discover constraints that would be processed.

This command shows all models and constraints that would be converted
to application-level validation based on the current UNIVERSAL_CONSTRAINTS settings.
"""

import json
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import router

from universal_constraints.constraint_converter import get_constraint_info
from universal_constraints.settings import constraint_settings


class Command(BaseCommand):
    help = 'Show all models and constraints that would be processed based on current settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'json'],
            default='text',
            help='Output format (text or json)'
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        self.options = options
        
        # Get all configured databases
        configured_databases = list(constraint_settings._db_settings.keys())
        
        if not configured_databases:
            self.stdout.write(
                self.style.WARNING(
                    "No databases configured in UNIVERSAL_CONSTRAINTS settings.\n"
                    "Add database configuration to settings.py to enable constraint processing."
                )
            )
            return
        
        if options['format'] == 'json':
            self._output_json(configured_databases)
        else:
            self._output_text(configured_databases)

    def _collect_database_info(self, configured_databases):
        """Collect constraint information for all databases (shared by text and JSON output)."""
        databases_info = {}
        
        # Initialize summary counters
        total_models = 0
        total_unique_constraints = 0
        total_unique_together = 0
        total_conditional = 0
        
        for db_alias in configured_databases:
            db_settings = constraint_settings.get_database_settings(db_alias)
            
            # Collect models for this database (respecting database routing)
            models_info = []
            for model in apps.get_models():
                # Check if this model should be processed for this database
                if (constraint_settings.should_process_model(model, db_alias) and
                    self._should_model_use_database(model, db_alias)):
                    info = get_constraint_info(model)
                    if info['constraints'] or info['unique_together']:
                        models_info.append((model, info))
                        
                        # Update summary counters
                        total_models += 1
                        total_unique_constraints += len(info['constraints'])
                        total_unique_together += len(info['unique_together'])
                        total_conditional += len([c for c in info['constraints'] if c['condition']])
            
            databases_info[db_alias] = {
                'settings': db_settings,
                'models': models_info,
            }
        
        # Add consolidated summary to the result
        databases_info['_summary'] = {
            'databases_configured': len(configured_databases),
            'total_models': total_models,
            'total_unique_constraints': total_unique_constraints,
            'total_unique_together': total_unique_together,
            'total_constraints': total_unique_constraints + total_unique_together,  # Combined total
            'conditional_constraints': total_conditional
        }
        
        return databases_info
    
    def _should_model_use_database(self, model, db_alias):
        """Check if a model should use a specific database according to Django's routing."""
        # Use Django's router to determine the correct database for this model
        suggested_db = router.db_for_write(model)
        return suggested_db == db_alias or suggested_db is None

    def _output_text(self, configured_databases):
        """Output results in text format."""
        databases_info = self._collect_database_info(configured_databases)
        summary = databases_info['_summary']
        
        self.stdout.write("Universal Constraints Discovery")
        self.stdout.write("=" * 50)
        
        for db_alias, db_info in databases_info.items():
            if db_alias == '_summary':  # Skip the summary entry
                continue
                
            db_settings = db_info['settings']
            models_info = db_info['models']
            
            self.stdout.write(f"\nDatabase: {db_alias}")
            
            exclude_apps = db_settings.get('EXCLUDE_APPS', [])
            if exclude_apps:
                self.stdout.write(f"  Excluded apps: {', '.join(exclude_apps)}")
            else:
                self.stdout.write("  Excluded apps: none")
            
            if models_info:
                self.stdout.write("  \n  Models with constraints:")
                
                for model, info in models_info:
                    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
                    
                    self.stdout.write(f"  ├── {model_label}")
                    
                    # Show UniqueConstraints
                    for constraint in info['constraints']:
                        fields_str = ', '.join(constraint['fields'])
                        if constraint['condition']:
                            self.stdout.write(f"  │   └── {constraint['name']} (conditional: {constraint['condition']})")
                        else:
                            self.stdout.write(f"  │   └── {constraint['name']} ({fields_str})")
                    
                    # Show unique_together
                    for fields in info['unique_together']:
                        fields_str = ', '.join(fields)
                        self.stdout.write(f"  │   └── unique_together: [{fields_str}]")
            else:
                self.stdout.write("  \n  No models with constraints found")
        
        # Use consolidated summary
        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"  Databases configured: {summary['databases_configured']}")
        self.stdout.write(f"  Models to process: {summary['total_models']}")
        self.stdout.write(f"  Total constraints: {summary['total_constraints']}")
        self.stdout.write(f"    - UniqueConstraints: {summary['total_unique_constraints']} ({summary['conditional_constraints']} conditional)")
        self.stdout.write(f"    - unique_together: {summary['total_unique_together']}")

    def _output_json(self, configured_databases):
        """Output results in JSON format."""
        databases_info = self._collect_database_info(configured_databases)
        summary = databases_info['_summary']
        
        result = {
            'databases': {},
            'summary': {
                'databases_configured': summary['databases_configured'],
                'total_models': summary['total_models'],
                'total_constraints': summary['total_constraints'],  # Combined total (UniqueConstraints + unique_together)
                'unique_constraints': summary['total_unique_constraints'],
                'unique_together_constraints': summary['total_unique_together'],
                'conditional_constraints': summary['conditional_constraints']
            }
        }
        
        for db_alias, db_info in databases_info.items():
            if db_alias == '_summary':  # Skip the summary entry
                continue
                
            db_settings = db_info['settings']
            models_info = db_info['models']
            
            db_result = {
                'settings': {
                    'exclude_apps': db_settings.get('EXCLUDE_APPS', []),
                    'race_condition_protection': db_settings.get('RACE_CONDITION_PROTECTION', True),
                    'log_level': db_settings.get('LOG_LEVEL', 'INFO'),
                },
                'models': {}
            }
            
            for model, info in models_info:
                model_label = f"{model._meta.app_label}.{model._meta.model_name}"
                
                # Convert constraints to JSON-serializable format
                json_constraints = []
                for constraint in info['constraints']:
                    json_constraint = {
                        'name': constraint['name'],
                        'fields': constraint['fields'],
                        'condition': str(constraint['condition']) if constraint['condition'] else None
                    }
                    json_constraints.append(json_constraint)
                
                db_result['models'][model_label] = {
                    'app_label': model._meta.app_label,
                    'model_name': model._meta.model_name,
                    'unique_constraints': json_constraints,
                    'unique_together': info['unique_together']
                }
            
            result['databases'][db_alias] = db_result
        
        self.stdout.write(json.dumps(result, indent=2))
