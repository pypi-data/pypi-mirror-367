#!/usr/bin/env python3
"""
EfficientLLM CLI: Unified command line interface for all EfficientLLM experiments
"""

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

class EfficientLLMCLI:
    """Main CLI class for EfficientLLM"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.pretrain_dir = self.base_dir / "pretrain"
        self.quantization_dir = self.base_dir / "quantization"
        self.finetune_dir = self.base_dir / "fine-tune"
        
        # Model configurations aligned with paper
        self.model_configs = {
            "qwen2.5": {
                "0.5B": {"layers": 24, "hidden": 896, "heads": 14, "kv_heads": 2, "intermediate": 4864},
                "1.5B": {"layers": 28, "hidden": 1536, "heads": 12, "kv_heads": 2, "intermediate": 8960},
                "3B": {"layers": 36, "hidden": 2048, "heads": 16, "kv_heads": 2, "intermediate": 11008}
            },
            "mamba": {
                "0.5B": {"layers": 24, "d_model": 768},
                "1.5B": {"layers": 48, "d_model": 1536},
                "3B": {"layers": 64, "d_model": 2560}
            },
            "pythia": {
                "0.5B": {"layers": 24, "hidden": 1024, "heads": 16, "intermediate": 4096},
                "1.5B": {"layers": 32, "hidden": 2048, "heads": 16, "intermediate": 8192},
                "3B": {"layers": 32, "hidden": 2560, "heads": 32, "intermediate": 10240}
            },
            "rwkv": {
                "0.5B": {"layers": 24, "embed_dim": 1024},
                "1.5B": {"layers": 32, "embed_dim": 2048},
                "3B": {"layers": 40, "embed_dim": 2560}
            }
        }
        
        # Attention mechanisms from paper
        self.attention_types = {
            "MQA": "Multi-Query Attention",
            "GQA": "Grouped-Query Attention", 
            "MLA": "Multi-Head Latent Attention",
            "NSA": "No Shared Attention"
        }
        
        # Paper experiment configurations
        self.paper_experiments = {
            "pretrain": {
                "dataset": "fine-webedu-v1.2.0-sample-350BT",
                "context_length": 8192,
                "batch_sizes": {"0.5B": 8, "1.5B": 4, "3B": 2},
                "learning_rate": 1e-4,
                "optimizer": "AdamW",
                "weight_decay": 0.1,
                "warmup_steps": 100,
                "precision": "bfloat16"
            },
            "inference": {
                "precisions": ["bfloat16", "float16", "int4"],
                "batch_sizes": [1, 4, 8, 16],
                "seq_lengths": [512, 1024, 2048, 4096, 8192]
            },
            "finetune": {
                "methods": ["LoRA", "DoRA", "PISSA"],
                "ranks": [8, 16, 32, 64],
                "alpha_multipliers": [1, 2, 4]
            }
        }
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser"""
        parser = argparse.ArgumentParser(
            description="EfficientLLM: A Comprehensive Benchmark for Large Language Model Efficiency",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples aligned with paper experiments:

  # Table 3: Attention Mechanisms Efficiency (MQA, GQA, MLA, NSA)
  efficientllm --stage pretrain --model qwen2.5 --size 0.5B --attn_type MQA
  efficientllm --stage pretrain --model qwen2.5 --size 1.5B --attn_type GQA
  efficientllm --stage pretrain --model qwen2.5 --size 3B --attn_type MLA
  
  # Table 4: Positional Encoding Efficiency (RoPE, Absolute, Learnable, Relative)
  efficientllm --stage pretrain --model qwen2.5 --size 1.5B --pos_encoding rope
  efficientllm --stage pretrain --model qwen2.5 --size 1.5B --pos_encoding absolute
  
  # Table 5: MoE Mechanisms (Dense vs MoE models)  
  efficientllm --stage pretrain --model qwen2.5 --size 1.5B --moe_experts 8 --top_k 2
  
  # Table 6: Attention-Free Mechanisms Comparison (0.5B, 1.5B, 3B models)
  efficientllm --stage pretrain --compare_attention_free --models qwen2.5,mamba,pythia,rwkv
  
  # Table 7&8: PEFT Training Efficiency (O1-SFT and Medical-O1 datasets)
  efficientllm --stage peft_benchmark --benchmark_type all
  efficientllm --stage peft_benchmark --method LoRA-plus --model llama3.2-1b --dataset O1-SFT
  efficientllm --stage peft_benchmark --method freeze --model llama3.2-3b --dataset Medical-O1
  
  # Table 9: Quantization Inference Efficiency (bfloat16, float16, int4)
  efficientllm --stage quantization_benchmark --models deepseek-r1-distill-qwen-1.5b,qwen2.5-7b,qwen2.5-14b --precision bfloat16,float16,int4
  
  # Download pre-trained checkpoints
  efficientllm --down
  
  # Reproduce all paper experiments
  efficientllm --reproduce_paper --experiment all
  
  # Specific experiment reproduction
  efficientllm --reproduce_paper --experiment attention_mechanisms
  efficientllm --reproduce_paper --experiment positional_encoding  
  efficientllm --reproduce_paper --experiment moe_mechanisms
  efficientllm --reproduce_paper --experiment attention_free
  efficientllm --reproduce_paper --experiment peft_benchmark
  efficientllm --reproduce_paper --experiment quantization
            """
        )
        
        # Main arguments
        parser.add_argument("--stage", 
                          choices=["pretrain", "inference", "finetune", "analysis", "peft_benchmark", "quantization_benchmark"],
                          help="Experiment stage to run")
        
        parser.add_argument("--model", 
                          choices=["qwen2.5", "mamba", "pythia", "rwkv", "llama3.2-1b", "llama3.2-3b", "llama3.1-8b", "qwen2.5-7b", "qwen2.5-14b", "mistral-7b", "mistral-24b", "deepseek-r1-distill-qwen-1.5b"],
                          help="Model architecture to use")
        
        parser.add_argument("--size", 
                          choices=["0.5B", "1.5B", "3B"],
                          help="Model size")
        
        parser.add_argument("--attn_type",
                          choices=["MQA", "GQA", "MLA", "NSA"],
                          help="Attention mechanism type")
        
        parser.add_argument("--pos_encoding",
                          choices=["rope", "absolute", "learnable_absolute", "relative", "none"],
                          help="Positional encoding type")
        
        parser.add_argument("--moe_experts", type=int,
                          help="Number of MoE experts")
        
        parser.add_argument("--top_k", type=int,
                          help="Top-K routing for MoE")
        
        parser.add_argument("--precision",
                          help="Training/inference precision (comma-separated for multiple)")
        
        parser.add_argument("--batch_size", type=int,
                          help="Batch size (overrides default)")
        
        parser.add_argument("--max_steps", type=int, default=1000,
                          help="Maximum training steps")
        
        parser.add_argument("--device", default="cuda:0",
                          help="Device to use for training/inference")
        
        parser.add_argument("--output_dir", 
                          help="Output directory for results")
        
        # Paper reproduction
        parser.add_argument("--reproduce_paper", action="store_true",
                          help="Reproduce paper experiments")
        
        parser.add_argument("--experiment",
                          choices=["attention_mechanisms", "positional_encoding", "moe_mechanisms",
                                 "attention_free", "peft_benchmark", "quantization", "all"],
                          help="Specific paper experiment to reproduce")
        
        # Special experiments
        parser.add_argument("--compare_attention_free", action="store_true",
                          help="Run attention-free mechanism comparison")
        
        parser.add_argument("--models",
                          help="Comma-separated list of models for comparison")
        
        parser.add_argument("--method",
                          choices=["LoRA", "LoRA-plus", "RSLoRA", "DoRA", "PISSA", "Freeze", "Full"],
                          help="Fine-tuning/PEFT method")
        
        parser.add_argument("--dataset",
                          choices=["O1-SFT", "Medical-O1", "MMLU-Pro", "BBH", "GPQA", "IFEval", "MATH", "MUSR"],
                          help="Dataset for evaluation")
        
        parser.add_argument("--tasks",
                          help="Comma-separated list of evaluation tasks")
        
        parser.add_argument("--benchmark_type",
                          choices=["quick", "lora", "all", "quantization"],
                          help="Type of benchmark to run")
        
        # Advanced options
        parser.add_argument("--config_file",
                          help="Custom configuration file")
        
        parser.add_argument("--dry_run", action="store_true",
                          help="Show commands without executing")
        
        parser.add_argument("--verbose", "-v", action="store_true",
                          help="Verbose output")
        
        parser.add_argument("--down", action="store_true",
                          help="Download pre-trained checkpoints")
        
        return parser
    
    def run_pretrain(self, args) -> int:
        """Run pretraining experiments"""
        if args.compare_attention_free:
            return self.run_attention_free_comparison(args)
        
        if not args.model or not args.size:
            print("Error: --model and --size are required for pretraining")
            return 1
        
        # For Qwen2.5 attention mechanisms, positional encoding, and MoE experiments
        if args.model == "qwen2.5":
            return self.run_qwen_efficientllm_benchmark(args)
        
        # For other models, run individual training scripts
        if args.model == "mamba":
            return self.run_mamba_pretrain(args)
        elif args.model == "pythia":
            return self.run_pythia_pretrain(args)
        elif args.model == "rwkv":
            return self.run_rwkv_pretrain(args)
        
        return 1
    
    def run_qwen_efficientllm_benchmark(self, args) -> int:
        """Run Qwen2.5 EfficientLLM benchmark (Table 3, 4, 5)"""
        megatron_dir = self.pretrain_dir / "Pai-Megatron-Patch"
        
        # Determine experiment type
        if args.attn_type:
            experiment_type = "attention"
        elif args.pos_encoding:
            experiment_type = "positional"
        elif args.moe_experts:
            experiment_type = "moe"
        else:
            experiment_type = "attention"  # default
        
        cmd = [
            "bash", str(megatron_dir / "scripts" / "run_efficientllm_benchmark.sh"),
            experiment_type
        ]
        
        # Set environment variables for specific configurations
        env = os.environ.copy()
        if args.attn_type:
            env["ATTENTION_TYPE"] = args.attn_type
        if args.size:
            env["MODEL_SIZE"] = args.size
        if args.pos_encoding:
            env["POS_ENCODING"] = args.pos_encoding
        if args.moe_experts:
            env["MOE_EXPERTS"] = str(args.moe_experts)
        if args.top_k:
            env["TOP_K"] = str(args.top_k)
        
        return self.execute_command_with_env(cmd, env, args.dry_run, args.verbose)
    
    def run_attention_free_comparison(self, args) -> int:
        """Run attention-free mechanism comparison from paper (Table 6)"""
        models = args.models.split(",") if args.models else ["qwen2.5", "mamba", "pythia", "rwkv"]
        
        print("Running attention-free mechanism comparison...")
        print(f"Models: {models}")
        
        # Use the existing attention-free benchmark script
        script_path = self.pretrain_dir / "scripts" / "run_all_attention_free_experiments.sh"
        
        cmd = [
            "bash", str(script_path),
            "dsw",  # environment
            args.device,
            str(args.max_steps)
        ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def run_mamba_pretrain(self, args) -> int:
        """Run Mamba pretraining"""
        script_path = self.pretrain_dir / "mamba" / "train_mamba_fineweb.py"
        
        cmd = [
            "python", str(script_path),
            "--model_size", args.size,
            "--data_path", str(self.pretrain_dir / "Pai-Megatron-Patch" / "data" / "fineweb_edu" / "processed" / "fineweb_edu_train.jsonl"),
            "--output_dir", args.output_dir or f"./results/pretrain/mamba_{args.size}",
            "--max_steps", str(args.max_steps),
            "--device", args.device
        ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def run_pythia_pretrain(self, args) -> int:
        """Run Pythia pretraining"""
        script_path = self.pretrain_dir / "pythia" / "train_pythia_fineweb.py"
        
        cmd = [
            "python", str(script_path),
            "--model_size", args.size,
            "--data_path", str(self.pretrain_dir / "Pai-Megatron-Patch" / "data" / "fineweb_edu" / "processed" / "fineweb_edu_train.jsonl"),
            "--output_dir", args.output_dir or f"./results/pretrain/pythia_{args.size}",
            "--max_steps", str(args.max_steps),
            "--device", args.device
        ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def run_rwkv_pretrain(self, args) -> int:
        """Run RWKV pretraining"""
        script_path = self.pretrain_dir / "RWKV-LM" / "train_rwkv_fineweb.py"
        
        cmd = [
            "python", str(script_path),
            "--model_size", args.size,
            "--data_path", str(self.pretrain_dir / "Pai-Megatron-Patch" / "data" / "fineweb_edu" / "processed" / "fineweb_edu_train.jsonl"),
            "--output_dir", args.output_dir or f"./results/pretrain/rwkv_{args.size}",
            "--max_steps", str(args.max_steps),
            "--device", args.device
        ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def run_download(self, args) -> int:
        """Download pre-trained checkpoints"""
        import urllib.request
        import zipfile
        import tempfile
        import shutil
        from tqdm import tqdm
        
        checkpoint_url = "http://47.251.191.39:7890/download"
        
        print("Downloading EfficientLLM pre-trained checkpoints...")
        print(f"Source: {checkpoint_url}")
        
        # Create download directory
        download_dir = self.base_dir / "checkpoints"
        download_dir.mkdir(exist_ok=True)
        
        temp_zip = download_dir / "checkpoints.zip"
        
        try:
            # Download with progress bar
            def show_progress(block_num, block_size, total_size):
                if hasattr(show_progress, 'pbar'):
                    show_progress.pbar.update(block_size)
                else:
                    show_progress.pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading")
            
            print(f"Downloading to: {temp_zip}")
            urllib.request.urlretrieve(checkpoint_url, temp_zip, reporthook=show_progress)
            
            if hasattr(show_progress, 'pbar'):
                show_progress.pbar.close()
            
            print(f"\nDownload completed. Extracting checkpoints...")
            
            # Extract zip file
            with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            # Clean up zip file
            temp_zip.unlink()
            
            print(f"Checkpoints extracted to: {download_dir}")
            print("Available checkpoints:")
            
            # List available checkpoints
            for item in download_dir.iterdir():
                if item.is_dir():
                    print(f"  - {item.name}")
            
            return 0
            
        except Exception as e:
            print(f"Download failed: {e}")
            if temp_zip.exists():
                temp_zip.unlink()
            return 1

    def execute_command_with_env(self, cmd: List[str], env: Dict[str, str], dry_run: bool = False, verbose: bool = False) -> int:
        """Execute a command with custom environment"""
        if verbose or dry_run:
            print(f"Command: {' '.join(cmd)}")
            print(f"Environment: {env}")
        
        if dry_run:
            return 0
        
        try:
            result = subprocess.run(cmd, env=env, check=True, capture_output=not verbose)
            if verbose:
                print(f"Exit code: {result.returncode}")
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            return e.returncode
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")
            return 1
    
    def run_inference(self, args) -> int:
        """Run inference benchmarks"""
        if not args.model or not args.size:
            print("Error: --model and --size are required for inference")
            return 1
        
        precisions = args.precision.split(",") if args.precision else ["bfloat16"]
        
        # Use the lm-evaluation-harness batch script
        script_path = self.quantization_dir / "lm-evaluation-harness-main" / "batch_eval.py"
        
        cmd = [
            "python", str(script_path),
            "--models", f"{args.model}-{args.size}",
            "--precisions", ",".join(precisions),
            "--output_dir", args.output_dir or f"./results/inference/{args.model}_{args.size}",
            "--device", args.device
        ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def run_finetune(self, args) -> int:
        """Run fine-tuning experiments"""
        if not args.model or not args.size or not args.method:
            print("Error: --model, --size, and --method are required for fine-tuning")
            return 1
        
        # Use LLaMA-Factory for fine-tuning
        factory_dir = self.finetune_dir / "LLaMA-Factory"
        
        # Build configuration
        config = {
            "stage": "sft",
            "model_name": f"{args.model}-{args.size}",
            "dataset": "fine_webedu",
            "finetuning_type": args.method.lower(),
            "lora_rank": args.rank or 16,
            "output_dir": args.output_dir or f"./results/finetune/{args.model}_{args.size}_{args.method}"
        }
        
        # Save config and run
        config_file = "temp_finetune_config.yaml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config, f)
        
        cmd = [
            "python", str(factory_dir / "src" / "train.py"),
            "--config", config_file
        ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def run_analysis(self, args) -> int:
        """Run analysis and generate results"""
        if args.compare_attention_free:
            # Generate attention-free results table
            script_path = self.pretrain_dir / "scripts" / "collect_attention_free_results.py"
            cmd = [
                "python", str(script_path),
                "--results_dir", "./results/pretrain",
                "--output_dir", "./results/tables"
            ]
        else:
            # Generate inference results table
            script_path = self.quantization_dir / "lm-evaluation-harness-main" / "process_results.py" 
            cmd = [
                "python", str(script_path),
                "--results_dir", "./results/inference",
                "--output_dir", "./results/tables"
            ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def reproduce_paper(self, args) -> int:
        """Reproduce paper experiments"""
        experiment = args.experiment or "all"
        
        if experiment in ["attention_mechanisms", "all"]:
            print("Reproducing Table 3: Attention Mechanisms Efficiency...")
            for model in ["qwen2.5"]:
                for size in ["0.5B", "1.5B", "3B"]:
                    for attn_type in ["MQA", "GQA", "MLA", "NSA"]:
                        args.model = model
                        args.size = size
                        args.attn_type = attn_type
                        self.run_pretrain(args)
        
        if experiment in ["positional_encoding", "all"]:
            print("Reproducing Table 4: Positional Encoding Efficiency...")
            for pos_enc in ["rope", "absolute", "learnable_absolute", "relative", "none"]:
                args.model = "qwen2.5"
                args.size = "1.5B"
                args.pos_encoding = pos_enc
                self.run_pretrain(args)
        
        if experiment in ["moe_mechanisms", "all"]:
            print("Reproducing Table 5: MoE Mechanisms...")
            # Dense models
            for size in ["1.5B", "3B"]:
                args.model = "qwen2.5"
                args.size = size
                args.moe_experts = None
                self.run_pretrain(args)
            
            # MoE models
            for base_size in ["0.5B", "1.5B"]:
                args.model = "qwen2.5"
                args.size = base_size
                args.moe_experts = 8
                args.top_k = 2
                self.run_pretrain(args)
        
        if experiment in ["attention_free", "all"]:
            print("Reproducing Table 6: Attention-free mechanism experiments...")
            args.compare_attention_free = True
            self.run_pretrain(args)
        
        if experiment in ["peft_benchmark", "all"]:
            print("Reproducing Table 7&8: PEFT benchmark experiments...")
            args.stage = "peft_benchmark"
            args.benchmark_type = "all"
            self.run_peft_benchmark(args)
        
        if experiment in ["quantization", "all"]:
            print("Reproducing Table 9: Quantization experiments...")
            args.stage = "quantization_benchmark"  
            args.models = "deepseek-r1-distill-qwen-1.5b,deepseek-r1-distill-llama-8b,deepseek-r1-distill-qwen-14b,qwen2.5-7b,qwen2.5-14b,qwen2.5-32b,phi-4,phi-3.5-mini,yi-34b"
            args.precision = "bfloat16,float16,int4"
            args.tasks = "MMLU-Pro,BBH,GPQA,IFEval,MATH,MUSR"
            self.run_quantization_benchmark(args)
        
        return 0
    
    def run_peft_benchmark(self, args) -> int:
        """Run PEFT benchmark suite"""
        benchmark_type = args.benchmark_type or "all"
        
        # LLaMA-Factory PEFT benchmark
        factory_dir = self.finetune_dir / "LLaMA-Factory"
        
        if benchmark_type == "quick":
            cmd = ["bash", str(factory_dir / "scripts" / "run_peft_benchmark.sh"), "quick"]
        elif benchmark_type == "lora":
            cmd = ["bash", str(factory_dir / "scripts" / "run_peft_benchmark.sh"), "lora"]  
        elif benchmark_type == "all":
            cmd = ["bash", str(factory_dir / "scripts" / "run_peft_benchmark.sh"), "all"]
        else:
            # Run specific method if provided
            if not args.method or not args.model or not args.dataset:
                print("Error: --method, --model, and --dataset are required for specific PEFT benchmark")
                return 1
            
            # Find appropriate config file
            config_file = self._find_peft_config(args.method, args.model, args.dataset, factory_dir)
            if not config_file:
                print(f"Error: No configuration found for {args.method} on {args.model} with {args.dataset}")
                return 1
            
            cmd = ["llamafactory-cli", "train", str(config_file)]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def run_quantization_benchmark(self, args) -> int:
        """Run quantization benchmark suite"""
        harness_dir = self.quantization_dir / "lm-evaluation-harness-main"
        
        # Build model list
        if args.models:
            models = args.models.split(",")
        elif args.model:
            models = [args.model]
        else:
            models = ["deepseek-r1-distill-qwen-1.5b", "qwen2.5-7b"]
        
        # Build precision list  
        precisions = args.precision.split(",") if args.precision else ["bfloat16", "float16", "int4"]
        
        # Build task list
        if args.tasks:
            tasks = args.tasks.split(",")
        else:
            tasks = ["MMLU-Pro", "BBH", "GPQA", "IFEval", "MATH", "MUSR"]
        
        cmd = [
            "python", str(harness_dir / "batch_eval.py"),
            "--models"] + models + [
            "--precisions"] + precisions + [
            "--tasks"] + tasks + [
            "--output_dir", args.output_dir or "./results/quantization",
            "--max_workers", "1"
        ]
        
        return self.execute_command(cmd, args.dry_run, args.verbose)
    
    def _find_peft_config(self, method: str, model: str, dataset: str, factory_dir: Path) -> Optional[Path]:
        """Find PEFT configuration file"""
        # Map method names to directory structure
        method_map = {
            "LoRA": "lora",
            "LoRA-plus": "lora_plus", 
            "RSLoRA": "rslora",
            "DoRA": "dora",
            "PISSA": "pissa",
            "Freeze": "freeze",
            "Full": "full"
        }
        
        # Map model names
        model_map = {
            "llama3.2-1b": "llama3_2_1b",
            "llama3.2-3b": "llama3_2_3b", 
            "llama3.1-8b": "llama3_1_8b",
            "qwen2.5-7b": "qwen2_5_7b",
            "qwen2.5-14b": "qwen2_5_14b",
            "mistral-7b": "mistral_7b",
            "mistral-24b": "mistral_24b"
        }
        
        # Map dataset names
        dataset_map = {
            "O1-SFT": "o1_sft",
            "Medical-O1": "medical_o1"
        }
        
        method_name = method_map.get(method, method.lower())
        model_name = model_map.get(model, model.replace("-", "_"))
        dataset_name = dataset_map.get(dataset, dataset.lower())
        
        # Determine subdirectory
        if method in ["LoRA", "LoRA-plus", "RSLoRA", "DoRA", "PISSA"]:
            subdir = "lora_variants"
        else:
            subdir = "freeze_full"
        
        config_path = factory_dir / "examples" / "peft_benchmark" / subdir / f"{model_name}_{dataset_name}_{method_name}.yaml"
        
        return config_path if config_path.exists() else None

    def execute_command(self, cmd: List[str], dry_run: bool = False, verbose: bool = False) -> int:
        """Execute a command"""
        if verbose or dry_run:
            print(f"Command: {' '.join(cmd)}")
        
        if dry_run:
            return 0
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=not verbose)
            if verbose:
                print(f"Exit code: {result.returncode}")
            return result.returncode
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            return e.returncode
        except FileNotFoundError:
            print(f"Command not found: {cmd[0]}")
            return 1


def main():
    """Main CLI entry point"""
    cli = EfficientLLMCLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    
    try:
        if args.down:
            return cli.run_download(args)
        elif args.reproduce_paper:
            return cli.reproduce_paper(args)
        elif args.stage == "pretrain":
            return cli.run_pretrain(args)
        elif args.stage == "inference":
            return cli.run_inference(args)
        elif args.stage == "finetune":
            return cli.run_finetune(args)
        elif args.stage == "analysis":
            return cli.run_analysis(args)
        elif args.stage == "peft_benchmark":
            return cli.run_peft_benchmark(args)
        elif args.stage == "quantization_benchmark":
            return cli.run_quantization_benchmark(args)
        elif args.stage:
            print(f"Unknown stage: {args.stage}")
            return 1
        else:
            print("Error: --stage is required when not using --down or --reproduce_paper")
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())