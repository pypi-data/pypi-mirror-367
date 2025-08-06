"""Hydra CLI."""

import os
import logging
import hydra

import torch

from hydra.core.config_store import ConfigStore
from hydra.core.hydra_config import HydraConfig
from hydra.utils import instantiate
from torch.utils.collect_env import get_pretty_env_info
from lightning.pytorch import Callback

from vis4d.common.logging import rank_zero_info, setup_logger
from vis4d.common.util import set_tf32
from vis4d.engine.loss_module import LossModule

from unidet3d.pl.callbacks.scheduler import LRSchedulerCallback
from unidet3d.pl.config import DefaultConfig
from unidet3d.pl.training_module import TrainingModule
from unidet3d.pl.data_module import DataModule


@hydra.main(config_path="./", config_name="base", version_base=None)
def main(config: DefaultConfig):
    """Main function."""
    # Parse config
    assert config.action in {
        "fit",
        "test",
    }, f"Invalid actione: {config.action}"
    mode = config.action

    num_gpus = config.gpus
    num_nodes = config.nodes

    output_dir = HydraConfig.get().runtime.output_dir

    # Setup logging
    logger_vis4d = logging.getLogger("vis4d")
    logger_pl = logging.getLogger("pytorch_lightning")
    log_file = os.path.join(output_dir, "run.log")
    setup_logger(logger_vis4d, log_file)
    setup_logger(logger_pl, log_file)

    rank_zero_info("Environment info: %s", get_pretty_env_info())

    # PyTorch Setting
    set_tf32(config.use_tf32, config.tf32_matmul_precision)
    torch.hub.set_dir(f"{config.work_dir}/.cache/torch/hub")

    # Setup device
    if num_gpus > 0:
        accelerator = "gpu"
        devices = num_gpus
    else:
        accelerator = "cpu"
        devices = 1

    # Instantiate data connector
    train_data_connector, test_data_connector = instantiate(
        config.data_connector, _convert_="object"
    )

    # Instantiate loss module
    if config.action == "fit":
        loss = LossModule(
            losses=list(instantiate(config.losses, _convert_="object"))
        )
    else:
        loss = None

    # Callbacks
    callbacks: list[Callback] = []
    for cb in config.callbacks:
        callback = instantiate(cb, _convert_="object")

        # if not config.vis and isinstance(callback, VisualizerCallback):
        #     rank_zero_info(
        #         "VisualizerCallback is not used. "
        #         "Please set ++vis=True to use it."
        #     )
        #     continue

        callbacks.append(callback)

    # Add needed callbacks
    callbacks.append(LRSchedulerCallback())

    # Checkpoint path
    ckpt_path = config.ckpt

    # Resume training
    resume = config.resume

    if resume:
        if ckpt_path is None:
            resume_ckpt_path = os.path.join(
                output_dir, "checkpoints/last.ckpt"
            )
        else:
            resume_ckpt_path = ckpt_path
    else:
        resume_ckpt_path = None

    trainer = instantiate(
        config.pl_trainer,
        work_dir=config.work_dir,
        exp_name=config.experiment_name,
        version=config.version,
        timestamp=config.timestamp,
        num_nodes=num_nodes,
        accelerator=accelerator,
        devices=devices,
        callbacks=callbacks,
        _convert_="object",
    )

    training_module = TrainingModule(
        config.model,
        config.optimizer,
        loss,
        train_data_connector,
        test_data_connector,
        dict(config.params),
        config.seed,
        ckpt_path if not resume else None,
        config.compute_flops,
    )

    # Data loaders
    data_module = DataModule(config.data)

    if mode == "fit":
        trainer.fit(
            training_module, datamodule=data_module, ckpt_path=resume_ckpt_path
        )
    elif mode == "test":
        trainer.test(training_module, datamodule=data_module, verbose=False)


if __name__ == "__main__":
    """Main."""

    # cs = ConfigStore.instance()
    # cs.store(name="vis4d_config", node=DefaultConfig)

    main()
