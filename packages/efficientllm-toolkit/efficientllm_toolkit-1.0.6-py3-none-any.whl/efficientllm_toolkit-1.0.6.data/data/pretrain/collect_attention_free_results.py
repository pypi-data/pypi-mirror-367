#!/usr/bin/env python3
"""
Collect results from attention-free mechanism experiments and generate LaTeX table
"""

import os
import sys
import json
import glob
import argparse
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class AttentionFreeResultsCollector:
    """Collect and process results from attention-free experiments"""
    
    def __init__(self, results_dir: str):
        self.results_dir = results_dir
        self.models = ["Qwen2.5", "Mamba", "Pythia", "RWKV"]
        self.sizes = ["0.5B", "1.5B", "3B"]
        self.context_length = "8K"
        
        # Model name mapping
        self.model_mapping = {
            "qwen2.5": "Qwen2.5", 
            "mamba": "Mamba",
            "pythia": "Pythia",
            "rwkv": "RWKV"
        }
        
        # Models that should be highlighted (from the table)
        self.highlighted_models = {"Mamba", "RWKV"}
    
    def load_metrics_from_json(self, metrics_file: str) -> Optional[Dict]:
        """Load metrics from JSON file"""
        try:
            with open(metrics_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load {metrics_file}: {e}")
            return None
    
    def extract_ppl_from_log(self, log_file: str) -> Optional[float]:
        """Extract perplexity from training log file"""
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
            
            # Look for final loss and convert to perplexity
            final_loss = None
            for line in reversed(lines):
                if 'Loss =' in line:
                    try:
                        # Extract loss value
                        loss_part = line.split('Loss =')[1].split(',')[0].strip()
                        final_loss = float(loss_part)
                        break
                    except (IndexError, ValueError):
                        continue
            
            if final_loss is not None:
                # Convert loss to perplexity: PPL = exp(loss)
                return np.exp(final_loss)
                
        except FileNotFoundError:
            print(f"Warning: Log file not found: {log_file}")
        
        return None
    
    def collect_all_results(self) -> pd.DataFrame:
        """Collect results from all experiments"""
        results_data = []
        
        for model_key in ["qwen2.5", "mamba", "pythia", "rwkv"]:
            model_name = self.model_mapping[model_key]
            
            for size in self.sizes:
                result_dir = os.path.join(self.results_dir, f"{model_key}_{size}")
                
                # Initialize row data
                row_data = {
                    "Method": model_name,
                    "Parameters": size,
                    "Context Length": self.context_length,
                    "PPL": None,
                    "AMU (GB)": None,
                    "AL (s/iter)": None,
                    "TT (Tokens/param/s)": None,
                    "AEC (W)": None
                }
                
                # Try to load metrics from JSON file
                metrics_file = os.path.join(result_dir, "efficientllm_metrics.json")
                metrics_data = self.load_metrics_from_json(metrics_file)
                
                if metrics_data and 'metrics' in metrics_data:
                    metrics = metrics_data['metrics']
                    row_data["AMU (GB)"] = metrics.get('amu_gb')
                    row_data["AL (s/iter)"] = metrics.get('al_seconds')
                    row_data["TT (Tokens/param/s)"] = metrics.get('tt_tokens_per_param_per_sec')
                    row_data["AEC (W)"] = metrics.get('aec_watts')
                
                # Try to extract PPL from log file
                log_file = os.path.join(os.path.dirname(self.results_dir), "logs", f"{model_key}_{size}.log")
                ppl = self.extract_ppl_from_log(log_file)
                if ppl is not None:
                    row_data["PPL"] = ppl
                
                results_data.append(row_data)
        
        return pd.DataFrame(results_data)
    
    def generate_latex_table(self, df: pd.DataFrame, output_file: str = None) -> str:
        """Generate LaTeX table matching the paper format"""
        
        latex_lines = []
        
        # Table header
        latex_lines.extend([
            "\\begin{table}",
            "\\centering",
            "\\small",
            "\\renewcommand{\\arraystretch}{1.3}",
            "",
            "\\setlength{\\tabcolsep}{2pt}",
            "\\vspace{3pt}",
            "\\caption{Efficiency Results for Attention-Free Mechanisms. The best result is compared under the same parameters.}",
            "\\resizebox{\\linewidth}{!}{",
            "\\begin{tabular}{@{}lccccccccc@{}}",
            "\\toprule",
            "\\textbf{Method}&\\textbf{Parameters}  & \\textbf{Context Length}  & \\textbf{PPL $\\downarrow$} & \\textbf{AMU (GB) $\\downarrow$} & \\textbf{AL (s/iter) $\\downarrow$} & \\textbf{TT (Tokens/param/s) $\\uparrow$} & \\textbf{AEC (W)}$\\downarrow$ \\\\",
            "\\midrule",
            ""
        ])
        
        # Group by model and add rows
        current_model = None
        for _, row in df.iterrows():
            model = row['Method']
            
            # Add row coloring for highlighted models
            row_prefix = ""
            if model in self.highlighted_models:
                row_prefix = "\\rowcolor{blue!5} "
            
            # Model name (only show for first size of each model)
            if model != current_model:
                model_display = model
                current_model = model
            else:
                model_display = ""
            
            # Format values
            def format_value(val, format_type="float"):
                if val is None or pd.isna(val):
                    return "N/A"
                
                if format_type == "ppl":
                    return f"{val:.2f}"
                elif format_type == "float":
                    return f"{val:.2f}"
                elif format_type == "scientific":
                    return f"{val:.2e}".replace('e', '\\times10^{').replace('+0', '') + '}'
                elif format_type == "time":
                    return f"{val:.4f}"
                else:
                    return f"{val:.2f}"
            
            ppl_str = format_value(row['PPL'], "ppl")
            amu_str = format_value(row['AMU (GB)'], "float")
            al_str = format_value(row['AL (s/iter)'], "time")
            tt_str = format_value(row['TT (Tokens/param/s)'], "scientific")
            aec_str = format_value(row['AEC (W)'], "float")
            
            # Build table row
            row_content = f"{model_display} & {row['Parameters']} & {row['Context Length']} & {ppl_str} & {amu_str} & {al_str} & {tt_str} & {aec_str} \\\\"
            
            latex_lines.append(row_prefix + row_content)
        
        # Table footer
        latex_lines.extend([
            "",
            "\\bottomrule",
            "\\end{tabular}}",
            "\\label{tab:efficient-attention-mechanisms-AF}",
            "\\end{table}"
        ])
        
        latex_table = "\n".join(latex_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(latex_table)
            print(f"LaTeX table saved to: {output_file}")
        
        return latex_table
    
    def generate_csv_table(self, df: pd.DataFrame, output_file: str = None) -> pd.DataFrame:
        """Generate CSV table for easier viewing"""
        
        # Format the dataframe for display
        df_formatted = df.copy()
        
        # Format numeric columns
        for col in ['PPL', 'AMU (GB)', 'AL (s/iter)', 'AEC (W)']:
            df_formatted[col] = df_formatted[col].apply(
                lambda x: f"{x:.4f}" if pd.notna(x) and x is not None else "N/A"
            )
        
        # Format scientific notation column
        df_formatted['TT (Tokens/param/s)'] = df_formatted['TT (Tokens/param/s)'].apply(
            lambda x: f"{x:.2e}" if pd.notna(x) and x is not None else "N/A"
        )
        
        if output_file:
            df_formatted.to_csv(output_file, index=False)
            print(f"CSV table saved to: {output_file}")
        
        return df_formatted
    
    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """Generate summary report"""
        report_lines = []
        
        report_lines.append("ATTENTION-FREE MECHANISMS BENCHMARK SUMMARY")
        report_lines.append("=" * 50)
        report_lines.append("")
        
        # Count completed experiments
        total_experiments = len(df)
        completed_experiments = 0
        
        for _, row in df.iterrows():
            if pd.notna(row['PPL']) or pd.notna(row['AMU (GB)']):
                completed_experiments += 1
        
        report_lines.append(f"Experiments: {completed_experiments}/{total_experiments} completed")
        report_lines.append("")
        
        # Best performing models per metric
        report_lines.append("BEST PERFORMING MODELS PER METRIC:")
        report_lines.append("-" * 35)
        
        metrics = ['PPL', 'AMU (GB)', 'AL (s/iter)', 'AEC (W)']
        for metric in metrics:
            valid_data = df[df[metric].notna() & (df[metric] != None)]
            if not valid_data.empty:
                # For these metrics, lower is better
                best_idx = valid_data[metric].idxmin()
                best_row = df.loc[best_idx]
                report_lines.append(f"{metric}: {best_row['Method']} {best_row['Parameters']} - {best_row[metric]:.4f}")
        
        # For TT, higher is better
        tt_data = df[df['TT (Tokens/param/s)'].notna() & (df['TT (Tokens/param/s)'] != None)]
        if not tt_data.empty:
            best_idx = tt_data['TT (Tokens/param/s)'].idxmax()
            best_row = df.loc[best_idx]
            report_lines.append(f"TT (Tokens/param/s): {best_row['Method']} {best_row['Parameters']} - {best_row['TT (Tokens/param/s)']:.2e}")
        
        report_lines.append("")
        
        # Model comparison
        report_lines.append("AVERAGE PERFORMANCE BY MODEL:")
        report_lines.append("-" * 30)
        
        for model in self.models:
            model_data = df[df['Method'] == model]
            if not model_data.empty:
                # Calculate averages for available metrics
                avg_metrics = {}
                for metric in ['PPL', 'AMU (GB)', 'AL (s/iter)', 'TT (Tokens/param/s)', 'AEC (W)']:
                    valid_values = model_data[model_data[metric].notna() & (model_data[metric] != None)][metric]
                    if not valid_values.empty:
                        avg_metrics[metric] = valid_values.mean()
                
                report_lines.append(f"{model}:")
                for metric, value in avg_metrics.items():
                    if metric == 'TT (Tokens/param/s)':
                        report_lines.append(f"  {metric}: {value:.2e}")
                    else:
                        report_lines.append(f"  {metric}: {value:.4f}")
        
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="Collect attention-free mechanism experiment results")
    parser.add_argument("--results_dir", default="./experiments/attention_free_benchmark/results", 
                       help="Directory containing experiment results")
    parser.add_argument("--output_dir", default="./experiments/attention_free_benchmark/tables", 
                       help="Output directory for generated tables")
    parser.add_argument("--latex_file", help="Output LaTeX table file")
    parser.add_argument("--csv_file", help="Output CSV table file")
    parser.add_argument("--report_file", help="Output summary report file")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize collector
    collector = AttentionFreeResultsCollector(args.results_dir)
    
    # Collect results
    print("Collecting attention-free mechanism results...")
    df = collector.collect_all_results()
    
    if df.empty:
        print("No results found. Please run experiments first.")
        return
    
    # Generate outputs
    latex_file = args.latex_file or os.path.join(args.output_dir, "attention_free_table.tex")
    csv_file = args.csv_file or os.path.join(args.output_dir, "attention_free_results.csv")
    report_file = args.report_file or os.path.join(args.output_dir, "attention_free_report.txt")
    
    # Generate LaTeX table
    print("Generating LaTeX table...")
    latex_table = collector.generate_latex_table(df, latex_file)
    
    # Generate CSV table
    print("Generating CSV table...")
    csv_df = collector.generate_csv_table(df, csv_file)
    
    # Generate summary report
    print("Generating summary report...")
    report = collector.generate_summary_report(df)
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"Summary report saved to: {report_file}")
    
    # Display results preview
    print("\nResults Preview:")
    print("=" * 100)
    print(csv_df.to_string(index=False))
    
    print(f"\nFiles generated:")
    print(f"  LaTeX table: {latex_file}")
    print(f"  CSV results: {csv_file}")
    print(f"  Summary report: {report_file}")
    
    print("\nTo view the LaTeX table:")
    print(f"  cat {latex_file}")


if __name__ == "__main__":
    main()