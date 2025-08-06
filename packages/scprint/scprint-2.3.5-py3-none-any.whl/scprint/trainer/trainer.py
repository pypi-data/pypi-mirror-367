from typing import List, Optional

from lightning.pytorch.callbacks import Callback


class TrainingMode(Callback):
    def __init__(
        self,
        do_denoise: bool = True,
        noise: List[float] = [0.6],
        do_cce: bool = False,
        cce_temp: float = 0.2,  # .6
        cce_scale: float = 0.1,  # .01
        do_ecs: bool = False,
        ecs_threshold: float = 0.4,
        class_embd_diss_scale: float = 0.1,
        ecs_scale: float = 0.1,  # .1
        do_mvc: bool = False,
        mvc_scale: float = 1.0,
        do_adv_cls: bool = False,
        do_next_tp: bool = False,
        do_generate: bool = True,
        class_scale: float = 1,
        mask_ratio: List[float | str] = [],  # 0.3
        test_every: int = 20,
        warmup_duration: int = 500,
        fused_adam: bool = False,
        adv_class_scale: float = 0.1,
        lr_reduce_patience: int = 2,
        lr_reduce_factor: float = 0.6,
        lr_reduce_monitor: str = "val_loss",
        do_cls: bool = True,
        do_adv_batch: bool = False,
        run_full_forward: bool = False,
        lr: float = 0.0001,
        dropout: float = 0.1,
        optim: str = "adamW",
        weight_decay: float = 0.01,
        zinb_and_mse: bool = False,
        var_context_length: bool = False,
        name="",
        set_step: Optional[int] = None,
    ):
        """
        TrainingMode a callback to set the training specific info to the model.

        This is because lightning is unfortunately setup this way. the model should be separated from training
        but at the same time it has training specific methods... so we have to do this.

        Args:
            do_denoise (bool): Whether to apply denoising during training. Defaults to True.
            noise (List[float]): List of noise levels to apply if denoising is enabled. Defaults to [0.6], meaning only one forward path with 60% of the counts being dropped will happen.
            do_cce (bool): Whether to apply the Contrastive Cell Embedding from scGPT during training. Defaults to False.
            cce_temp (float): Similarity threshold for CCE. Defaults to 0.5.
            cce_scale (float): Scaling factor for CCE loss. Defaults to 0.002.
            do_ecs (bool): Whether to apply the Elastic Cell Similarity loss from scGPT during training. Defaults to False.
            ecs_threshold (float): Threshold for ECS. Defaults to 0.3.
            ecs_scale (float): Scaling factor for ECS loss. Defaults to 0.05.
            do_mvc (bool): Whether to do the cell embedding generation with the scGPT's MVC loss. Defaults to False.
            mvc_scale (float): Scaling factor for MVC loss. Defaults to 1.0.
            do_adv_cls (bool): Whether to apply adversarial classification during training. Defaults to False.
            do_generate (bool): Whether to do the bottleneck learning task. Defaults to True.
            class_scale (float): Scaling factor for classification loss. Defaults to 1.5.
            mask_ratio (List[float]): List of mask ratios to apply during training. Defaults to [], meaning no masking is applied during pretraining.
            warmup_duration (int): Number of warmup steps for learning rate scheduling. Defaults to 500.
            fused_adam (bool): Whether to use fused Adam optimizer. Defaults to True.
            adv_class_scale (float): Scaling factor for adversarial classification loss. Defaults to 0.1.
            lr_reduce_patience (int): Number of epochs with no improvement after which learning rate will be reduced. Defaults to 1.
            lr_reduce_factor (float): Factor by which the learning rate will be reduced. Defaults to 0.6.
            lr_reduce_monitor (str): Quantity to be monitored for learning rate reduction. Defaults to "val_loss".
            do_cls (bool): Whether to perform classification during training. Defaults to True.
            do_adv_batch (bool): Whether to apply adversarial batch training. Defaults to False.
            run_full_forward (bool): Whether to run a second forward pass without masking or denoising for the bottleneck learning / MVC case. Defaults to False.
            lr (float): Initial learning rate. Defaults to 0.001.
            optim (str): Optimizer to use during training. Defaults to "adamW".
            weight_decay (float): Weight decay to apply during optimization. Defaults to 0.01.
            name (str): Name of the training mode. Defaults to an empty string. should be an ID for the model
            test_every (int): Number of epochs between testing. Defaults to 1.
            class_embd_diss_scale (float): Scaling factor for the class embedding dissimilarity loss. Defaults to 0.1.
            zinb_and_mse (bool): Whether to use ZINB and MSE loss. Defaults to False.
            var_context_length (bool): Whether to use variable context length. Defaults to False.
            dropout (float): Dropout rate for the model. Defaults to 0.1.
            set_step (int, optional): Set the global step for the model. Defaults to None.
        """
        super().__init__()
        self.do_denoise = do_denoise
        self.noise = noise
        self.do_cce = do_cce
        self.cce_temp = cce_temp
        self.cce_scale = cce_scale
        self.do_ecs = do_ecs
        self.ecs_threshold = ecs_threshold
        self.ecs_scale = ecs_scale
        self.do_mvc = do_mvc
        self.do_adv_cls = do_adv_cls
        self.do_next_tp = do_next_tp
        self.do_generate = do_generate
        self.class_scale = class_scale
        self.mask_ratio = mask_ratio
        self.warmup_duration = warmup_duration
        self.fused_adam = fused_adam
        self.mvc_scale = mvc_scale
        self.do_cls = do_cls
        self.adv_class_scale = adv_class_scale
        self.lr_reduce_patience = lr_reduce_patience
        self.lr_reduce_factor = lr_reduce_factor
        self.lr_reduce_monitor = lr_reduce_monitor
        self.lr = lr
        self.optim = optim
        self.weight_decay = weight_decay
        self.do_cls = do_cls
        self.do_adv_batch = do_adv_batch
        self.run_full_forward = run_full_forward
        self.name = name
        self.test_every = test_every
        self.class_embd_diss_scale = class_embd_diss_scale
        self.zinb_and_mse = zinb_and_mse
        self.var_context_length = var_context_length
        self.dropout = dropout
        self.set_step = set_step

    def __repr__(self):
        return (
            f"TrainingMode("
            f"do_denoise={self.do_denoise}, "
            f"noise={self.noise}, "
            f"do_cce={self.do_cce}, "
            f"cce_temp={self.cce_temp}, "
            f"cce_scale={self.cce_scale}, "
            f"do_ecs={self.do_ecs}, "
            f"ecs_threshold={self.ecs_threshold}, "
            f"ecs_scale={self.ecs_scale}, "
            f"do_mvc={self.do_mvc}, "
            f"lr={self.lr},"
            f"optim={self.optim},"
            f"weight_decay={self.weight_decay},"
            f"do_adv_cls={self.do_adv_cls}, "
            f"adv_class_scale={self.adv_class_scale}, "
            f"do_next_tp={self.do_next_tp}, "
            f"do_generate={self.do_generate}, "
            f"class_scale={self.class_scale}, "
            f"mask_ratio={self.mask_ratio}, "
            f"warmup_duration={self.warmup_duration}, "
            f"fused_adam={self.fused_adam}, "
            f"lr_reduce_patience={self.lr_reduce_patience}, "
            f"lr_reduce_factor={self.lr_reduce_factor}, "
            f"lr_reduce_monitor={self.lr_reduce_monitor}, "
            f"mvc_scale={self.mvc_scale}, "
            f"do_cls={self.do_cls}, "
            f"do_adv_batch={self.do_adv_batch}, "
            f"run_full_forward={self.run_full_forward}), "
            f"name={self.name}, "
            f"test_every={self.test_every}, "
            f"class_embd_diss_scale={self.class_embd_diss_scale}, "
            f"zinb_and_mse={self.zinb_and_mse}, "
            f"var_context_length={self.var_context_length}, "
            f"dropout={self.dropout}, "
            f"set_step={self.set_step})"
        )

    def setup(self, trainer, model, stage=None):
        # do something with all training_step outputs, for example:
        model.do_denoise = self.do_denoise
        model.noise = self.noise
        model.do_cce = self.do_cce
        model.cce_temp = self.cce_temp
        model.cce_scale = self.cce_scale
        model.do_ecs = self.do_ecs
        model.ecs_threshold = self.ecs_threshold
        model.ecs_scale = self.ecs_scale
        model.do_mvc = self.do_mvc
        model.do_adv_cls = self.do_adv_cls
        model.do_next_tp = self.do_next_tp
        model.class_scale = self.class_scale
        model.mask_ratio = self.mask_ratio
        model.warmup_duration = self.warmup_duration
        model.fused_adam = self.fused_adam
        model.do_generate = self.do_generate
        model.mvc_scale = self.mvc_scale
        model.do_cls = self.do_cls
        model.adv_class_scale = self.adv_class_scale
        model.lr_reduce_patience = self.lr_reduce_patience
        model.lr_reduce_factor = self.lr_reduce_factor
        model.lr_reduce_monitor = self.lr_reduce_monitor
        model.do_cls = self.do_cls
        model.do_adv_batch = self.do_adv_batch
        model.run_full_forward = self.run_full_forward
        model.lr = self.lr
        model.optim = self.optim
        model.weight_decay = self.weight_decay
        model.name = self.name
        model.test_every = self.test_every
        model.class_embd_diss_scale = self.class_embd_diss_scale
        model.zinb_and_mse = self.zinb_and_mse
        model.var_context_length = self.var_context_length
        model.dropout = self.dropout
        model.set_step = self.set_step
        # model.configure_optimizers()
