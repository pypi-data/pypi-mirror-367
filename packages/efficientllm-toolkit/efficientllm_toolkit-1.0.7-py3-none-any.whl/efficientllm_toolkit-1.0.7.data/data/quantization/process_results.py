#!/usr/bin/env python3
"""
Results processing and LaTeX table generation for inference benchmark performance.
"""

import os
import json
import pandas as pd
import argparse
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BenchmarkResultsProcessor:
    """Process benchmark results and generate LaTeX tables."""
    
    def __init__(self, results_dir: str):
        self.results_dir = results_dir
        self.task_configs = {
            "MMLU-Pro": "leaderboard_mmlu_pro",
            "BBH": "leaderboard_bbh", 
            "GPQA": "leaderboard_gpqa",
            "IFEval": "leaderboard_ifeval",
            "MATH": "leaderboard_math_hard",
            "MUSR": "leaderboard_musr"
        }
        
        # Model display order (as in the paper table)
        self.model_order = [
            "DeepSeek-R1-Distill-Qwen-1.5B",
            "DeepSeek-R1-Distill-Llama-8B", 
            "DeepSeek-R1-Distill-Qwen-14B",
            "Qwen2.5-7B",
            "Qwen2.5-14B",
            "Qwen2.5-32B",
            "Phi-4",
            "Phi-3.5-mini",
            "Yi-34B"
        ]
        
        # Models that should have blue highlighting (as in paper)
        self.highlighted_models = {
            "DeepSeek-R1-Distill-Qwen-1.5B",
            "DeepSeek-R1-Distill-Qwen-14B", 
            "Qwen2.5-14B",
            "Phi-4",
            "Yi-34B"
        }
    
    def extract_task_score(self, result_file: str, task_name: str) -> Optional[float]:
        """Extract score for a specific task from result file."""
        try:
            if not os.path.exists(result_file):
                return None
                
            with open(result_file, 'r') as f:
                data = json.load(f)
            
            results = data.get('results', {})
            
            if task_name == "MMLU-Pro":
                # Look for mmlu_pro accuracy
                for key in results:
                    if 'mmlu_pro' in key.lower():
                        return results[key].get('acc,none', results[key].get('acc'))
            
            elif task_name == "BBH":
                # Average across all BBH subtasks
                bbh_scores = []
                for key, value in results.items():
                    if 'bbh' in key.lower() and isinstance(value, dict):
                        score = value.get('exact_match,none', value.get('exact_match'))
                        if score is not None:
                            bbh_scores.append(score)
                return sum(bbh_scores) / len(bbh_scores) if bbh_scores else None
            
            elif task_name == "GPQA":
                # Average across GPQA variants
                gpqa_scores = []
                for key, value in results.items():
                    if 'gpqa' in key.lower() and isinstance(value, dict):
                        score = value.get('acc,none', value.get('acc'))
                        if score is not None:
                            gpqa_scores.append(score)
                return sum(gpqa_scores) / len(gpqa_scores) if gpqa_scores else None
            
            elif task_name == "IFEval":
                # Look for ifeval strict accuracy
                for key in results:
                    if 'ifeval' in key.lower():
                        result = results[key]
                        return result.get('strict_accuracy,none', 
                                        result.get('prompt_level_strict_accuracy'))
            
            elif task_name == "MATH":
                # Average across MATH subtasks
                math_scores = []
                for key, value in results.items():
                    if 'math' in key.lower() and isinstance(value, dict):
                        score = value.get('exact_match,none', value.get('exact_match'))
                        if score is not None:
                            math_scores.append(score)
                return sum(math_scores) / len(math_scores) if math_scores else None
            
            elif task_name == "MUSR":
                # Average across MUSR subtasks
                musr_scores = []
                for key, value in results.items():
                    if 'musr' in key.lower() and isinstance(value, dict):
                        score = value.get('exact_match,none', value.get('exact_match'))
                        if score is not None:
                            musr_scores.append(score)
                return sum(musr_scores) / len(musr_scores) if musr_scores else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting results from {result_file}: {e}")
            return None
    
    def collect_all_results(self) -> pd.DataFrame:
        """Collect all evaluation results into a DataFrame."""
        results_data = []
        
        for model_name in self.model_order:
            for precision in ["bfloat16", "float16", "int4"]:
                row_data = {"Model": model_name, "Precision": precision}
                
                for task_name in self.task_configs.keys():
                    result_file = os.path.join(
                        self.results_dir, 
                        f"{model_name}_{precision}_{task_name}.json"
                    )
                    score = self.extract_task_score(result_file, task_name)
                    row_data[task_name] = score
                
                results_data.append(row_data)
        
        return pd.DataFrame(results_data)
    
    def format_score(self, score: Optional[float]) -> str:
        """Format score for display."""
        if score is None:
            return "N/A"
        return f"{score:.4f}"
    
    def generate_latex_table(self, df: pd.DataFrame, output_file: str = None) -> str:
        """Generate LaTeX table matching the paper format."""
        
        latex_lines = []
        
        # Table header
        latex_lines.extend([
            "\\begin{table}[htbp]",
            "\\centering",
            "\\small",
            "\\renewcommand{\\arraystretch}{1.3}",
            "\\setlength{\\tabcolsep}{3pt}",
            "\\caption{Evaluation Results Across Precisions - Performance Metrics.} \\label{tab:inference-benchmark-performance}",
            "\\begin{tabular}{@{}lccccccc@{}}",
            "\\toprule",
            "Model & Precision & MMLU-Pro & BBH & GPQA & IFEval & MATH & MUSR \\\\",
            "\\midrule"
        ])
        
        # Table rows
        current_model = None
        for _, row in df.iterrows():
            model = row['Model']
            precision = row['Precision']
            
            # Add row coloring for highlighted models
            row_prefix = ""
            if model in self.highlighted_models:
                row_prefix = "\\rowcolor{blue!5}\n"
            
            # Model name display (only show for first precision of each model)
            if model != current_model:
                model_display = model
                current_model = model
            else:
                model_display = ""
            
            # Format scores
            scores = [
                self.format_score(row['MMLU-Pro']),
                self.format_score(row['BBH']),
                self.format_score(row['GPQA']),
                self.format_score(row['IFEval']),
                self.format_score(row['MATH']),
                self.format_score(row['MUSR'])
            ]
            
            # Build table row
            row_content = f"{model_display} & {precision} & {' & '.join(scores)} \\\\"
            latex_lines.append(row_prefix + row_content)
        
        # Table footer
        latex_lines.extend([
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}"
        ])
        
        latex_table = "\n".join(latex_lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(latex_table)
            logger.info(f"LaTeX table saved to: {output_file}")
        
        return latex_table
    
    def generate_csv_table(self, df: pd.DataFrame, output_file: str = None) -> pd.DataFrame:
        """Generate CSV table for easier viewing."""
        
        # Reorder columns to match paper
        column_order = ['Model', 'Precision', 'MMLU-Pro', 'BBH', 'GPQA', 'IFEval', 'MATH', 'MUSR']
        df_ordered = df[column_order].copy()
        
        # Format scores in DataFrame
        for col in ['MMLU-Pro', 'BBH', 'GPQA', 'IFEval', 'MATH', 'MUSR']:
            df_ordered[col] = df_ordered[col].apply(
                lambda x: f"{x:.4f}" if pd.notna(x) and x is not None else "N/A"
            )
        
        if output_file:
            df_ordered.to_csv(output_file, index=False)
            logger.info(f"CSV table saved to: {output_file}")
        
        return df_ordered
    
    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """Generate a summary report."""
        report_lines = []
        
        report_lines.append("INFERENCE BENCHMARK PERFORMANCE SUMMARY")
        report_lines.append("=" * 50)
        report_lines.append("")
        
        # Count completed evaluations
        total_evaluations = 0
        completed_evaluations = 0
        
        for _, row in df.iterrows():
            for task in ['MMLU-Pro', 'BBH', 'GPQA', 'IFEval', 'MATH', 'MUSR']:
                total_evaluations += 1
                if pd.notna(row[task]) and row[task] is not None:
                    completed_evaluations += 1
        
        report_lines.append(f"Evaluation Coverage: {completed_evaluations}/{total_evaluations} ({completed_evaluations/total_evaluations*100:.1f}%)")
        report_lines.append("")
        
        # Best performing models per task
        report_lines.append("BEST PERFORMING MODELS PER TASK:")
        report_lines.append("-" * 35)
        
        for task in ['MMLU-Pro', 'BBH', 'GPQA', 'IFEval', 'MATH', 'MUSR']:
            valid_scores = df[df[task].notna() & (df[task] != None)]
            if not valid_scores.empty:
                best_idx = valid_scores[task].idxmax()
                best_row = df.loc[best_idx]
                score = best_row[task]
                report_lines.append(f"{task}: {best_row['Model']} ({best_row['Precision']}) - {score:.4f}")
            else:
                report_lines.append(f"{task}: No valid results")
        
        report_lines.append("")
        
        # Precision comparison
        report_lines.append("AVERAGE PERFORMANCE BY PRECISION:")
        report_lines.append("-" * 35)
        
        for precision in ['bfloat16', 'float16', 'int4']:
            precision_df = df[df['Precision'] == precision]
            precision_scores = []
            
            for task in ['MMLU-Pro', 'BBH', 'GPQA', 'IFEval', 'MATH', 'MUSR']:
                valid_scores = precision_df[precision_df[task].notna() & (precision_df[task] != None)][task]
                if not valid_scores.empty:
                    precision_scores.extend(valid_scores.tolist())
            
            if precision_scores:
                avg_score = sum(precision_scores) / len(precision_scores)
                report_lines.append(f"{precision}: {avg_score:.4f} (n={len(precision_scores)})")
            else:
                report_lines.append(f"{precision}: No valid results")
        
        return "\n".join(report_lines)

def main():
    parser = argparse.ArgumentParser(description="Process benchmark results and generate tables")
    parser.add_argument("--results_dir", default="./results", help="Directory containing result files")
    parser.add_argument("--output_dir", default="./tables", help="Output directory for generated tables")
    parser.add_argument("--latex_file", help="Output LaTeX table file")
    parser.add_argument("--csv_file", help="Output CSV table file") 
    parser.add_argument("--report_file", help="Output summary report file")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize processor
    processor = BenchmarkResultsProcessor(args.results_dir)
    
    # Collect results
    logger.info("Collecting benchmark results...")
    df = processor.collect_all_results()
    
    # Generate outputs
    latex_file = args.latex_file or os.path.join(args.output_dir, "benchmark_table.tex")
    csv_file = args.csv_file or os.path.join(args.output_dir, "benchmark_results.csv")
    report_file = args.report_file or os.path.join(args.output_dir, "benchmark_report.txt")
    
    # Generate LaTeX table
    logger.info("Generating LaTeX table...")
    latex_table = processor.generate_latex_table(df, latex_file)
    
    # Generate CSV table
    logger.info("Generating CSV table...")
    csv_df = processor.generate_csv_table(df, csv_file)
    
    # Generate summary report
    logger.info("Generating summary report...")
    report = processor.generate_summary_report(df)
    with open(report_file, 'w') as f:
        f.write(report)
    logger.info(f"Summary report saved to: {report_file}")
    
    # Display results
    print("\nBenchmark Results Preview:")
    print("=" * 80)
    print(csv_df.head(10).to_string(index=False))
    
    print(f"\nFiles generated:")
    print(f"  LaTeX table: {latex_file}")
    print(f"  CSV results: {csv_file}")
    print(f"  Summary report: {report_file}")

if __name__ == "__main__":
    main()