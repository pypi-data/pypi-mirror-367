#!/usr/bin/env python3
"""
Async Data Analyzer - Demonstrates YAPP async/sync dual interface

This async version shows:
- Async file I/O operations
- Async data processing with simulated delays
- Async statistical computations
- Mixed sync/async method exposure
"""

import asyncio
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

# Create yapp application
app = Yaapp()


@dataclass
class Dataset:
    name: str
    data: List[Dict[str, Any]]
    columns: List[str]
    size: int
    created_at: str


class AsyncDataLoader:
    """Handle different data formats with async I/O."""

    @staticmethod
    async def load_csv_async(file_path: str) -> Dataset:
        """Load data from CSV file asynchronously."""
        try:
            # Simulate async file reading
            await asyncio.sleep(0.01)  # Simulate I/O delay
            
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
    async def load_json_async(file_path: str) -> Dataset:
        """Load data from JSON file asynchronously."""
        try:
            # Simulate async file reading
            await asyncio.sleep(0.01)
            
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


# Expose async file loading functions
@app.expose
async def load_csv_file_async(file_path: str) -> Dict[str, Any]:
    """Load and return basic info about a CSV file (async version)."""
    try:
        dataset = await AsyncDataLoader.load_csv_async(file_path)
        return {
            "name": dataset.name,
            "columns": dataset.columns,
            "size": dataset.size,
            "sample": dataset.data[:3],  # First 3 rows
            "created_at": dataset.created_at
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
async def analyze_column_async(file_path: str, column: str) -> Dict[str, Any]:
    """Analyze a specific column in the dataset (async version)."""
    try:
        dataset = await AsyncDataLoader.load_csv_async(file_path)
        
        if column not in dataset.columns:
            return {"error": f"Column '{column}' not found"}

        # Extract column values with async processing simulation
        await asyncio.sleep(0.01)  # Simulate processing delay
        
        values = []
        for row in dataset.data:
            try:
                val = float(row[column])
                values.append(val)
            except (ValueError, TypeError):
                continue  # Skip non-numeric values

        if not values:
            return {"error": f"No numeric values found in column '{column}'"}

        # Async statistical computation
        await asyncio.sleep(0.01)  # Simulate computation delay
        
        return {
            "column": column,
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "processed_async": True
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
class AsyncDataProcessor:
    """Data processor with async methods."""
    
    async def process_large_dataset(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a large dataset asynchronously."""
        # Simulate heavy processing
        await asyncio.sleep(0.05)
        
        total_rows = len(data)
        
        # Count numeric columns
        numeric_columns = []
        if data:
            for key, value in data[0].items():
                try:
                    float(value)
                    numeric_columns.append(key)
                except (ValueError, TypeError):
                    continue
        
        return {
            "total_rows": total_rows,
            "numeric_columns": numeric_columns,
            "processing_time": "async",
            "status": "completed"
        }
    
    def get_info(self) -> Dict[str, str]:
        """Get processor info (sync method for comparison)."""
        return {
            "name": "AsyncDataProcessor",
            "version": "1.0",
            "type": "async_capable"
        }


# Mixed async/sync statistical functions
@app.expose
async def async_correlation(file_path: str, col1: str, col2: str) -> Dict[str, Any]:
    """Calculate correlation between two columns asynchronously."""
    try:
        dataset = await AsyncDataLoader.load_csv_async(file_path)
        
        if col1 not in dataset.columns or col2 not in dataset.columns:
            return {"error": "One or both columns not found"}

        # Extract values with async processing
        await asyncio.sleep(0.02)  # Simulate processing delay
        
        values1, values2 = [], []
        for row in dataset.data:
            try:
                v1 = float(row[col1])
                v2 = float(row[col2])
                values1.append(v1)
                values2.append(v2)
            except (ValueError, TypeError):
                continue

        if len(values1) < 2:
            return {"error": "Insufficient numeric data for correlation"}

        # Async correlation calculation
        await asyncio.sleep(0.01)
        
        correlation = statistics.correlation(values1, values2)
        
        return {
            "column1": col1,
            "column2": col2,
            "correlation": correlation,
            "sample_size": len(values1),
            "computed_async": True
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
def sync_basic_stats(numbers: List[float]) -> Dict[str, float]:
    """Calculate basic statistics synchronously for comparison."""
    if not numbers:
        return {"error": "Empty list provided"}
    
    return {
        "count": len(numbers),
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "mode": statistics.mode(numbers) if len(set(numbers)) < len(numbers) else None,
        "computed_sync": True
    }


# Data generation for testing
@app.expose
async def generate_test_data_async(rows: int = 100) -> Dict[str, Any]:
    """Generate test data asynchronously."""
    import random
    
    # Simulate data generation delay
    await asyncio.sleep(0.1)
    
    data = []
    for i in range(rows):
        data.append({
            "id": i + 1,
            "value": random.uniform(1, 100),
            "category": random.choice(["A", "B", "C"]),
            "score": random.randint(1, 10)
        })
        
        # Yield control periodically for long generations
        if i % 50 == 0:
            await asyncio.sleep(0.01)
    
    return {
        "generated_rows": len(data),
        "sample_data": data[:5],
        "columns": ["id", "value", "category", "score"],
        "generation_method": "async"
    }


# Custom async object for advanced processing
class AsyncAnalyzer:
    """Custom analyzer with async capabilities."""
    
    def expose_to_registry(self, name: str, exposer) -> None:
        """Expose this analyzer to the registry."""
        pass
    
    async def execute_call(self, function_name: str, **kwargs) -> Any:
        """Execute analysis functions asynchronously."""
        if function_name == "deep_analysis":
            return await self._deep_analysis(kwargs.get("data", []))
        elif function_name == "pattern_detection":
            return await self._pattern_detection(kwargs.get("values", []))
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    async def _deep_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform deep analysis on the data."""
        # Simulate complex analysis
        await asyncio.sleep(0.1)
        
        if not data:
            return {"error": "No data provided"}
        
        # Analyze patterns
        numeric_fields = []
        text_fields = []
        
        if data:
            for key, value in data[0].items():
                try:
                    float(value)
                    numeric_fields.append(key)
                except (ValueError, TypeError):
                    text_fields.append(key)
        
        return {
            "total_records": len(data),
            "numeric_fields": numeric_fields,
            "text_fields": text_fields,
            "analysis_type": "deep_async",
            "processing_time": "simulated_100ms"
        }
    
    async def _pattern_detection(self, values: List[float]) -> Dict[str, Any]:
        """Detect patterns in numeric values."""
        await asyncio.sleep(0.05)
        
        if not values:
            return {"error": "No values provided"}
        
        # Simple pattern detection
        is_increasing = all(values[i] <= values[i+1] for i in range(len(values)-1))
        is_decreasing = all(values[i] >= values[i+1] for i in range(len(values)-1))
        
        return {
            "values_count": len(values),
            "is_increasing": is_increasing,
            "is_decreasing": is_decreasing,
            "range": max(values) - min(values),
            "pattern_analysis": "async_computed"
        }


# Expose the custom analyzer
async_analyzer = AsyncAnalyzer()
app.expose(async_analyzer, name="async_analyzer", custom=True)


if __name__ == "__main__":
    print("🚀 Async Data Analyzer loaded!")
    print("This version demonstrates async/sync dual interface capabilities.")
    print("Functions are available in both sync and async contexts.")
    app.run()