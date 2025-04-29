from transformers import TrainerCallback
import torch

class SaveTrainLogitsCallback(TrainerCallback):
    def __init__(self, trainer, train_dataset, save_dir):
        self.trainer = trainer
        self.train_dataset = train_dataset
        self.save_dir = save_dir
        self.epoch_count = 0

    def on_epoch_end(self, args, state, control, **kwargs):
        # 让trainer在train_dataset上预测
        outputs = self.trainer.predict(self.train_dataset)

        # outputs.predictions 是 logits
        logits = outputs.predictions  # shape: (num_samples, num_classes)

        # 保存 logits，比如保存成 torch
        save_path = f"{self.save_dir}/train_logits_epoch_{self.epoch_count}.pt"
        torch.save(torch.tensor(logits), save_path)

        print(f"Saved train logits for epoch {self.epoch_count} at {save_path}")
        self.epoch_count += 1
