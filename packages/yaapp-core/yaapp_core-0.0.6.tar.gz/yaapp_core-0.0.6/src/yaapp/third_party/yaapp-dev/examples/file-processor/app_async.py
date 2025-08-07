#!/usr/bin/env python3
"""
Async File Processor - Demonstrates YAPP async file operations

This async version shows:
- Async file I/O operations
- Async text processing and analysis  
- Concurrent file processing
- Mixed sync/async file operations
"""

import asyncio
import sys
import json
import csv
import os
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import re

# Add parent directory to path to import yaapp
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp

# Create yapp application
app = Yaapp()


# Basic async file operations
@app.expose
async def read_file_async(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Read file contents asynchronously."""
    try:
        # Simulate async file reading
        await asyncio.sleep(0.01)
        
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Simulate processing delay
        await asyncio.sleep(0.005)
        
        return {
            "file_path": str(path),
            "size_bytes": len(content.encode(encoding)),
            "size_chars": len(content),
            "lines": len(content.splitlines()),
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "read_method": "async"
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
async def write_file_async(file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Write content to file asynchronously."""
    try:
        # Simulate async file writing
        await asyncio.sleep(0.01)
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return {
            "file_path": str(path), 
            "bytes_written": len(content.encode(encoding)),
            "lines_written": len(content.splitlines()),
            "write_method": "async",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
async def list_files_async(directory: str = ".", pattern: str = "*") -> Dict[str, Any]:
    """List files in directory asynchronously."""
    try:
        # Simulate async directory scanning
        await asyncio.sleep(0.02)
        
        path = Path(directory)
        if not path.exists():
            return {"error": f"Directory not found: {directory}"}
        
        if not path.is_dir():
            return {"error": f"Not a directory: {directory}"}
        
        files = []
        for file_path in path.glob(pattern):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return {
            "directory": str(path),
            "pattern": pattern,
            "files": files,
            "count": len(files),
            "scanned_async": True
        }
    except Exception as e:
        return {"error": str(e)}


# Async text processing
@app.expose
class AsyncTextProcessor:
    """Text processor with async methods."""
    
    async def analyze_text_async(self, text: str) -> Dict[str, Any]:
        """Analyze text content asynchronously."""
        # Simulate processing delay for large text
        if len(text) > 1000:
            await asyncio.sleep(0.05)
        else:
            await asyncio.sleep(0.01)
        
        lines = text.splitlines()
        words = text.split()
        
        # Count different types of characters
        char_counts = {
            'letters': sum(1 for c in text if c.isalpha()),
            'digits': sum(1 for c in text if c.isdigit()),
            'spaces': sum(1 for c in text if c.isspace()),
            'punctuation': sum(1 for c in text if not c.isalnum() and not c.isspace())
        }
        
        return {
            "char_count": len(text),
            "word_count": len(words),
            "line_count": len(lines),
            "char_breakdown": char_counts,
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "analysis_method": "async"
        }
    
    async def extract_patterns_async(self, text: str, pattern: str) -> Dict[str, Any]:
        """Extract patterns from text asynchronously."""
        # Simulate pattern processing delay
        await asyncio.sleep(0.02)
        
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            unique_matches = list(set(matches))
            
            return {
                "pattern": pattern,
                "total_matches": len(matches),
                "unique_matches": len(unique_matches),
                "matches": matches[:20],  # First 20 matches
                "unique_values": unique_matches[:10],  # First 10 unique
                "extraction_method": "async_regex"
            }
        except re.error as e:
            return {"error": f"Invalid regex pattern: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_processor_info(self) -> Dict[str, str]:
        """Get processor info (sync method for comparison)."""
        return {
            "name": "AsyncTextProcessor",
            "version": "1.0",
            "capabilities": "async_text_processing",
            "info_method": "sync"
        }


# Async file conversion operations
@app.expose
async def convert_csv_to_json_async(csv_path: str, json_path: str) -> Dict[str, Any]:
    """Convert CSV to JSON asynchronously."""
    try:
        # Simulate async file operations
        await asyncio.sleep(0.01)
        
        if not Path(csv_path).exists():
            return {"error": f"CSV file not found: {csv_path}"}
        
        # Read CSV
        data = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
                # Yield control for large files
                if len(data) % 100 == 0:
                    await asyncio.sleep(0.001)
        
        # Simulate processing delay
        await asyncio.sleep(0.01)
        
        # Write JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            "input_file": csv_path,
            "output_file": json_path,
            "records_converted": len(data),
            "conversion_method": "async",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@app.expose
async def convert_json_to_csv_async(json_path: str, csv_path: str) -> Dict[str, Any]:
    """Convert JSON to CSV asynchronously."""
    try:
        # Simulate async file operations  
        await asyncio.sleep(0.01)
        
        if not Path(json_path).exists():
            return {"error": f"JSON file not found: {json_path}"}
        
        # Read JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list) or not data:
            return {"error": "JSON must contain a non-empty array of objects"}
        
        # Simulate processing delay
        await asyncio.sleep(0.01)
        
        # Write CSV
        fieldnames = data[0].keys()
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                writer.writerow(row)
                # Yield control for large files
                if len(data) % 100 == 0:
                    await asyncio.sleep(0.001)
        
        return {
            "input_file": json_path,
            "output_file": csv_path,
            "records_converted": len(data),
            "columns": list(fieldnames),
            "conversion_method": "async",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


# Concurrent file processing
@app.expose
async def process_multiple_files_async(file_paths: List[str], operation: str = "analyze") -> Dict[str, Any]:
    """Process multiple files concurrently."""
    try:
        async def process_single_file(file_path: str) -> Dict[str, Any]:
            """Process a single file."""
            try:
                if not Path(file_path).exists():
                    return {
                        "file": file_path,
                        "success": False,
                        "error": "file_not_found"
                    }
                
                # Simulate file processing based on operation
                if operation == "analyze":
                    await asyncio.sleep(0.02)  # Simulate analysis
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    return {
                        "file": file_path,
                        "success": True,
                        "size": len(content),
                        "lines": len(content.splitlines()),
                        "operation": "analyze"
                    }
                elif operation == "count_words":
                    await asyncio.sleep(0.01)  # Simulate word counting
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    word_count = len(content.split())
                    return {
                        "file": file_path,
                        "success": True,
                        "word_count": word_count,
                        "operation": "count_words"
                    }
                else:
                    return {
                        "file": file_path,
                        "success": False,
                        "error": f"unknown_operation: {operation}"
                    }
            except Exception as e:
                return {
                    "file": file_path,
                    "success": False,
                    "error": str(e)
                }
        
        # Process files concurrently
        results = await asyncio.gather(
            *[process_single_file(path) for path in file_paths],
            return_exceptions=True
        )
        
        # Collect results
        successful = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed = [r for r in results if isinstance(r, dict) and not r.get("success")]
        exceptions = [r for r in results if not isinstance(r, dict)]
        
        return {
            "total_files": len(file_paths),
            "successful": len(successful),
            "failed": len(failed),
            "exceptions": len(exceptions),
            "results": results,
            "operation": operation,
            "processing_method": "concurrent_async"
        }
    except Exception as e:
        return {"error": str(e)}


# Async batch operations
@app.expose
async def backup_files_async(source_dir: str, backup_dir: str, pattern: str = "*.txt") -> Dict[str, Any]:
    """Backup files matching pattern asynchronously."""
    try:
        source_path = Path(source_dir)
        backup_path = Path(backup_dir)
        
        if not source_path.exists():
            return {"error": f"Source directory not found: {source_dir}"}
        
        # Create backup directory
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Find files to backup
        files_to_backup = list(source_path.glob(pattern))
        
        async def backup_single_file(file_path: Path) -> Dict[str, Any]:
            """Backup a single file."""
            try:
                # Simulate backup operation
                await asyncio.sleep(0.01)
                
                dest_path = backup_path / file_path.name
                
                # Copy file content
                with open(file_path, 'r', encoding='utf-8') as src:
                    content = src.read()
                
                with open(dest_path, 'w', encoding='utf-8') as dest:
                    dest.write(content)
                
                return {
                    "source": str(file_path),
                    "destination": str(dest_path),
                    "success": True,
                    "size": len(content)
                }
            except Exception as e:
                return {
                    "source": str(file_path),
                    "success": False,
                    "error": str(e)
                }
        
        # Backup files concurrently (in batches to avoid overwhelming)
        batch_size = 5
        all_results = []
        
        for i in range(0, len(files_to_backup), batch_size):
            batch = files_to_backup[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[backup_single_file(f) for f in batch],
                return_exceptions=True
            )
            all_results.extend(batch_results)
            
            # Small delay between batches
            await asyncio.sleep(0.005)
        
        successful_backups = [r for r in all_results if isinstance(r, dict) and r.get("success")]
        failed_backups = [r for r in all_results if isinstance(r, dict) and not r.get("success")]
        
        return {
            "source_directory": source_dir,
            "backup_directory": backup_dir,
            "pattern": pattern,
            "total_files": len(files_to_backup),
            "successful_backups": len(successful_backups),
            "failed_backups": len(failed_backups),
            "backup_results": all_results,
            "backup_method": "async_concurrent",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


# Custom async file processor
class AsyncFileProcessor:
    """Custom file processor with async capabilities."""
    
    def expose_to_registry(self, name: str, exposer) -> None:
        """Expose this processor to the registry."""
        pass
    
    async def execute_call(self, function_name: str, **kwargs) -> Any:
        """Execute file processing functions asynchronously."""
        if function_name == "bulk_rename":
            return await self._bulk_rename(
                kwargs.get("directory", "."),
                kwargs.get("pattern", "*.txt"),
                kwargs.get("prefix", "renamed_")
            )
        elif function_name == "calculate_checksums":
            return await self._calculate_checksums(kwargs.get("file_paths", []))
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    async def _bulk_rename(self, directory: str, pattern: str, prefix: str) -> Dict[str, Any]:
        """Rename multiple files with a prefix."""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return {"error": f"Directory not found: {directory}"}
            
            files_to_rename = list(dir_path.glob(pattern))
            renamed_files = []
            
            for file_path in files_to_rename:
                # Simulate rename operation
                await asyncio.sleep(0.005)
                
                new_name = prefix + file_path.name
                new_path = file_path.parent / new_name
                
                # In a real implementation, would actually rename
                # file_path.rename(new_path)
                
                renamed_files.append({
                    "original": str(file_path),
                    "renamed": str(new_path),
                    "simulated": True
                })
            
            return {
                "directory": directory,
                "pattern": pattern,
                "prefix": prefix,
                "files_processed": len(renamed_files),
                "renamed_files": renamed_files,
                "operation": "bulk_rename_async"
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _calculate_checksums(self, file_paths: List[str]) -> Dict[str, Any]:
        """Calculate checksums for multiple files."""
        import hashlib
        
        try:
            async def checksum_file(file_path: str) -> Dict[str, Any]:
                """Calculate checksum for a single file."""
                try:
                    # Simulate checksum calculation delay
                    await asyncio.sleep(0.01)
                    
                    path = Path(file_path)
                    if not path.exists():
                        return {
                            "file": file_path,
                            "success": False,
                            "error": "file_not_found"
                        }
                    
                    # Calculate MD5 checksum
                    hash_md5 = hashlib.md5()
                    with open(path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    
                    return {
                        "file": file_path,
                        "success": True,
                        "md5": hash_md5.hexdigest(),
                        "size": path.stat().st_size
                    }
                except Exception as e:
                    return {
                        "file": file_path,
                        "success": False,
                        "error": str(e)
                    }
            
            # Calculate checksums concurrently
            results = await asyncio.gather(
                *[checksum_file(path) for path in file_paths],
                return_exceptions=True
            )
            
            successful = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed = [r for r in results if isinstance(r, dict) and not r.get("success")]
            
            return {
                "total_files": len(file_paths),
                "successful": len(successful),
                "failed": len(failed),
                "checksums": results,
                "calculation_method": "async_concurrent"
            }
        except Exception as e:
            return {"error": str(e)}


# Expose the custom processor
async_file_processor = AsyncFileProcessor()
app.expose(async_file_processor, name="async_file_processor", custom=True)


if __name__ == "__main__":
    print("🚀 Async File Processor loaded!")
    print("This version demonstrates async file I/O and concurrent processing.")
    print("All operations support both sync and async execution contexts.")
    app.run()