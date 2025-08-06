"""
Simple command-line interface focused on core functionality.
"""

import click
import logging
import sys
import csv
import pandas as pd
from pathlib import Path

# Handle both direct execution and module import
try:
    from .simple_analyzer import analyze_imputation_requirements, analyze_dataframe
    from .models import AnalysisConfig
    from .io import save_suggestions, load_data
    from .metadata_inference import infer_metadata_from_dataframe
except ImportError:
    # Direct execution - add parent directory to path
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from funimpute.simple_analyzer import analyze_imputation_requirements, analyze_dataframe
    from funimpute.models import AnalysisConfig
    from funimpute.io import save_suggestions, load_data
    from funimpute.metadata_inference import infer_metadata_from_dataframe


@click.group()
def cli():
    """FunPuter - Intelligent Imputation Analysis"""
    pass


@cli.command()
@click.option('--data', '-d',
              required=True, 
              help='Path to data CSV file to analyze')
@click.option('--output', '-o',
              default='metadata.csv',
              help='Output path for metadata template (default: metadata.csv)')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose logging')
def init(data, output, verbose):
    """
    Generate a metadata template CSV by analyzing your data file.
    
    This command scans your CSV file, infers data types and constraints,
    and creates a metadata template with placeholders for business rules
    that you can customize before running analysis.
    
    Examples:
    
    # Generate metadata template
    funimputer init -d data.csv
    
    # Specify custom output location
    funimputer init -d data.csv -o my_metadata.csv
    
    # With verbose output
    funimputer init -d data.csv --verbose
    """
    if verbose:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
    
    try:
        # Load and analyze the data
        if verbose:
            click.echo(f"INFO: Analyzing data file: {data}")
        
        df = pd.read_csv(data)
        if verbose:
            click.echo(f"INFO: Loaded {len(df)} rows and {len(df.columns)} columns")
        
        # Infer metadata
        if verbose:
            click.echo("INFO: Inferring metadata and data types...")
        
        inferred_metadata = infer_metadata_from_dataframe(df)
        
        # Generate metadata template with placeholders
        template_rows = []
        for metadata in inferred_metadata:
            # Create template row with inferred values and placeholders
            # Handle both string and enum data types
            data_type_str = metadata.data_type.value if hasattr(metadata.data_type, 'value') else str(metadata.data_type)
            
            template_row = {
                'column_name': metadata.column_name,
                'data_type': data_type_str,
                'min_value': metadata.min_value if metadata.min_value is not None else '',
                'max_value': metadata.max_value if metadata.max_value is not None else '',
                'max_length': metadata.max_length if metadata.max_length is not None else '',
                'unique_flag': 'TRUE' if getattr(metadata, 'unique_flag', False) else 'FALSE',
                'nullable': 'TRUE' if getattr(metadata, 'nullable', True) else 'FALSE',
                'allowed_values': '',  # Placeholder for user to fill with categorical values
                'dependent_column': getattr(metadata, 'dependent_column', '') or '',  # Placeholder for user to fill
                'dependency_rule': '',  # Placeholder for user to fill
                'business_rule': getattr(metadata, 'business_rule', '') or '',  # Placeholder for user to fill
                'description': getattr(metadata, 'description', '') or f'Auto-inferred {data_type_str} column'
            }
            template_rows.append(template_row)
        
        # Write template to CSV
        if verbose:
            click.echo(f"INFO: Writing metadata template to: {output}")
        
        with open(output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['column_name', 'data_type', 'min_value', 'max_value', 'max_length', 
                         'unique_flag', 'nullable', 'allowed_values', 'dependent_column', 'dependency_rule', 'business_rule', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(template_rows)
        
        # Success message
        click.echo(f"✅ Metadata template created: {output}")
        click.echo(f"📊 Analyzed {len(template_rows)} columns")
        click.echo("\n📝 Next steps:")
        click.echo("1. Review and customize the generated metadata template")
        click.echo("2. Fill in business rules, dependencies, and missing strategy hints")
        click.echo(f"3. Run analysis: funimputer analyze -m {output} -d {data}")
        
        if verbose:
            click.echo("\n🔍 Column summary:")
            for row in template_rows:
                click.echo(f"  - {row['column_name']}: {row['data_type']}")
        
    except FileNotFoundError:
        click.echo(f"❌ Error: Data file not found: {data}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error generating metadata template: {str(e)}", err=True)
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.option('--metadata', '-m', 
              required=False,
              help='Path to metadata CSV file (optional - will auto-infer if not provided)')
@click.option('--data', '-d',
              required=True, 
              help='Path to data CSV file')
@click.option('--output', '-o',
              help='Output path for suggestions CSV (default: suggestions.csv)')
@click.option('--config', '-c',
              help='Path to configuration YAML file')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Enable verbose logging')
def analyze(metadata, data, output, config, verbose):
    """
    Analyze dataset and suggest imputation methods.
    
    Examples:
    
    # Auto-infer metadata (recommended for quick analysis)
    funimputer analyze -d data.csv
    
    # With explicit metadata (recommended for production)
    funimputer analyze -m metadata.csv -d data.csv
    
    # Save results to specific file
    funimputer analyze -d data.csv -o my_suggestions.csv
    
    # With verbose output
    funimputer analyze -d data.csv --verbose
    
    # With custom configuration
    funimputer analyze -m metadata.csv -d data.csv -c config.yml
    """
    
    # Setup logging
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s',
        stream=sys.stdout
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration if provided
        analysis_config = AnalysisConfig()
        if config:
            try:
                from .io import load_configuration
            except ImportError:
                from funimpute.io import load_configuration
            analysis_config = load_configuration(config)
        
        # Handle metadata: explicit file or auto-inference
        if metadata:
            if verbose:
                click.echo(f"INFO: Analyzing {data} with explicit metadata {metadata}")
            else:
                logger.info(f"Analyzing {data} with explicit metadata {metadata}")
            suggestions = analyze_imputation_requirements(
                metadata_path=metadata,
                data_path=data,
                config=analysis_config
            )
        else:
            if verbose:
                click.echo(f"INFO: Analyzing {data} with auto-inferred metadata")
            else:
                logger.info(f"Analyzing {data} with auto-inferred metadata")
            # Load data and infer metadata
            try:
                import pandas as pd
                df = pd.read_csv(data)
            except Exception as e:
                raise FileNotFoundError(f"Could not load data file {data}: {e}")
                
            inferred_metadata = infer_metadata_from_dataframe(
                df, 
                warn_user=True
            )
            
            # Run analysis with inferred metadata
            suggestions = analyze_dataframe(
                data=df,
                metadata=inferred_metadata,
                config=analysis_config
            )
        
        # Save results
        output_path = output or "suggestions.csv"
        save_suggestions(suggestions, output_path)
        
        # Display summary
        click.echo(f"\n✓ Analysis complete!")
        click.echo(f"  Columns analyzed: {len(suggestions)}")
        click.echo(f"  Total missing values: {sum(s.missing_count for s in suggestions):,}")
        avg_confidence = sum(s.confidence_score for s in suggestions) / len(suggestions) if suggestions else 0.0
        click.echo(f"  Average confidence: {avg_confidence:.3f}")
        click.echo(f"  Results saved to: {output_path}")
        
        # Show method distribution
        from collections import Counter
        methods = Counter(s.proposed_method for s in suggestions)
        click.echo(f"\n  Proposed methods:")
        for method, count in methods.most_common():
            click.echo(f"    {method}: {count}")
        
    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if "not found" in str(e).lower():
            click.echo(f"Error: File not found - {e}", err=True)
        else:
            logger.error(f"Analysis failed: {e}")
            click.echo(f"Error: Analysis failed - {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()