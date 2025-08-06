#!/usr/bin/env python3
"""
Batch evaluation script for inference benchmark performance.
Supports evaluating multiple models with different precision configurations.
"""

import os
import json
import subprocess
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model configurations for the paper benchmark - Using HuggingFace model IDs
MODEL_CONFIGS = {
    "DeepSeek-R1-Distill-Qwen-1.5B": {
        "model_path": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"}, 
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "DeepSeek-R1-Distill-Llama-8B": {
        "model_path": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "DeepSeek-R1-Distill-Qwen-14B": {
        "model_path": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B", 
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "Qwen2.5-7B": {
        "model_path": "Qwen/Qwen2.5-7B",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "Qwen2.5-14B": {
        "model_path": "Qwen/Qwen2.5-14B",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "Qwen2.5-32B": {
        "model_path": "Qwen/Qwen2.5-32B",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "Phi-4": {
        "model_path": "microsoft/Phi-4",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "Phi-3.5-mini": {
        "model_path": "microsoft/Phi-3.5-mini-instruct",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    },
    "Yi-34B": {
        "model_path": "01-ai/Yi-34B",
        "precisions": {
            "bfloat16": {"quantization": None, "dtype": "bfloat16"},
            "float16": {"quantization": None, "dtype": "float16"},
            "int4": {"quantization": "awq", "dtype": "auto"}
        }
    }
}

# Task configurations based on leaderboard tasks
TASK_CONFIGS = {
    "MMLU-Pro": "leaderboard_mmlu_pro",
    "BBH": "leaderboard_bbh", 
    "GPQA": "leaderboard_gpqa",
    "IFEval": "leaderboard_ifeval",
    "MATH": "leaderboard_math_hard",
    "MUSR": "leaderboard_musr"
}

def build_eval_command(
    model_name: str, 
    model_path: str, 
    precision: str, 
    precision_config: Dict, 
    task_name: str, 
    task_code: str,
    device: str = "cuda:0",
    output_dir: str = "./results"
) -> List[str]:
    """Build the evaluation command for lm_eval."""
    
    # Build model_args
    model_args = [f"pretrained={model_path}"]
    
    if precision_config["quantization"]:
        model_args.append(f"quantization={precision_config['quantization']}")
    
    if precision_config["dtype"]:
        model_args.append(f"dtype={precision_config['dtype']}")
    
    model_args.append("gpu_memory_utilization=0.7")
    
    # Build output path
    output_path = os.path.join(output_dir, f"{model_name}_{precision}_{task_name}.json")
    
    # Build command
    cmd = [
        "python", "-m", "lm_eval",
        "--model", "vllm",
        "--model_args", ",".join(model_args),
        "--tasks", task_code,
        "--device", device,
        "--batch_size", "auto",
        "--output_path", output_path
    ]
    
    return cmd, output_path

def run_evaluation(
    model_name: str, 
    model_path: str, 
    precision: str, 
    precision_config: Dict, 
    task_name: str, 
    task_code: str,
    device: str = "cuda:0",
    output_dir: str = "./results"
) -> Tuple[bool, str, Optional[str]]:
    """Run a single evaluation."""
    
    cmd, output_path = build_eval_command(
        model_name, model_path, precision, precision_config, 
        task_name, task_code, device, output_dir
    )
    
    logger.info(f"Running evaluation: {model_name} - {precision} - {task_name}")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        # Run evaluation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✓ Completed: {model_name} - {precision} - {task_name}")
            return True, output_path, None
        else:
            error_msg = f"Command failed with return code {result.returncode}\nStderr: {result.stderr}"
            logger.error(f"✗ Failed: {model_name} - {precision} - {task_name}: {error_msg}")
            return False, output_path, error_msg
            
    except subprocess.TimeoutExpired:
        error_msg = "Evaluation timed out after 1 hour"
        logger.error(f"✗ Timeout: {model_name} - {precision} - {task_name}")
        return False, output_path, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"✗ Error: {model_name} - {precision} - {task_name}: {error_msg}")
        return False, output_path, error_msg

def extract_results_from_file(result_file: str, task_name: str) -> Optional[float]:
    """Extract evaluation results from output JSON file."""
    try:
        if not os.path.exists(result_file):
            return None
            
        with open(result_file, 'r') as f:
            data = json.load(f)
        
        # Extract results based on task type
        results = data.get('results', {})
        
        # Try to find the main metric for each task
        if task_name == "MMLU-Pro":
            # Look for accuracy metric in mmlu_pro results
            for key in results:
                if 'mmlu_pro' in key.lower():
                    task_results = results[key]
                    return task_results.get('acc,none', task_results.get('acc', None))
        
        elif task_name == "BBH":
            # BBH uses exact_match metric, average across all subtasks
            bbh_scores = []
            for key, value in results.items():
                if 'bbh' in key.lower():
                    score = value.get('exact_match,none', value.get('exact_match', None))
                    if score is not None:
                        bbh_scores.append(score)
            return sum(bbh_scores) / len(bbh_scores) if bbh_scores else None
        
        elif task_name == "GPQA":
            # GPQA uses accuracy metric, average across variants
            gpqa_scores = []
            for key, value in results.items():
                if 'gpqa' in key.lower():
                    score = value.get('acc,none', value.get('acc', None))
                    if score is not None:
                        gpqa_scores.append(score)
            return sum(gpqa_scores) / len(gpqa_scores) if gpqa_scores else None
        
        elif task_name == "IFEval":
            # IFEval uses strict accuracy
            for key in results:
                if 'ifeval' in key.lower():
                    task_results = results[key]
                    return task_results.get('strict_accuracy,none', task_results.get('prompt_level_strict_accuracy', None))
        
        elif task_name == "MATH":
            # MATH uses exact_match, average across subtasks
            math_scores = []
            for key, value in results.items():
                if 'math' in key.lower():
                    score = value.get('exact_match,none', value.get('exact_match', None))
                    if score is not None:
                        math_scores.append(score)
            return sum(math_scores) / len(math_scores) if math_scores else None
        
        elif task_name == "MUSR":
            # MUSR uses exact_match, average across subtasks
            musr_scores = []
            for key, value in results.items():
                if 'musr' in key.lower():
                    score = value.get('exact_match,none', value.get('exact_match', None))
                    if score is not None:
                        musr_scores.append(score)
            return sum(musr_scores) / len(musr_scores) if musr_scores else None
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting results from {result_file}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Batch evaluation for inference benchmark")
    parser.add_argument("--models", nargs="+", help="Models to evaluate (default: all)")
    parser.add_argument("--precisions", nargs="+", default=["bfloat16", "float16", "int4"], 
                       help="Precisions to evaluate")
    parser.add_argument("--tasks", nargs="+", help="Tasks to evaluate (default: all)")
    parser.add_argument("--device", default="cuda:0", help="Device to use")
    parser.add_argument("--output_dir", default="./results", help="Output directory")
    parser.add_argument("--max_workers", type=int, default=1, help="Max parallel workers")
    parser.add_argument("--resume", action="store_true", help="Resume from existing results")
    
    args = parser.parse_args()
    
    # Set default models and tasks if not specified
    models_to_eval = args.models if args.models else list(MODEL_CONFIGS.keys())
    tasks_to_eval = args.tasks if args.tasks else list(TASK_CONFIGS.keys())
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Prepare evaluation jobs
    jobs = []
    for model_name in models_to_eval:
        if model_name not in MODEL_CONFIGS:
            logger.warning(f"Unknown model: {model_name}, skipping")
            continue
            
        model_config = MODEL_CONFIGS[model_name]
        for precision in args.precisions:
            if precision not in model_config["precisions"]:
                logger.warning(f"Precision {precision} not supported for {model_name}, skipping")
                continue
                
            precision_config = model_config["precisions"][precision]
            for task_name in tasks_to_eval:
                if task_name not in TASK_CONFIGS:
                    logger.warning(f"Unknown task: {task_name}, skipping")
                    continue
                    
                task_code = TASK_CONFIGS[task_name]
                
                # Check if we should skip this job (resume mode)
                if args.resume:
                    expected_output = os.path.join(
                        args.output_dir, 
                        f"{model_name}_{precision}_{task_name}.json"
                    )
                    if os.path.exists(expected_output):
                        logger.info(f"Skipping existing result: {model_name} - {precision} - {task_name}")
                        continue
                
                jobs.append((
                    model_name, model_config["model_path"], 
                    precision, precision_config, 
                    task_name, task_code
                ))
    
    logger.info(f"Total evaluation jobs: {len(jobs)}")
    
    # Run evaluations
    failed_jobs = []
    
    if args.max_workers == 1:
        # Sequential execution
        for job in jobs:
            success, output_path, error = run_evaluation(
                *job, device=args.device, output_dir=args.output_dir
            )
            if not success:
                failed_jobs.append((job, error))
    else:
        # Parallel execution
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            future_to_job = {
                executor.submit(
                    run_evaluation, *job, 
                    device=args.device, output_dir=args.output_dir
                ): job for job in jobs
            }
            
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    success, output_path, error = future.result()
                    if not success:
                        failed_jobs.append((job, error))
                except Exception as exc:
                    logger.error(f"Job {job} generated an exception: {exc}")
                    failed_jobs.append((job, str(exc)))
    
    # Report results
    successful_jobs = len(jobs) - len(failed_jobs)
    logger.info(f"Evaluation completed: {successful_jobs}/{len(jobs)} successful")
    
    if failed_jobs:
        logger.error("Failed jobs:")
        for job, error in failed_jobs:
            model_name, _, precision, _, task_name, _ = job
            logger.error(f"  {model_name} - {precision} - {task_name}: {error}")
    
    # Generate summary table
    generate_results_table(args.output_dir, models_to_eval, args.precisions, tasks_to_eval)

def generate_results_table(output_dir: str, models: List[str], precisions: List[str], tasks: List[str]):
    """Generate results table similar to the paper."""
    logger.info("Generating results table...")
    
    # Collect all results
    results_data = []
    
    for model_name in models:
        if model_name not in MODEL_CONFIGS:
            continue
            
        for precision in precisions:
            if precision not in MODEL_CONFIGS[model_name]["precisions"]:
                continue
                
            row_data = {"Model": model_name, "Precision": precision}
            
            for task_name in tasks:
                result_file = os.path.join(output_dir, f"{model_name}_{precision}_{task_name}.json")
                score = extract_results_from_file(result_file, task_name)
                row_data[task_name] = score if score is not None else "N/A"
            
            results_data.append(row_data)
    
    # Create DataFrame
    df = pd.DataFrame(results_data)
    
    # Save to CSV
    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    df.to_csv(csv_path, index=False)
    logger.info(f"Results saved to: {csv_path}")
    
    # Display table
    print("\nBenchmark Results:")
    print("=" * 80)
    print(df.to_string(index=False))
    
    return df

if __name__ == "__main__":
    main()