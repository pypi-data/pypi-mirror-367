#!/usr/bin/env python

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from torch import nn

from ..datasets.lerobot_dataset import LeRobotDatasetMetadata
from ..utils.dataset_utils import dataset_to_policy_features
from ..common.envs_config import EnvConfig

# from lerobot.common.envs.utils import env_to_policy_features
from .pretrained import PreTrainedPolicy

from .pi0.configuration_pi0 import PI0Config
from .smolvla.configuration_smolvla import SmolVLAConfig
from .pi0fast.configuration_pi0fast import PI0FASTConfig

from .pretrained import PreTrainedConfig
from ..params import FeatureType
from loguru import logger


def get_policy_class(name: str) -> PreTrainedPolicy:
    """Get the policy's class and config class given a name (matching the policy class' `name` attribute)."""
    if name == "tdmpc":
        return NotImplemented(f"{name} not supported yet.")
    elif name == "diffusion":
        return NotImplemented(f"{name} not supported yet.")
    elif name == "act":
        return NotImplemented(f"{name} not supported yet.")
    elif name == "vqbet":
        return NotImplemented(f"{name} not supported yet.")
    elif name == "pi0":
        from .pi0.modeling_pi0 import PI0Policy

        return PI0Policy
    elif name == "pi0fast":
        from .pi0fast.modeling_pi0fast import PI0FASTPolicy
        return PI0FASTPolicy
    elif name == "smolvla":
        from .smolvla.modeling_smolvla import SmolVLAPolicy

        return SmolVLAPolicy
    else:
        raise NotImplementedError(f"Policy with name {name} is not implemented.")


def make_policy_config(policy_type: str, **kwargs) -> PreTrainedConfig:
    if policy_type == "tdmpc":
        return NotImplemented(f"policy_type {policy_type} not supported yet.")
    elif policy_type == "diffusion":
        return NotImplemented(f"policy_type {policy_type} not supported yet.")
    elif policy_type == "act":
        return NotImplemented(f"policy_type {policy_type} not supported yet.")
    elif policy_type == "vqbet":
        return NotImplemented(f"policy_type {policy_type} not supported yet.")
    elif policy_type == "pi0":
        return PI0Config(**kwargs)
    elif policy_type == "pi0fast":
        return PI0FASTConfig(**kwargs)
    elif policy_type == "smolvla":
        return SmolVLAConfig(**kwargs)
    else:
        raise ValueError(f"Policy type '{policy_type}' is not available.")


def make_policy(
    cfg: PreTrainedConfig,
    ds_meta: LeRobotDatasetMetadata | None = None,
    env_cfg: EnvConfig | None = None,
) -> PreTrainedPolicy:
    """Make an instance of a policy class.

    This function exists because (for now) we need to parse features from either a dataset or an environment
    in order to properly dimension and instantiate a policy for that dataset or environment.

    Args:
        cfg (PreTrainedConfig): The config of the policy to make. If `pretrained_path` is set, the policy will
            be loaded with the weights from that path.
        ds_meta (LeRobotDatasetMetadata | None, optional): Dataset metadata to take input/output shapes and
            statistics to use for (un)normalization of inputs/outputs in the policy. Defaults to None.
        env_cfg (EnvConfig | None, optional): The config of a gym environment to parse features from. Must be
            provided if ds_meta is not. Defaults to None.

    Raises:
        ValueError: Either ds_meta or env and env_cfg must be provided.
        NotImplementedError: if the policy.type is 'vqbet' and the policy device 'mps' (due to an incompatibility)

    Returns:
        PreTrainedPolicy: _description_
    """
    # if bool(ds_meta) == bool(env_cfg):
    #     raise ValueError(
    #         "Either one of a dataset metadata or a sim env must be provided."
    #     )

    # NOTE: Currently, if you try to run vqbet with mps backend, you'll get this error.
    # TODO(aliberts, rcadene): Implement a check_backend_compatibility in policies?
    # NotImplementedError: The operator 'aten::unique_dim' is not currently implemented for the MPS device. If
    # you want this op to be added in priority during the prototype phase of this feature, please comment on
    # https://github.com/pytorch/pytorch/issues/77764. As a temporary fix, you can set the environment
    # variable `PYTORCH_ENABLE_MPS_FALLBACK=1` to use the CPU as a fallback for this op. WARNING: this will be
    # slower than running natively on MPS.
    if cfg.type == "vqbet" and cfg.device == "mps":
        raise NotImplementedError(
            "Current implementation of VQBeT does not support `mps` backend. "
            "Please use `cpu` or `cuda` backend."
        )

    policy_cls = get_policy_class(cfg.type)

    kwargs = {}
    if ds_meta is not None:
        features = dataset_to_policy_features(ds_meta.features)
        kwargs["dataset_stats"] = ds_meta.stats
        
        cfg.output_features = {
            key: ft for key, ft in features.items() if ft.type is FeatureType.ACTION
        }
        cfg.input_features = {
            key: ft for key, ft in features.items() if key not in cfg.output_features
        }
        kwargs["config"] = cfg
    else:
        if not cfg.pretrained_path:
            logging.warning(
                "You are instantiating a policy from scratch and its features are parsed from an environment "
                "rather than a dataset. Normalization modules inside the policy will have infinite values "
                "by default without stats from a dataset."
            )
        # features = env_to_policy_features(env_cfg)
        assert cfg.input_features is not None, f'{cfg} does contains input_features, ensure saved it when training'
        assert cfg.output_features is not None, f'{cfg} does contains output_features, ensure saved it when training'
                

    logger.info(f'cfg.pretrained_path: {cfg.pretrained_path}')
    # forcely set strict True, avoid miss params load
    kwargs['strict'] = True
    if cfg.pretrained_path:
        # Load a pretrained policy and override the config if needed (for example, if there are inference-time
        # hyperparameters that we want to vary).
        kwargs["pretrained_name_or_path"] = cfg.pretrained_path
        policy = policy_cls.from_pretrained(**kwargs)
    else:
        # Make a fresh policy.
        policy = policy_cls(**kwargs)

    policy.to(cfg.device)
    assert isinstance(policy, nn.Module)

    # policy = torch.compile(policy, mode="reduce-overhead")

    return policy
