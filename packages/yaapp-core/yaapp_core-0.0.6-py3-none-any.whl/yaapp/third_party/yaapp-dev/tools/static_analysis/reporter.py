"""
Violation reporting and formatting.
"""

import json
from typing import List, Dict, Any, Optional
from collections import defaultdict

from .rules import RuleViolation, ViolationType


class ViolationReporter:
    """Reports and formats rule violations."""
    
    def format_console_report(self, violations: List[RuleViolation], 
                            show_suggestions: bool = True) -> str:
        """Format violations for console output."""
        if not violations:
            return "✅ No violations found!"
        
        report_lines = []
        report_lines.append(f"❌ Found {len(violations)} violation(s):")
        report_lines.append("")
        
        # Group violations by file
        violations_by_file = defaultdict(list)
        for violation in violations:
            violations_by_file[violation.file_path].append(violation)
        
        for file_path, file_violations in violations_by_file.items():
            report_lines.append(f"📄 {file_path}:")
            
            for violation in sorted(file_violations, key=lambda v: v.line_number):
                report_lines.append(
                    f"  Line {violation.line_number}:{violation.column_number} "
                    f"[{violation.violation_type.value}] {violation.message}"
                )
                
                if show_suggestions and violation.suggestion:
                    report_lines.append(f"    💡 Suggestion: {violation.suggestion}")
                
                if violation.code_snippet:
                    report_lines.append("    Code:")
                    for line in violation.code_snippet.split('\n'):
                        report_lines.append(f"      {line}")
                
                report_lines.append("")
        
        # Add summary
        violation_counts = defaultdict(int)
        for violation in violations:
            violation_counts[violation.violation_type] += 1
        
        report_lines.append("📊 Summary:")
        for violation_type, count in violation_counts.items():
            report_lines.append(f"  {violation_type.value}: {count}")
        
        return "\n".join(report_lines)
    
    def format_json_report(self, violations: List[RuleViolation]) -> str:
        """Format violations as JSON."""
        violations_data = []
        
        for violation in violations:
            violations_data.append({
                "file_path": violation.file_path,
                "line_number": violation.line_number,
                "column_number": violation.column_number,
                "violation_type": violation.violation_type.value,
                "message": violation.message,
                "suggestion": violation.suggestion,
                "code_snippet": violation.code_snippet
            })
        
        return json.dumps({
            "total_violations": len(violations),
            "violations": violations_data
        }, indent=2)
    
    def format_github_annotations(self, violations: List[RuleViolation]) -> str:
        """Format violations as GitHub Actions annotations."""
        annotations = []
        
        for violation in violations:
            level = "error" if violation.violation_type in [
                ViolationType.FORBIDDEN_TRY_EXCEPT,
                ViolationType.INTERNAL_CODE_IN_TRY
            ] else "warning"
            
            annotation = (
                f"::{level} file={violation.file_path},"
                f"line={violation.line_number},"
                f"col={violation.column_number}::"
                f"{violation.message}"
            )
            
            if violation.suggestion:
                annotation += f" Suggestion: {violation.suggestion}"
            
            annotations.append(annotation)
        
        return "\n".join(annotations)
    
    def get_violation_summary(self, violations: List[RuleViolation]) -> Dict[str, Any]:
        """Get summary statistics for violations."""
        if not violations:
            return {
                "total_violations": 0,
                "files_with_violations": 0,
                "violation_types": {},
                "severity_breakdown": {"error": 0, "warning": 0}
            }
        
        files_with_violations = set(v.file_path for v in violations)
        violation_type_counts = defaultdict(int)
        severity_counts = {"error": 0, "warning": 0}
        
        for violation in violations:
            violation_type_counts[violation.violation_type.value] += 1
            
            # Classify severity
            if violation.violation_type in [
                ViolationType.FORBIDDEN_TRY_EXCEPT,
                ViolationType.INTERNAL_CODE_IN_TRY
            ]:
                severity_counts["error"] += 1
            else:
                severity_counts["warning"] += 1
        
        return {
            "total_violations": len(violations),
            "files_with_violations": len(files_with_violations),
            "violation_types": dict(violation_type_counts),
            "severity_breakdown": severity_counts
        }
    
    def save_report(self, violations: List[RuleViolation], output_file: str, 
                   format_type: str = "console"):
        """Save report to file."""
        if format_type == "json":
            content = self.format_json_report(violations)
        elif format_type == "github":
            content = self.format_github_annotations(violations)
        else:
            content = self.format_console_report(violations)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)