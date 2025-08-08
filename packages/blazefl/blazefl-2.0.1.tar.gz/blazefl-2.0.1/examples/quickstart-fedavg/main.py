import logging
from datetime import datetime
from pathlib import Path

import hydra
import torch
import torch.multiprocessing as mp
from blazefl.contrib import (
    FedAvgBaseClientTrainer,
    FedAvgBaseServerHandler,
    FedAvgProcessPoolClientTrainer,
    FedAvgThreadPoolClientTrainer,
)
from blazefl.reproducibility import setup_reproducibility
from hydra.core import hydra_config
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf
from torch.utils.tensorboard.writer import SummaryWriter

from config import MyConfig
from dataset import PartitionedCIFAR10
from models import FedAvgModelSelector


class FedAvgPipeline:
    def __init__(
        self,
        handler: FedAvgBaseServerHandler,
        trainer: FedAvgBaseClientTrainer
        | FedAvgProcessPoolClientTrainer
        | FedAvgThreadPoolClientTrainer,
        writer: SummaryWriter,
    ) -> None:
        self.handler = handler
        self.trainer = trainer
        self.writer = writer

    def main(self):
        while not self.handler.if_stop():
            round_ = self.handler.round
            # server side
            sampled_clients = self.handler.sample_clients()
            broadcast = self.handler.downlink_package()

            # client side
            self.trainer.local_process(broadcast, sampled_clients)
            uploads = self.trainer.uplink_package()

            # server side
            for pack in uploads:
                self.handler.load(pack)

            summary = self.handler.get_summary()
            for key, value in summary.items():
                self.writer.add_scalar(key, value, round_)
            formatted_summary = ", ".join(f"{k}: {v:.3f}" for k, v in summary.items())
            logging.info(f"round: {round_}, {formatted_summary}")

        logging.info("done!")


cs = ConfigStore.instance()
cs.store(name="config", node=MyConfig)


@hydra.main(version_base=None, config_name="config")
def main(cfg: MyConfig):
    print(OmegaConf.to_yaml(cfg))

    log_dir = hydra_config.HydraConfig.get().runtime.output_dir
    writer = SummaryWriter(log_dir=log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_root_dir = Path(cfg.dataset_root_dir)
    dataset_split_dir = dataset_root_dir.joinpath(timestamp)
    share_dir = Path(cfg.share_dir).joinpath(timestamp)
    state_dir = Path(cfg.state_dir).joinpath(timestamp)

    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    logging.info(f"device: {device}")

    setup_reproducibility(cfg.seed)

    dataset = PartitionedCIFAR10(
        root=dataset_root_dir,
        path=dataset_split_dir,
        num_clients=cfg.num_clients,
        seed=cfg.seed,
        partition=cfg.partition,
        num_shards=cfg.num_shards,
        dir_alpha=cfg.dir_alpha,
    )
    model_selector = FedAvgModelSelector(num_classes=10, seed=cfg.seed)

    handler = FedAvgBaseServerHandler(
        model_selector=model_selector,
        model_name=cfg.model_name,
        dataset=dataset,
        global_round=cfg.global_round,
        num_clients=cfg.num_clients,
        device=device,
        sample_ratio=cfg.sample_ratio,
        batch_size=cfg.batch_size,
        seed=cfg.seed,
    )
    trainer: (
        FedAvgBaseClientTrainer
        | FedAvgProcessPoolClientTrainer
        | FedAvgThreadPoolClientTrainer
        | None
    ) = None
    match cfg.execution_mode:
        case "single-threaded":
            trainer = FedAvgBaseClientTrainer(
                model_selector=model_selector,
                model_name=cfg.model_name,
                dataset=dataset,
                device=device,
                num_clients=cfg.num_clients,
                epochs=cfg.epochs,
                lr=cfg.lr,
                batch_size=cfg.batch_size,
                seed=cfg.seed,
            )
        case "multi-process":
            trainer = FedAvgProcessPoolClientTrainer(
                model_selector=model_selector,
                model_name=cfg.model_name,
                dataset=dataset,
                share_dir=share_dir,
                state_dir=state_dir,
                seed=cfg.seed,
                device=device,
                num_clients=cfg.num_clients,
                epochs=cfg.epochs,
                lr=cfg.lr,
                batch_size=cfg.batch_size,
                num_parallels=cfg.num_parallels,
                ipc_mode=cfg.ipc_mode,
            )
        case "multi-threaded":
            trainer = FedAvgThreadPoolClientTrainer(
                model_selector=model_selector,
                model_name=cfg.model_name,
                dataset=dataset,
                seed=cfg.seed,
                device=device,
                num_clients=cfg.num_clients,
                epochs=cfg.epochs,
                lr=cfg.lr,
                batch_size=cfg.batch_size,
                num_parallels=cfg.num_parallels,
            )
        case _:
            raise ValueError(f"Invalid execution mode: {cfg.execution_mode}")
    pipeline = FedAvgPipeline(handler=handler, trainer=trainer, writer=writer)
    try:
        pipeline.main()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt")


if __name__ == "__main__":
    # NOTE: To use CUDA with multiprocessing, you must use the 'spawn' start method
    mp.set_start_method("spawn")

    main()
