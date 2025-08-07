#!/usr/bin/env python3
"""
CLI Performance Benchmarking Script

This script measures the responsiveness of the quansys CLI commands
to identify performance bottlenecks and track improvements.
"""

import time
import subprocess
from pathlib import Path
from typing import Dict, List
import statistics

def measure_import_times() -> Dict[str, float]:
    """Measure import times for key modules."""
    import_tests = {
        "typer": "import typer",
        "quansys.cli.main": "from quansys.cli.main import app",
        "quansys.workflow": "from quansys.workflow import WorkflowConfig, execute_workflow",
        "ansys.aedt.core": "from ansys.aedt.core import Hfss",
        "quansys.simulation": "from quansys.simulation import EigenmodeAnalysis, QuantumEPR",
    }
    
    results = {}
    for name, import_stmt in import_tests.items():
        try:
            start_time = time.time()
            exec(import_stmt)
            end_time = time.time()
            results[name] = end_time - start_time
        except ImportError as e:
            results[name] = f"ImportError: {e}"
        except Exception as e:
            results[name] = f"Error: {e}"
    
    return results

def measure_cli_startup_time(command: List[str], runs: int = 5) -> Dict[str, float]:
    """Measure CLI startup time for a given command."""
    times = []
    
    for _ in range(runs):
        start_time = time.time()
        try:
            _ = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            end_time = time.time()
            elapsed = end_time - start_time
            times.append(elapsed)
        except subprocess.TimeoutExpired:
            times.append(30.0)  # Max timeout
        except Exception as e:
            print(f"Error running {' '.join(command)}: {e}")
            return {"error": str(e)}
    
    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times), 
        "min": min(times),
        "max": max(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        "times": times
    }

def benchmark_cli_commands() -> Dict[str, Dict[str, float]]:
    """Benchmark various CLI commands."""
    commands_to_test = [
        (["quansys", "--help"], "help_command"),
        (["quansys", "example", "--list"], "example_list"),
        (["python", "-c", "from quansys.cli.main import app; print('Import successful')"], "import_test"),
    ]
    
    results = {}
    for command, name in commands_to_test:
        print(f"Benchmarking: {name}")
        results[name] = measure_cli_startup_time(command)
    
    return results

def print_benchmark_results(import_results: Dict, cli_results: Dict):
    """Print formatted benchmark results."""
    print("\n" + "="*50)
    print("CLI PERFORMANCE BENCHMARK RESULTS")
    print("="*50)
    
    print("\nIMPORT TIMES:")
    print("-" * 30)
    for module, time_or_error in import_results.items():
        if isinstance(time_or_error, float):
            print(f"{module:25} : {time_or_error:.4f}s")
        else:
            print(f"{module:25} : {time_or_error}")
    
    print("\nCLI COMMAND TIMES:")
    print("-" * 30)
    for command, stats in cli_results.items():
        if "error" in stats:
            print(f"{command:25} : ERROR - {stats['error']}")
        else:
            print(f"{command:25} : {stats['mean']:.4f}s +/- {stats['std_dev']:.4f}s")
            print(f"{'':25}   (min: {stats['min']:.4f}s, max: {stats['max']:.4f}s)")
    
    print("\nANALYSIS:")
    print("-" * 30)
    
    # Find slowest imports
    import_times = {k: v for k, v in import_results.items() if isinstance(v, float)}
    if import_times:
        slowest_import = max(import_times.items(), key=lambda x: x[1])
        print(f"Slowest import: {slowest_import[0]} ({slowest_import[1]:.4f}s)")
    
    # Calculate total import time
    total_import_time = sum(t for t in import_times.values())
    print(f"Total measured import time: {total_import_time:.4f}s")
    
    # Find slowest CLI command
    cli_times = {k: v['mean'] for k, v in cli_results.items() if 'mean' in v}
    if cli_times:
        slowest_cli = max(cli_times.items(), key=lambda x: x[1])
        print(f"Slowest CLI command: {slowest_cli[0]} ({slowest_cli[1]:.4f}s)")

def main():
    """Run the CLI benchmark suite."""
    print("Starting CLI Performance Benchmark...")
    print("This may take a few moments...")
    
    # Measure import times
    print("\nMeasuring import times...")
    import_results = measure_import_times()
    
    # Measure CLI command times
    print("\nMeasuring CLI command times...")
    cli_results = benchmark_cli_commands()
    
    # Print results
    print_benchmark_results(import_results, cli_results)
    
    # Save results to file for comparison
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    results_file = Path(f"cli_benchmark_{timestamp}.txt")
    
    with open(results_file, "w") as f:
        f.write("CLI Performance Benchmark Results\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        
        f.write("Import Times:\n")
        for module, time_or_error in import_results.items():
            f.write(f"{module}: {time_or_error}\n")
        
        f.write("\nCLI Command Times:\n")
        for command, stats in cli_results.items():
            f.write(f"{command}: {stats}\n")
    
    print(f"\nResults saved to: {results_file}")
    print("\nBenchmark complete!")

if __name__ == "__main__":
    main()