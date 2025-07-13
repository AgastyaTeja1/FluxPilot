# training/train.py

import os
import argparse
import logging

import mlflow
import mlflow.pytorch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments
)

from training.data_loader import load_data
from training.hf_utils import preprocess_function


def parse_args():
    parser = argparse.ArgumentParser(
        description="Fine-tune the Granite LLM with MLflow tracking"
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default=os.getenv("BASE_MODEL", "granite/granite-model"),
        help="Base model to fine-tune"
    )
    parser.add_argument(
        "--dataset_name",
        type=str,
        default="wikitext",
        help="HuggingFace dataset name"
    )
    parser.add_argument(
        "--dataset_config",
        type=str,
        default="wikitext-2-raw-v1",
        help="HuggingFace dataset config"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./outputs",
        help="Where to save the fine-tuned model"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=int(os.getenv("EPOCHS", 3)),
        help="Number of training epochs"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=int(os.getenv("BATCH_SIZE", 4)),
        help="Batch size per device"
    )
    return parser.parse_args()


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — %(levelname)s — %(message)s"
    )
    logging.info("Logger initialized")


def main():
    args = parse_args()
    setup_logging()

    # MLflow setup
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_uri)
    exp_name = os.getenv("MLFLOW_EXPERIMENT", "FluxPilot_Granite")
    mlflow.set_experiment(exp_name)
    logging.info(f"MLflow URI={mlflow_uri}, experiment={exp_name}")

    # Load raw dataset
    raw_dataset = load_data(args.dataset_name, args.dataset_config)
    logging.info(f"Loaded dataset {args.dataset_name}/{args.dataset_config} with {len(raw_dataset)} records")

    # Initialize tokenizer & model
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForCausalLM.from_pretrained(args.model_name)
    logging.info(f"Loaded model & tokenizer from {args.model_name}")

    # Preprocess (tokenize + chunk, drop unused cols)
    tokenized = raw_dataset.map(
        lambda examples: preprocess_function(examples, tokenizer),
        batched=True,
        remove_columns=raw_dataset.column_names
    )
    logging.info("Dataset tokenized")

    # TrainingArguments with MLflow integration
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        logging_dir="./logs",
        logging_steps=50,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="loss",
        report_to=["mlflow"]
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized
    )

    # Run training under MLflow
    with mlflow.start_run(run_name="granite_finetune") as run:
        mlflow.pytorch.autolog()               # auto-log all params/metrics/artifacts
        trainer.train()
        mlflow.log_params({
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "model_name": args.model_name
        })

        # Register the best model in MLflow Model Registry
        run_id = run.info.run_id
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, "FluxPilot_Granite")
        logging.info(f"Registered model 'FluxPilot_Granite' from run {run_id}")

    logging.info("Training complete.")


if __name__ == "__main__":
    main()
