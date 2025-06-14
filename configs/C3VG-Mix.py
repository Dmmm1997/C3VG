_base_ = [
    "./_base_/datasets/segmentation/mixed-seg_nogoogle.py",
    "./_base_/misc.py",
]
dataset = "MixedSeg"
max_token = 20
img_size = 320
patch_size = 16

img_norm_cfg = dict(mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375])

train_pipeline = [
    dict(
        type="LoadImageAnnotationsFromFile",
        max_token=max_token,
        with_mask=True,
        with_bbox=True,
        dataset=dataset,
        use_token_type="beit3",
    ),
    dict(type="LargeScaleJitter", out_max_size=img_size, jitter_min=0.3, jitter_max=1.4),
    dict(type="Resize", img_scale=(img_size, img_size), keep_ratio=False),
    dict(type="Normalize", **img_norm_cfg),
    dict(type="Pad", size_divisor=32),
    # dict(type='SampleMaskVertices', num_ray=18, center_sampling=False),
    # dict(type='Pad', pad_to_square=True),
    dict(type="DefaultFormatBundle"),
    dict(
        type="CollectData",
        keys=["img", "ref_expr_inds", "text_attention_mask", "is_crowd", "gt_mask_rle", "gt_bbox"],
    ),
]

val_pipeline = [
    dict(
        type="LoadImageAnnotationsFromFile",
        max_token=max_token,
        with_mask=True,
        with_bbox=True,
        dataset=dataset,
        use_token_type="beit3",
    ),
    dict(type="Resize", img_scale=(img_size, img_size), keep_ratio=False),
    dict(type="Normalize", **img_norm_cfg),
    dict(type="Pad", size_divisor=32),
    # dict(type='Pad', pad_to_square=True),
    dict(type="DefaultFormatBundle"),
    dict(
        type="CollectData",
        keys=["img", "ref_expr_inds", "text_attention_mask", "is_crowd", "gt_mask_rle", "gt_bbox"],
    ),
]
test_pipeline = val_pipeline.copy()

data = dict(
    samples_per_gpu=16,
    workers_per_gpu=4,
    train=dict(
        pipeline=train_pipeline,
    ),
    val_refcoco_unc=dict(
        pipeline=val_pipeline,
    ),
    testA_refcoco_unc=dict(
        pipeline=val_pipeline,
    ),
    testB_refcoco_unc=dict(
        pipeline=val_pipeline,
    ),
    val_refcocoplus_unc=dict(
        pipeline=test_pipeline,
    ),
    testA_refcocoplus_unc=dict(
        pipeline=test_pipeline,
    ),
    testB_refcocoplus_unc=dict(
        pipeline=test_pipeline,
    ),
    val_refcocog_umd=dict(
        pipeline=test_pipeline,
    ),
    test_refcocog_umd=dict(
        pipeline=test_pipeline,
    ),
)

model = dict(
    type="MIXUniModel",
    vis_enc=dict(
        type="BEIT3",
        img_size=img_size,
        patch_size=patch_size,
        vit_type="base",
        drop_path_rate=0.1,
        vocab_size=64010,
        freeze_layer=-1,
        vision_embed_proj_interpolate=False,
        pretrain="pretrain_weights/beit3_base_patch16_224.zip",
    ),
    lan_enc=None,
    fusion=None,
    head=dict(
        type="UniHeadCoarseToFine",
        input_channels=768,
        hidden_channels=256,
        loss_weight={
            "mask": {"dice": 1.0, "bce": 1.0},
            "bbox": 0.05,
            "clip": {"box": 0, "seg": 0, "pixel": True},
            "boxsegcc": {"S2B": 0.3, "B2S": 0.1, "cem": 0.0},
            "stage": {"first": 0.3, "second": 1.0},
        },
        query_augment={"num_queries":1},
        threshold={"B2S": 0.5, "S2B": 0.5},
        decoder_upsample_type="fpn",
        start_epoch=-1,
        uim={"enable": True, "weighted_compose": "boxmask", "enable_box_coorinate_embed": True, "box_weights": [0.1, 1.0]},
    ),
)

grad_norm_clip = 0.15
use_fp16 = False
ema = False
# work_dir = "work_dir/seqtr_det_refcoco-unc_pvtv2mmb1_mix_type1_detectionpretrain_nofreeze_fusionv3_lr0.0003_ema_ep30"
# work_dir = "work_dir/paper_exp/decoder_ablation/ViTBaseP32-1.0decoder-40ep-512hw-refcocounc"

lr = 0.0005
optimizer_config = dict(
    type="Adam",
    lr=lr,
    lr_vis_enc=lr / 10.0,
    lr_lan_enc=lr,
    betas=(0.9, 0.98),
    eps=1e-9,
    weight_decay=0,
    amsgrad=True,
)

scheduler_config = dict(
    type="MultiStepLRWarmUp",
    warmup_epochs=3,
    decay_steps=[25],
    decay_ratio=0.1,
    max_epoch=30,
)

log_interval = 50
threshold = 0.5
seed = 1234