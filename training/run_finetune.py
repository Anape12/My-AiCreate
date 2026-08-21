"""Explicit LoRA fine-tuning entry point.

Install requirements-training.txt in a separate GPU environment before use.
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--method", choices=["lora"], default="lora")
    args = parser.parse_args()

    try:
        from datasets import load_dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
        from trl import SFTTrainer
        from peft import LoraConfig
    except ImportError as exc:
        raise SystemExit("Install requirements-training.txt in a GPU environment before fine-tuning.") from exc

    dataset = load_dataset("json", data_files=args.dataset, split="train")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.base_model, device_map="auto")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05),
        args=TrainingArguments(output_dir=args.output_dir, num_train_epochs=3, per_device_train_batch_size=1),
    )
    trainer.train()
    trainer.save_model(args.output_dir)


if __name__ == "__main__":
    main()
