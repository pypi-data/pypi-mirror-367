#!/usr/bin/env python3
"""
Example demonstration script for the inference benchmark evaluation.
Creates sample results to show how the table generation works.
"""

import os
import json
import random
from pathlib import Path

def create_sample_results():
    """Create sample result files to demonstrate the table generation."""
    
    # Create results directory
    results_dir = "./sample_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Sample data based on the paper table (approximate values)
    sample_data = {
        "DeepSeek-R1-Distill-Qwen-1.5B": {
            "bfloat16": {"MMLU-Pro": 0.1656, "BBH": 0.3471, "GPQA": 0.269, "IFEval": 0.1955, "MATH": 0.1192, "MUSR": 0.3553},
            "float16": {"MMLU-Pro": 0.1668, "BBH": 0.3505, "GPQA": 0.2754, "IFEval": 0.1995, "MATH": 0.1213, "MUSR": 0.3567},
            "int4": {"MMLU-Pro": 0.1496, "BBH": 0.3337, "GPQA": 0.2529, "IFEval": 0.1937, "MATH": 0.1043, "MUSR": 0.3702}
        },
        "Qwen2.5-7B": {
            "bfloat16": {"MMLU-Pro": 0.4468, "BBH": 0.5555, "GPQA": 0.3281, "IFEval": 0.6619, "MATH": 0.2499, "MUSR": 0.4264},
            "float16": {"MMLU-Pro": 0.4461, "BBH": 0.5545, "GPQA": 0.3307, "IFEval": 0.6626, "MATH": 0.2574, "MUSR": 0.4290},
            "int4": {"MMLU-Pro": 0.4187, "BBH": 0.5451, "GPQA": 0.3413, "IFEval": 0.6134, "MATH": 0.1501, "MUSR": 0.4227}
        },
        "Phi-4": {
            "bfloat16": {"MMLU-Pro": 0.5284, "BBH": 0.6705, "GPQA": 0.4081, "IFEval": 0.0549, "MATH": 0.2554, "MUSR": 0.5034},
            "float16": {"MMLU-Pro": 0.5295, "BBH": 0.6710, "GPQA": 0.4009, "IFEval": 0.0503, "MATH": 0.2497, "MUSR": 0.5021},
            "int4": {"MMLU-Pro": 0.5276, "BBH": 0.6679, "GPQA": 0.3953, "IFEval": 0.0651, "MATH": 0.2385, "MUSR": 0.4756}
        }
    }
    
    # Task mapping
    task_mapping = {
        "MMLU-Pro": "leaderboard_mmlu_pro",
        "BBH": "leaderboard_bbh", 
        "GPQA": "leaderboard_gpqa",
        "IFEval": "leaderboard_ifeval",
        "MATH": "leaderboard_math_hard",
        "MUSR": "leaderboard_musr"
    }
    
    # Generate sample result files
    for model_name, model_data in sample_data.items():
        for precision, precision_data in model_data.items():
            for task_name, score in precision_data.items():
                # Create realistic result structure
                result_data = {
                    "results": {},
                    "versions": {},
                    "n-shot": {},
                    "config": {
                        "model": "vllm",
                        "model_args": f"pretrained=./model/{model_name},dtype={precision}",
                        "tasks": [task_mapping[task_name]],
                        "num_fewshot": None,
                        "batch_size": "auto",
                        "device": "cuda:0"
                    }
                }
                
                # Add task-specific result format
                task_key = task_mapping[task_name]
                
                if task_name == "MMLU-Pro":
                    result_data["results"][task_key] = {
                        "acc,none": score,
                        "acc_stderr,none": score * 0.05  # Mock stderr
                    }
                elif task_name in ["BBH", "MATH", "MUSR"]:
                    result_data["results"][task_key] = {
                        "exact_match,none": score,
                        "exact_match_stderr,none": score * 0.05
                    }
                elif task_name in ["GPQA"]:
                    result_data["results"][task_key] = {
                        "acc,none": score,
                        "acc_stderr,none": score * 0.05
                    }
                elif task_name == "IFEval":
                    result_data["results"][task_key] = {
                        "strict_accuracy,none": score,
                        "strict_accuracy_stderr,none": score * 0.05
                    }
                
                # Save result file
                filename = f"{model_name}_{precision}_{task_name}.json"
                filepath = os.path.join(results_dir, filename)
                
                with open(filepath, 'w') as f:
                    json.dump(result_data, f, indent=2)
    
    print(f"Sample results created in: {results_dir}")
    print(f"Generated {len(os.listdir(results_dir))} result files")
    
    return results_dir

def main():
    """Main demonstration function."""
    print("Creating sample benchmark results...")
    results_dir = create_sample_results()
    
    print("\nNow you can run the results processor:")
    print(f"python process_results.py --results_dir {results_dir} --output_dir ./sample_tables")
    
    # Also demonstrate the batch evaluation command structure
    print("\nTo run actual evaluations, use:")
    print("python batch_eval.py --models DeepSeek-R1-Distill-Qwen-1.5B Qwen2.5-7B --precisions bfloat16 float16 --tasks MMLU-Pro BBH")
    print("\nFull evaluation command:")
    print("python batch_eval.py --output_dir ./results --max_workers 1 --resume")

if __name__ == "__main__":
    main()