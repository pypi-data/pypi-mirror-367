#!/usr/bin/env python3
"""
Standalone runner for yaapp static analysis.

Usage:
    python tools/run_static_analysis.py                    # Analyze entire project
    python tools/run_static_analysis.py src/yaapp/core.py  # Analyze specific file
    python tools/run_static_analysis.py src/              # Analyze directory
"""

import sys
import argparse
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from static_analysis import YaappStaticAnalyzer, AnalysisConfig, ViolationReporter


def main():
    """Main entry point for static analysis."""
    parser = argparse.ArgumentParser(
        description="YApp Static Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Analyze entire project
  %(prog)s src/yaapp/core.py         # Analyze specific file
  %(prog)s src/                      # Analyze directory
  %(prog)s --format json --output report.json  # JSON output
        """
    )
    
    parser.add_argument(
        'paths',
        nargs='*',
        default=['.'],
        help='Files or directories to analyze (default: current directory)'
    )
    
    parser.add_argument(
        '--format',
        choices=['console', 'json', 'github'],
        default='console',
        help='Output format (default: console)'
    )
    
    parser.add_argument(
        '--output',
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--config',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--exclude',
        action='append',
        help='Additional exclude patterns'
    )
    
    parser.add_argument(
        '--no-suggestions',
        action='store_true',
        help='Hide suggestions in console output'
    )
    
    parser.add_argument(
        '--fail-on-violations',
        action='store_true',
        help='Exit with non-zero code if violations found'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = AnalysisConfig()
    if args.exclude:
        config.exclude_patterns.extend(args.exclude)
    
    # Initialize analyzer
    analyzer = YaappStaticAnalyzer(config)
    reporter = ViolationReporter()
    
    # Collect all violations
    all_violations = []
    
    for path in args.paths:
        path_obj = Path(path)
        
        if path_obj.is_file():
            violations = analyzer.analyze_file(str(path_obj))
        elif path_obj.is_dir():
            violations = analyzer.analyze_directory(str(path_obj))
        else:
            print(f"❌ Path not found: {path}", file=sys.stderr)
            sys.exit(1)
        
        all_violations.extend(violations)
    
    # Generate report
    if args.format == 'json':
        report = reporter.format_json_report(all_violations)
    elif args.format == 'github':
        report = reporter.format_github_annotations(all_violations)
    else:
        report = reporter.format_console_report(
            all_violations, 
            show_suggestions=not args.no_suggestions
        )
    
    # Output report
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to {args.output}")
    else:
        print(report)
    
    # Print summary
    summary = reporter.get_violation_summary(all_violations)
    if args.format == 'console':
        print(f"\n🔍 Analysis complete: {summary['total_violations']} violations found")
        if summary['total_violations'] > 0:
            print(f"📁 Files affected: {summary['files_with_violations']}")
            print(f"🚨 Errors: {summary['severity_breakdown']['error']}")
            print(f"⚠️  Warnings: {summary['severity_breakdown']['warning']}")
    
    # Exit with appropriate code
    if args.fail_on_violations and all_violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()