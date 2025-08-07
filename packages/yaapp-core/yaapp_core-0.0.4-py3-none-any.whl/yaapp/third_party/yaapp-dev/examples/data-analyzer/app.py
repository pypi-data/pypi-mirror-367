#!/usr/bin/env python3
"""
Data Analyzer - An advanced example using yaapp

This example demonstrates:
- Data analysis and statistics
- Chart generation and visualization
- Multiple data format support (CSV, JSON, XML)
- Mathematical computations
- Report generation
"""

import csv
import io
import json
import math
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path to import yaapp
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp

# Create yaapp application
app = Yaapp()


@dataclass
class Dataset:
    name: str
    data: List[Dict[str, Any]]
    columns: List[str]
    size: int
    created_at: str


class DataLoader:
    """Handle different data formats."""

    @staticmethod
    def load_csv(file_path: str) -> Dataset:
        """Load data from CSV file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                data = [row for row in reader]

            columns = list(data[0].keys()) if data else []
            return Dataset(
                name=Path(file_path).stem,
                data=data,
                columns=columns,
                size=len(data),
                created_at=datetime.now().isoformat(),
            )
        except Exception as e:
            raise ValueError(f"Error loading CSV: {str(e)}")

    @staticmethod
    def load_json(file_path: str) -> Dataset:
        """Load data from JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("JSON must contain an array of objects")

            columns = list(data[0].keys()) if data else []
            return Dataset(
                name=Path(file_path).stem,
                data=data,
                columns=columns,
                size=len(data),
                created_at=datetime.now().isoformat(),
            )
        except Exception as e:
            raise ValueError(f"Error loading JSON: {str(e)}")

    @staticmethod
    def parse_csv_string(csv_string: str, name: str = "dataset") -> Dataset:
        """Parse CSV from string."""
        try:
            reader = csv.DictReader(io.StringIO(csv_string))
            data = [row for row in reader]
            columns = list(data[0].keys()) if data else []

            return Dataset(
                name=name,
                data=data,
                columns=columns,
                size=len(data),
                created_at=datetime.now().isoformat(),
            )
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {str(e)}")


class StatisticalAnalyzer:
    """Advanced statistical analysis functions."""

    @staticmethod
    def descriptive_stats(values: List[float]) -> Dict[str, float]:
        """Calculate descriptive statistics."""
        if not values:
            return {"error": "No values provided"}

        try:
            return {
                "count": len(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "mode": statistics.mode(values)
                if len(set(values)) < len(values)
                else None,
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "variance": statistics.variance(values) if len(values) > 1 else 0,
                "min": min(values),
                "max": max(values),
                "range": max(values) - min(values),
                "q1": statistics.quantiles(values, n=4)[0]
                if len(values) >= 4
                else None,
                "q3": statistics.quantiles(values, n=4)[2]
                if len(values) >= 4
                else None,
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def correlation(x_values: List[float], y_values: List[float]) -> Dict[str, float]:
        """Calculate correlation between two variables."""
        if len(x_values) != len(y_values):
            return {"error": "Lists must have the same length"}

        if len(x_values) < 2:
            return {"error": "Need at least 2 data points"}

        try:
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            sum_y2 = sum(y * y for y in y_values)

            numerator = n * sum_xy - sum_x * sum_y
            denominator = math.sqrt(
                (n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)
            )

            correlation = numerator / denominator if denominator != 0 else 0

            return {
                "correlation_coefficient": correlation,
                "correlation_strength": (
                    "Very Strong"
                    if abs(correlation) >= 0.8
                    else "Strong"
                    if abs(correlation) >= 0.6
                    else "Moderate"
                    if abs(correlation) >= 0.4
                    else "Weak"
                    if abs(correlation) >= 0.2
                    else "Very Weak"
                ),
                "r_squared": correlation**2,
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def regression_analysis(
        x_values: List[float], y_values: List[float]
    ) -> Dict[str, Any]:
        """Perform linear regression analysis."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return {"error": "Invalid input data"}

        try:
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)

            # Calculate slope and intercept
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
            intercept = (sum_y - slope * sum_x) / n

            # Calculate predictions and residuals
            predictions = [slope * x + intercept for x in x_values]
            residuals = [y - pred for y, pred in zip(y_values, predictions)]

            # Calculate R-squared
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in y_values)
            ss_res = sum(r**2 for r in residuals)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

            return {
                "slope": slope,
                "intercept": intercept,
                "equation": f"y = {slope:.4f}x + {intercept:.4f}",
                "r_squared": r_squared,
                "predictions": predictions,
                "residuals": residuals,
                "mean_squared_error": statistics.mean(r**2 for r in residuals),
                "root_mean_squared_error": math.sqrt(
                    statistics.mean(r**2 for r in residuals)
                ),
            }
        except Exception as e:
            return {"error": str(e)}


# Initialize analyzers
data_loader = DataLoader()
stats_analyzer = StatisticalAnalyzer()


# Expose core data analysis functions
@app.expose
def load_csv_file(file_path: str) -> Dict[str, Any]:
    """Load and analyze a CSV file."""
    try:
        dataset = data_loader.load_csv(file_path)
        return {
            "success": True,
            "dataset": {
                "name": dataset.name,
                "columns": dataset.columns,
                "size": dataset.size,
                "sample_data": dataset.data[:5],  # First 5 rows
            },
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
def analyze_column(csv_string: str, column_name: str) -> Dict[str, Any]:
    """Analyze a specific column from CSV data."""
    try:
        dataset = data_loader.parse_csv_string(csv_string)

        if column_name not in dataset.columns:
            return {
                "error": f"Column '{column_name}' not found. Available: {dataset.columns}"
            }

        # Extract values and try to convert to numbers
        values = []
        non_numeric = []

        for row in dataset.data:
            try:
                val = float(row[column_name])
                values.append(val)
            except (ValueError, TypeError):
                non_numeric.append(row[column_name])

        result = {
            "column": column_name,
            "total_rows": len(dataset.data),
            "numeric_values": len(values),
            "non_numeric_values": len(non_numeric),
        }

        if values:
            result["statistics"] = stats_analyzer.descriptive_stats(values)

        if non_numeric:
            # Frequency analysis for non-numeric data
            freq = {}
            for val in non_numeric:
                freq[str(val)] = freq.get(str(val), 0) + 1
            result["value_counts"] = dict(
                sorted(freq.items(), key=lambda x: x[1], reverse=True)
            )

        return result
    except Exception as e:
        return {"error": str(e)}


@app.expose
def compare_columns(csv_string: str, col1: str, col2: str) -> Dict[str, Any]:
    """Compare two columns and calculate correlation."""
    try:
        dataset = data_loader.parse_csv_string(csv_string)

        missing_cols = [col for col in [col1, col2] if col not in dataset.columns]
        if missing_cols:
            return {
                "error": f"Columns not found: {missing_cols}. Available: {dataset.columns}"
            }

        # Extract numeric values
        x_values = []
        y_values = []

        for row in dataset.data:
            try:
                x_val = float(row[col1])
                y_val = float(row[col2])
                x_values.append(x_val)
                y_values.append(y_val)
            except (ValueError, TypeError):
                continue

        if len(x_values) < 2:
            return {"error": "Not enough numeric values for comparison"}

        result = {
            "column_1": col1,
            "column_2": col2,
            "valid_pairs": len(x_values),
            "correlation": stats_analyzer.correlation(x_values, y_values),
            "regression": stats_analyzer.regression_analysis(x_values, y_values),
        }

        return result
    except Exception as e:
        return {"error": str(e)}


@app.expose
class DataVisualizer:
    """Generate simple text-based visualizations."""

    def histogram(self, values: List[float], bins: int = 10) -> str:
        """Create a text-based histogram."""
        if not values:
            return "No data to visualize"

        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins

        # Count values in each bin
        bin_counts = [0] * bins
        for val in values:
            bin_index = min(int((val - min_val) / bin_width), bins - 1)
            bin_counts[bin_index] += 1

        # Create histogram
        max_count = max(bin_counts)
        scale = 50 / max_count if max_count > 0 else 1

        result = []
        result.append(f"Histogram ({len(values)} values, {bins} bins)")
        result.append("-" * 60)

        for i, count in enumerate(bin_counts):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            bar = "█" * int(count * scale)
            result.append(f"{bin_start:6.2f}-{bin_end:6.2f} |{bar:<50} {count}")

        return "\n".join(result)

    def summary_table(self, data: Dict[str, Any]) -> str:
        """Create a formatted summary table."""
        lines = []
        lines.append("Data Summary")
        lines.append("=" * 40)

        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"\n{key.upper()}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, float):
                        lines.append(f"  {sub_key:<20}: {sub_value:>10.4f}")
                    else:
                        lines.append(f"  {sub_key:<20}: {sub_value:>10}")
            else:
                if isinstance(value, float):
                    lines.append(f"{key:<20}: {value:>10.4f}")
                else:
                    lines.append(f"{key:<20}: {value:>10}")

        return "\n".join(lines)


# Expose advanced functionality via dictionary tree
app.expose(
    {
        "math": {
            "basic_stats": lambda values: stats_analyzer.descriptive_stats(
                [float(x) for x in values.split(",")]
            ),
            "correlation": lambda x_vals, y_vals: stats_analyzer.correlation(
                [float(x) for x in x_vals.split(",")],
                [float(y) for y in y_vals.split(",")],
            ),
            "linear_regression": lambda x_vals, y_vals: stats_analyzer.regression_analysis(
                [float(x) for x in x_vals.split(",")],
                [float(y) for y in y_vals.split(",")],
            ),
        },
        "generators": {
            "sample_csv": lambda rows=10: generate_sample_csv(int(rows)),
            "random_data": lambda size=100: generate_random_dataset(int(size)),
            "test_data": lambda: get_test_datasets(),
        },
        "reports": {
            "full_analysis": lambda csv_data: perform_full_analysis(csv_data),
            "column_report": lambda csv_data, column: generate_column_report(
                csv_data, column
            ),
            "comparison_report": lambda csv_data, col1, col2: generate_comparison_report(
                csv_data, col1, col2
            ),
        },
    }
)


def generate_sample_csv(rows: int) -> str:
    """Generate sample CSV data for testing."""
    import random

    header = "id,name,age,salary,department,score"
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance"]
    names = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry"]

    lines = [header]
    for i in range(rows):
        row = [
            str(i + 1),
            random.choice(names),
            str(random.randint(22, 65)),
            str(random.randint(30000, 120000)),
            random.choice(departments),
            str(round(random.uniform(1.0, 5.0), 2)),
        ]
        lines.append(",".join(row))

    return "\n".join(lines)


def generate_random_dataset(size: int) -> Dict[str, Any]:
    """Generate random dataset for analysis."""
    import random

    data = []
    for i in range(size):
        x = random.uniform(0, 100)
        y = 2 * x + random.uniform(-10, 10)  # Linear relationship with noise
        data.append({"x": x, "y": y, "category": random.choice(["A", "B", "C"])})

    return {
        "size": size,
        "data": data,
        "description": "Random dataset with linear relationship between x and y",
    }


def get_test_datasets() -> Dict[str, str]:
    """Get pre-defined test datasets."""
    return {
        "simple": "x,y\n1,2\n2,4\n3,6\n4,8\n5,10",
        "sales": "month,revenue,costs\nJan,10000,7000\nFeb,12000,8000\nMar,15000,9000\nApr,11000,7500",
        "students": "name,math,science,english\nAlice,85,92,78\nBob,78,85,88\nCarol,92,95,85\nDavid,88,78,92",
    }


def perform_full_analysis(csv_data: str) -> Dict[str, Any]:
    """Perform comprehensive analysis on dataset."""
    try:
        dataset = data_loader.parse_csv_string(csv_data)

        analysis = {
            "dataset_info": {
                "rows": dataset.size,
                "columns": len(dataset.columns),
                "column_names": dataset.columns,
            },
            "column_analysis": {},
        }

        # Analyze each column
        for column in dataset.columns:
            values = []
            non_numeric = []

            for row in dataset.data:
                try:
                    val = float(row[column])
                    values.append(val)
                except (ValueError, TypeError):
                    non_numeric.append(row[column])

            col_analysis = {
                "total_values": len(dataset.data),
                "numeric_count": len(values),
                "non_numeric_count": len(non_numeric),
            }

            if values:
                col_analysis["statistics"] = stats_analyzer.descriptive_stats(values)

            if non_numeric:
                freq = {}
                for val in non_numeric:
                    freq[str(val)] = freq.get(str(val), 0) + 1
                col_analysis["value_counts"] = dict(
                    sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
                )

            analysis["column_analysis"][column] = col_analysis

        return analysis
    except Exception as e:
        return {"error": str(e)}


def generate_column_report(csv_data: str, column: str) -> str:
    """Generate a detailed text report for a column."""
    analysis = analyze_column(csv_data, column)

    if "error" in analysis:
        return f"Error: {analysis['error']}"

    visualizer = DataVisualizer()
    return visualizer.summary_table(analysis)


def generate_comparison_report(csv_data: str, col1: str, col2: str) -> str:
    """Generate a comparison report between two columns."""
    analysis = compare_columns(csv_data, col1, col2)

    if "error" in analysis:
        return f"Error: {analysis['error']}"

    visualizer = DataVisualizer()
    return visualizer.summary_table(analysis)


if __name__ == "__main__":
    app.run()
