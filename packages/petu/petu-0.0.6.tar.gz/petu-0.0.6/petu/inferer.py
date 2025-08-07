from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import torch
from loguru import logger

from petu.data_handler import DataHandler
from petu.model_handler import ModelHandler
from petu.utils.citation_reminder import citation_reminder


class Inferer:

    def __init__(
        self,
        device: Optional[str] = "cuda",
        cuda_visible_devices: Optional[str] = "0",
    ) -> None:
        """
        Initialize the Inferer class.

        Args:
            device (Optional[str], optional): torch device string. Defaults to "cuda".
            cuda_visible_devices (Optional[str], optional): CUDA_VISIBLE_DEVICES environment variable. Defaults to "0".
        """
        self.device = self._configure_device(
            requested_device=device,
            cuda_visible_devices=cuda_visible_devices,
        )
        self.data_handler = DataHandler()
        self.model_handler = ModelHandler(device=self.device)

    def _configure_device(
        self, requested_device: str, cuda_visible_devices: str
    ) -> torch.device:
        """Configure the device for inference based on the specified config.device.

        Args:
            requested_device (str): Requested device.
            cuda_visible_devices (str): CUDA_VISIBLE_DEVICES environment variable.

        Returns:
            torch.device: Configured device.
        """
        device = torch.device(requested_device)
        if device.type == "cuda":
            # The env vars have to be set before the first call to torch.cuda, else torch will always attempt to use the first device
            os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
            os.environ["CUDA_VISIBLE_DEVICES"] = cuda_visible_devices
            if torch.cuda.is_available():
                # clean memory
                torch.cuda.empty_cache()

        logger.info(f"Set torch device: {device}")

        return device

    @citation_reminder
    def infer(
        self,
        t1c: Optional[str | Path | np.ndarray] = None,
        fla: Optional[str | Path | np.ndarray] = None,
        t1: Optional[str | Path | np.ndarray] = None,
        t2: Optional[str | Path | np.ndarray] = None,
        ET_segmentation_file: Optional[str | Path] = None,
        CC_segmentation_file: Optional[str | Path] = None,
        T2H_segmentation_file: Optional[str | Path] = None,
        et_dust_threshold: int = 0,
        et_dust_connectivity: int = 26,
        cc_dust_threshold: int = 0,
        cc_dust_connectivity: int = 26,
        t2h_dust_threshold: int = 0,
        t2h_dust_connectivity: int = 26,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Infer segmentations based on provided images.

        Args:
            t1c (Optional[str  |  Path  |  np.ndarray], optional): T1C image. Defaults to None.
            fla (Optional[str  |  Path  |  np.ndarray], optional): FLAIR image. Defaults to None.
            t1 (Optional[str  |  Path  |  np.ndarray], optional): T1 image. Defaults to None.
            t2 (Optional[str  |  Path  |  np.ndarray], optional): T2 image. Defaults to None.
            ET_segmentation_file (Optional[str  |  Path], optional): Path to save ET segmentation. Defaults to None.
            CC_segmentation_file (Optional[str  |  Path], optional): Path to save CC segmentation. Defaults to None.
            T2H_segmentation_file (Optional[str  |  Path], optional): Path to save T2H segmentation. Defaults to None.
            et_dust_threshold (int, optional): Minimum size of connected components to keep for ET. Defaults to 0.
            et_dust_connectivity (int, optional): Connectivity for connected component analysis for ET. Defaults to 26. Reference: https://en.wikipedia.org/wiki/Pixel_connectivity
            cc_dust_threshold (int, optional): Minimum size of connected components to keep for CC. Defaults to 0.
            cc_dust_connectivity (int, optional): Connectivity for connected component analysis for CC. Defaults to 26. Reference: https://en.wikipedia.org/wiki/Pixel_connectivity
            t2h_dust_threshold (int, optional): Minimum size of connected components to keep for T2H. Defaults to 0.
            t2h_dust_connectivity (int, optional): Connectivity for connected component analysis for T2H. Defaults to 26. Reference: https://en.wikipedia.org/wiki/Pixel_connectivity

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: Tuple of segmentations: (ET, CC, T2H) as numpy arrays.
        """

        # check inputs and get mode , if mode == prev mode => run inference, else load new model
        validated_images = self.data_handler.validate_images(
            t1=t1, t1c=t1c, t2=t2, fla=fla
        )
        determined_inference_mode = self.data_handler.determine_inference_mode(
            images=validated_images
        )

        self.model_handler.load_model(
            inference_mode=determined_inference_mode,
        )

        with tempfile.TemporaryDirectory() as tmpdir:

            input_file_paths = self.data_handler.get_input_file_paths(
                images=validated_images,
                tmp_folder=Path(tmpdir),
            )

            logger.info(f"Running inference on device: {self.device}")
            np_results = self.model_handler.infer(
                input_file_paths=input_file_paths,
                ET_segmentation_file=ET_segmentation_file,
                CC_segmentation_file=CC_segmentation_file,
                T2H_segmentation_file=T2H_segmentation_file,
                et_dust_threshold=et_dust_threshold,
                et_dust_connectivity=et_dust_connectivity,
                cc_dust_threshold=cc_dust_threshold,
                cc_dust_connectivity=cc_dust_connectivity,
                t2h_dust_threshold=t2h_dust_threshold,
                t2h_dust_connectivity=t2h_dust_connectivity,
            )
            logger.info(f"Finished inference")
            return np_results
