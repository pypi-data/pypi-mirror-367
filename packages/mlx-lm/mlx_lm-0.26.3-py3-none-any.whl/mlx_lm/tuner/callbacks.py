# Copyright © 2024 Apple Inc.

try:
    import wandb
except ImportError:
    wandb = None


class TrainingCallback:

    def on_train_loss_report(self, train_info: dict):
        """Called to report training loss at specified intervals."""
        pass

    def on_val_loss_report(self, val_info: dict):
        """Called to report validation loss at specified intervals or the beginning."""
        pass


class WandBCallback(TrainingCallback):
    def __init__(
        self,
        project_name: str,
        log_dir: str,
        config: dict,
        wrapped_callback: TrainingCallback = None,
    ):
        if wandb is None:
            raise ImportError(
                "wandb is not installed. Please install it to use WandBCallback."
            )
        self.wrapped_callback = wrapped_callback
        wandb.init(project=project_name, dir=log_dir, config=config)

    def _convert_to_serializable(self, data: dict) -> dict:
        return {k: v.tolist() if hasattr(v, "tolist") else v for k, v in data.items()}

    def on_train_loss_report(self, train_info: dict):
        wandb.log(
            self._convert_to_serializable(train_info), step=train_info.get("iteration")
        )
        if self.wrapped_callback:
            self.wrapped_callback.on_train_loss_report(train_info)

    def on_val_loss_report(self, val_info: dict):
        wandb.log(
            self._convert_to_serializable(val_info), step=val_info.get("iteration")
        )
        if self.wrapped_callback:
            self.wrapped_callback.on_val_loss_report(val_info)
