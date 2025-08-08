#!/usr/bin/env python3
"""
Tanat runner core application.
"""

import logging

from pypassist.optional.runner.omegaconf import OmegaConf
from pypassist.runner.workflow.execution.dagster import DagsterWorkflow

from ..config import TanatRunnerConfig
from ..workenv.workenv import TanatWorkEnv
from ..utils import ASCII_ART

LOGGER = logging.getLogger(__name__)


def core_tanat_app(cfg):
    """TanaT application core function."""
    LOGGER.info(ASCII_ART)
    cfg = OmegaConf.to_container(cfg, resolve=True)
    app_cfg = TanatRunnerConfig(**cfg)
    tanat_wenv = TanatWorkEnv(app_cfg.workenv)
    workflow = DagsterWorkflow(app_cfg.workflow, tanat_wenv)
    result = workflow.execute()
    return result
