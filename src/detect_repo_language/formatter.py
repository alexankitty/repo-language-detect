from typing import Dict, Tuple
from . import LANGUAGE_GLYPHS, analyze

def print_results(stats: Dict[str, Tuple[int, ...]], with_glyph: bool = False, show_mode: str = 'raw') -> None:
    """Print the analysis results.
    
    Args:
        stats: Language statistics dictionary
        with_glyph: Whether to include language glyphs
        show_mode: Display mode - 'raw' (default), 'weighted', or 'both'
    """
    if not stats:
        print("No recognized source files found.")
        return
    
    # Keep original unweighted stats for comparison
    unweighted_stats = stats.copy()
    
    # Apply weights to stats
    weighted_stats = analyze.apply_weights_to_stats(stats)
    
    # Sort by weighted lines of code (descending)
    sorted_stats = sorted(weighted_stats.items(), key=lambda x: x[1][1], reverse=True)
    
    # Calculate totals
    total_files = 0
    total_weighted_lines = 0
    total_unweighted_lines = 0
    
    for language, (file_count, weighted_line_count) in sorted_stats:
        unweighted_line_count = unweighted_stats[language][1]
        total_files += file_count
        total_weighted_lines += weighted_line_count
        total_unweighted_lines += unweighted_line_count
    
    # Format output table
    # Use fixed column widths that work well for all terminals
    if show_mode == 'raw':
        # Show only raw values (default)
        # Formula: Language(18) + Files(8) + Lines#(12) + %(5) = 43 chars total
        num_col_width = 12
        table_width = 18 + 1 + 8 + 1 + num_col_width + 1 + 5  # Actual content width
        
        print("\n" + "=" * table_width)
        print("Repository Language Analysis")
        print("=" * table_width)
        
        # Print header
        print(f"{'Language':<18} {'Files':<8} {'Lines':>{num_col_width}} {'%':<5}")
        print("-" * table_width)
        
        for language, (file_count, weighted_line_count) in sorted_stats:
            unweighted_line_count = unweighted_stats[language][1]
            lang_display = format_language_output(language, with_glyph)
            
            # Calculate percentages
            raw_pct = (unweighted_line_count / total_unweighted_lines * 100) if total_unweighted_lines > 0 else 0
            
            print(f"{lang_display:<18} {file_count:<8} {unweighted_line_count:>{num_col_width},} {raw_pct:>4.1f}%")
        
        print("-" * table_width)
        
        # Calculate total percentages
        raw_total_pct = (total_unweighted_lines / total_unweighted_lines * 100) if total_unweighted_lines > 0 else 0
        
        print(f"{'TOTAL':<18} {total_files:<8} {total_unweighted_lines:>{num_col_width},} {raw_total_pct:>4.1f}%")
        print("=" * table_width)
    elif show_mode == 'weighted':
        # Show only weighted values
        # Formula: Language(18) + Files(8) + Lines#(12) + %(5) = 43 chars total
        num_col_width = 12
        table_width = 18 + 1 + 8 + 1 + num_col_width + 1 + 5  # Actual content width
        
        print("\n" + "=" * table_width)
        print("Repository Language Analysis")
        print("=" * table_width)
        
        # Print header
        print(f"{'Language':<18} {'Files':<8} {'Lines':>{num_col_width}} {'%':<5}")
        print("-" * table_width)
        
        for language, (file_count, weighted_line_count) in sorted_stats:
            lang_display = format_language_output(language, with_glyph)
            
            # Calculate percentages
            weighted_pct = (weighted_line_count / total_weighted_lines * 100) if total_weighted_lines > 0 else 0
            
            print(f"{lang_display:<18} {file_count:<8} {weighted_line_count:>{num_col_width},} {weighted_pct:>4.1f}%")
        
        print("-" * table_width)
        
        # Calculate total percentages
        weighted_total_pct = (total_weighted_lines / total_weighted_lines * 100) if total_weighted_lines > 0 else 0
        
        print(f"{'TOTAL':<18} {total_files:<8} {total_weighted_lines:>{num_col_width},} {weighted_total_pct:>4.1f}%")
        print("=" * table_width)
    else:  # show_mode == 'both'
        # Show both raw and weighted values
        # Formula: Language(18) + Files(8) + Raw#(12) + Raw%(5) + Wt#(12) + Wt%(5) = 65 chars total
        num_col_width = 12
        table_width = 18 + 1 + 8 + 1 + num_col_width + 1 + 5 + 1 + num_col_width + 1 + 5  # Actual content width
        
        print("\n" + "=" * table_width)
        print("Repository Language Analysis")
        print("=" * table_width)
        
        # Print header
        print(f"{'Language':<18} {'Files':<8} {'Lines (Raw)':>{num_col_width}} {'%':<5} {'Lines (Wt)':>{num_col_width}} {'%':<5}")
        print("-" * table_width)
        
        for language, (file_count, weighted_line_count) in sorted_stats:
            unweighted_line_count = unweighted_stats[language][1]
            lang_display = format_language_output(language, with_glyph)
            
            # Calculate percentages
            raw_pct = (unweighted_line_count / total_unweighted_lines * 100) if total_unweighted_lines > 0 else 0
            weighted_pct = (weighted_line_count / total_weighted_lines * 100) if total_weighted_lines > 0 else 0
            
            print(f"{lang_display:<18} {file_count:<8} {unweighted_line_count:>{num_col_width},} {raw_pct:>4.1f}% {weighted_line_count:>{num_col_width},} {weighted_pct:>4.1f}%")
        
        print("-" * table_width)
        
        # Calculate total percentages (should be 100%)
        raw_total_pct = (total_unweighted_lines / total_unweighted_lines * 100) if total_unweighted_lines > 0 else 0
        weighted_total_pct = (total_weighted_lines / total_weighted_lines * 100) if total_weighted_lines > 0 else 0
        
        print(f"{'TOTAL':<18} {total_files:<8} {total_unweighted_lines:>{num_col_width},} {raw_total_pct:>4.1f}% {total_weighted_lines:>{num_col_width},} {weighted_total_pct:>4.1f}%")
        print("=" * table_width)
    
    primary_language = sorted_stats[0][0]
    primary_weighted_lines = sorted_stats[0][1][1]
    primary_unweighted_lines = unweighted_stats[primary_language][1]
    weighted_pct = (primary_weighted_lines / total_weighted_lines * 100) if total_weighted_lines > 0 else 0
    unweighted_pct = (primary_unweighted_lines / total_unweighted_lines * 100) if total_unweighted_lines > 0 else 0
    
    primary_display = format_language_output(primary_language, with_glyph)
    print(f"\n✓ Primary Language: {primary_display}")
    
    # Show both values in summary if weighted differs from unweighted
    if primary_weighted_lines != primary_unweighted_lines:
        print(f"  ({primary_unweighted_lines:,} raw {unweighted_pct:.1f}% → {primary_weighted_lines:,} weighted {weighted_pct:.1f}% of total)")
    else:
        print(f"  ({primary_weighted_lines:,} lines {weighted_pct:.1f}% of total)")
    print()

def format_language_output(language: str, with_glyph: bool = False) -> str:
    """Format language name with optional glyph."""
    if not with_glyph:
        return language
    glyph = LANGUAGE_GLYPHS.get(language, '')
    if glyph:
        return f"{glyph} {language}"
    return language