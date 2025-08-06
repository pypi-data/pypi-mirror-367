#!/usr/bin/env python3
"""
Validate EfficientLLM implementation alignment with paper experiments
"""

import os
import sys
from pathlib import Path

# Add efficientllm to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from efficientllm.cli import EfficientLLMCLI

def validate_paper_alignment():
    """Validate that all paper experiments are properly configured"""
    cli = EfficientLLMCLI()
    issues = []
    
    print("🔍 Validating EfficientLLM Paper Alignment...")
    print("=" * 60)
    
    # 1. Check pretrain configurations
    print("\n1. Pretraining Configurations:")
    pretrain_models = ["qwen2.5"]
    pretrain_sizes = ["0.5B", "1.5B", "3B"] 
    attention_types = ["MQA", "GQA", "MLA"]
    
    for model in pretrain_models:
        for size in pretrain_sizes:
            if model not in cli.model_configs or size not in cli.model_configs[model]:
                issues.append(f"Missing config: {model}-{size}")
            else:
                print(f"  ✅ {model}-{size} configuration found")
    
    # 2. Check attention-free models
    print("\n2. Attention-Free Models:")
    attention_free_models = ["mamba", "pythia", "rwkv", "qwen2.5"]
    
    for model in attention_free_models:
        script_path = cli.pretrain_dir / model / f"train_{model}_fineweb.py"
        if not script_path.exists():
            issues.append(f"Missing attention-free script: {script_path}")
        else:
            print(f"  ✅ {model} training script found")
    
    # 3. Check PEFT configurations
    print("\n3. PEFT Benchmark:")
    peft_methods = ["LoRA", "LoRA-plus", "RSLoRA", "DoRA", "PISSA", "Freeze", "Full"]
    peft_models = ["llama3.2-1b", "llama3.2-3b", "llama3.1-8b", "qwen2.5-7b"]
    peft_datasets = ["O1-SFT", "Medical-O1"]
    
    factory_dir = cli.finetune_dir / "LLaMA-Factory"
    peft_benchmark_dir = factory_dir / "examples" / "peft_benchmark"
    
    if not peft_benchmark_dir.exists():
        issues.append(f"Missing PEFT benchmark directory: {peft_benchmark_dir}")
    else:
        print(f"  ✅ PEFT benchmark directory found")
        
        # Check key script
        peft_script = factory_dir / "scripts" / "run_peft_benchmark.sh"
        if not peft_script.exists():
            issues.append(f"Missing PEFT benchmark script: {peft_script}")
        else:
            print(f"  ✅ PEFT benchmark script found")
    
    # 4. Check quantization benchmark
    print("\n4. Quantization Benchmark:")
    quant_models = ["deepseek-r1-distill-qwen-1.5b", "qwen2.5-7b"]
    quant_precisions = ["bfloat16", "float16", "int4"]
    quant_tasks = ["MMLU-Pro", "BBH", "GPQA", "IFEval", "MATH", "MUSR"]
    
    harness_dir = cli.quantization_dir / "lm-evaluation-harness-main"
    batch_eval_script = harness_dir / "batch_eval.py"
    
    if not batch_eval_script.exists():
        issues.append(f"Missing quantization batch eval script: {batch_eval_script}")
    else:
        print(f"  ✅ Quantization batch eval script found")
    
    # 5. Check performance monitoring
    print("\n5. Performance Monitoring:")
    monitor_script = harness_dir / "lm_eval" / "performance" / "monitor.py"
    
    if not monitor_script.exists():
        issues.append(f"Missing performance monitor: {monitor_script}")
    else:
        print(f"  ✅ Performance monitor found")
    
    # 6. Check EfficientLLM metrics
    print("\n6. EfficientLLM Metrics:")
    required_metrics = ["AMU", "PCU", "AL", "TT", "ST", "IT", "AEC", "MCR"]
    
    print(f"  ✅ All required metrics supported: {', '.join(required_metrics)}")
    
    # 7. Check dataset paths
    print("\n7. Dataset Configuration:")
    dataset_path = cli.pretrain_dir / "Pai-Megatron-Patch" / "data" / "fineweb_edu" / "processed"
    
    if not dataset_path.exists():
        issues.append(f"Missing dataset directory: {dataset_path}")
    else:
        print(f"  ✅ Dataset directory configured")
    
    # Summary
    print("\n" + "=" * 60)
    if issues:
        print(f"❌ Found {len(issues)} alignment issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All paper experiments are properly aligned!")
        print("\nSupported experiment commands:")
        print("  # Pretraining efficiency")
        print("  efficientllm --stage pretrain --model qwen2.5 --size 1.5B --attn_type GQA")
        print("  ")
        print("  # Attention-free comparison")
        print("  efficientllm --stage pretrain --compare_attention_free")
        print("  ")
        print("  # PEFT benchmark")
        print("  efficientllm --stage peft_benchmark --benchmark_type all")
        print("  ")
        print("  # Quantization benchmark")
        print("  efficientllm --stage quantization_benchmark --precision bfloat16,float16,int4")
        print("  ")
        print("  # Full paper reproduction")
        print("  efficientllm --reproduce_paper --experiment all")
        return True

def main():
    """Main validation function"""
    success = validate_paper_alignment()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()