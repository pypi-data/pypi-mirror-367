from tqdm.auto import tqdm
from adaptive_harmony import StringThread, DataSet, CosineScheduler, TrainingModel, Logger, JobNotifier, StageNotifier
from adaptive_harmony.core.utils import async_map_batch
from adaptive_harmony.metric_logger import StdoutLogger


class SFT:

    def __init__(
        self,
        dataset: list[StringThread],
        model: TrainingModel,
        logger: Logger = StdoutLogger(),
        stage_notifier: StageNotifier = JobNotifier().stage_notifier("SFT Training"),
        lr: float = 1e-5,
        samples_per_batch=512,  # axel magic number: "pretty well validated across different scales"
        max_grad_norm=1.0,
        epochs: int = 1,
    ):
        self.dataset = DataSet(dataset)
        self.lr_schedule = CosineScheduler(lr)
        self.model = model
        self.logger = logger
        self.stage_notifier = stage_notifier
        self.samples_per_batch = samples_per_batch
        self.max_grad_norm = max_grad_norm
        self.epochs = epochs

    @property
    def training_completion_percentage(self):
        return self.dataset.completion_percentage() / self.epochs

    async def run(self):
        with tqdm(total=100) as pbar:
            while self.training_completion_percentage < 1.0:
                self.stage_notifier.report_training_progress(
                    tot_num_samples=len(self.dataset) * self.epochs,
                    processed_num_samples=self.dataset.idx,
                    monitoring_link=self.logger.training_monitoring_link,
                )
                await async_map_batch(self.model.train_language_modelling, self.dataset, self.samples_per_batch)
                cp = self.training_completion_percentage
                current_lr = self.lr_schedule(cp)
                pbar.update(cp * 100.0 - pbar.n)

                logs = await self.model.optim_step(current_lr, wd=0, max_grad_norm=self.max_grad_norm)

                self.logger(logs | dict(completion_percentage=cp))
