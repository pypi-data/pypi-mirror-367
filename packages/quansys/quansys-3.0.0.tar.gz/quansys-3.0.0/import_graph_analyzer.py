#!/usr/bin/env python3
"""
Import Graph Analyzer for CLI Performance

Analyzes the actual import chain when loading quansys.cli.main
to identify remaining heavy dependencies.
"""

import sys
import time
from pathlib import Path

def trace_imports():
    """Trace all imports when loading quansys.cli.main"""
    import_times = {}
    import_order = []
    
    # Hook into the import system
    original_import = __builtins__.__import__
    
    def traced_import(name, globals=None, locals=None, fromlist=(), level=0):
        start_time = time.time()
        try:
            result = original_import(name, globals, locals, fromlist, level)
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Only track substantial imports (>1ms)
            if elapsed > 0.001:
                import_key = f"{name}" + (f" from {fromlist}" if fromlist else "")
                import_times[import_key] = elapsed
                import_order.append((import_key, elapsed))
                
            return result
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            import_key = f"{name} (FAILED: {e})"
            import_times[import_key] = elapsed
            import_order.append((import_key, elapsed))
            raise
    
    # Install the hook
    __builtins__.__import__ = traced_import
    
    try:
        # Add the source directory to path
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
            
        # Import the CLI main module and measure
        print("Tracing imports for quansys.cli.main...")
        start_total = time.time()
        
        # This will trigger all the imports we want to analyze
        
        end_total = time.time()
        total_time = end_total - start_total
        
        return import_times, import_order, total_time
        
    finally:
        # Restore original import
        __builtins__.__import__ = original_import

def analyze_import_chain():
    """Analyze what's being imported and when"""
    try:
        import_times, import_order, total_time = trace_imports()
        
        print("\n📊 IMPORT ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Total import time: {total_time:.4f}s")
        print(f"Tracked imports: {len(import_times)}")
        
        # Sort by time taken
        sorted_imports = sorted(import_times.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n🐌 SLOWEST IMPORTS (>{1}ms):")
        print("-" * 40)
        cumulative_time = 0
        for name, elapsed in sorted_imports:
            if elapsed > 0.001:  # Only show >1ms
                cumulative_time += elapsed
                percentage = (elapsed / total_time) * 100
                print(f"{elapsed:>7.4f}s ({percentage:>5.1f}%) - {name}")
        
        print("\n📈 CUMULATIVE ANALYSIS:")
        print("-" * 30)
        print(f"Top 5 imports account for: {(sum(t for _, t in sorted_imports[:5]) / total_time * 100):.1f}% of time")
        print(f"Tracked imports account for: {(cumulative_time / total_time * 100):.1f}% of total time")
        
        print("\n⏰ IMPORT ORDER (first 10):")
        print("-" * 35)
        for i, (name, elapsed) in enumerate(import_order[:10]):
            print(f"{i+1:>2}. {elapsed:.4f}s - {name}")
        
        # Save detailed results
        with open("import_graph_analysis.txt", "w") as f:
            f.write("Import Graph Analysis\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total time: {total_time:.4f}s\n\n")
            
            f.write("All imports by time:\n")
            for name, elapsed in sorted_imports:
                f.write(f"{elapsed:.6f}s - {name}\n")
                
            f.write("\nImport order:\n")
            for i, (name, elapsed) in enumerate(import_order):
                f.write(f"{i+1}. {elapsed:.6f}s - {name}\n")
        
        print("\n💾 Detailed analysis saved to: import_graph_analysis.txt")
        
        return sorted_imports[:10]  # Return top 10 slowest
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return []

def recommend_optimizations(slow_imports):
    """Generate specific optimization recommendations"""
    print("\n🚀 OPTIMIZATION RECOMMENDATIONS:")
    print("-" * 40)
    
    recommendations = []
    
    for name, elapsed in slow_imports:
        if 'typer' in name.lower():
            recommendations.append(f"• Typer taking {elapsed:.4f}s - consider CLI framework alternatives")
        elif 'quansys' in name.lower():
            recommendations.append(f"• {name} taking {elapsed:.4f}s - move to lazy loading")
        elif any(heavy in name.lower() for heavy in ['pandas', 'numpy', 'matplotlib', 'scipy']):
            recommendations.append(f"• Heavy scientific library {name} taking {elapsed:.4f}s - defer import")
        elif 'pydantic' in name.lower():
            recommendations.append(f"• Pydantic {name} taking {elapsed:.4f}s - consider simpler validation")
        else:
            recommendations.append(f"• {name} taking {elapsed:.4f}s - investigate necessity")
    
    if not recommendations:
        recommendations.append("• No major slow imports detected - investigate other bottlenecks")
    
    for rec in recommendations:
        print(rec)
    
    print("\n💡 ARCHITECTURAL SUGGESTIONS:")
    print("• Implement full lazy loading pattern like the example")
    print("• Move command functions to separate modules")
    print("• Use importlib.import_module() for dynamic loading")
    print("• Consider CLI entry point that doesn't import any app logic")

def main():
    print("🔍 CLI Import Graph Analysis")
    print("This will trace all imports when loading quansys.cli.main")
    print("=" * 60)
    
    slow_imports = analyze_import_chain()
    recommend_optimizations(slow_imports)

if __name__ == "__main__":
    main()