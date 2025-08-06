import json
import logging
import unittest
from typing import Optional

import torch
from parameterized import parameterized

from birder.data.collators.detection import batch_images
from birder.model_registry import registry
from birder.net.detection import base

logging.disable(logging.CRITICAL)


class TestBase(unittest.TestCase):
    def test_get_signature(self) -> None:
        signature = base.get_detection_signature((1, 3, 224, 224), 10, dynamic=False)
        self.assertIn("dynamic", signature)
        self.assertIn("inputs", signature)
        self.assertIn("outputs", signature)
        self.assertIn("boxes", signature["outputs"][0][0])


class TestNetDetection(unittest.TestCase):
    @parameterized.expand(  # type: ignore[misc]
        [
            ("deformable_detr", None, ("fasternet_t0", None)),
            ("deformable_detr", None, ("efficientvit_msft_m0", None)),  # 3 stage network
            ("deformable_detr_boxref", None, ("regnet_x_200m", None)),
            ("detr", None, ("regnet_y_1_6g", None)),
            ("efficientdet_d0", None, ("efficientnet_v1_b0", None)),
            ("faster_rcnn", None, ("resnet_v2_18", None)),
            ("faster_rcnn", None, ("efficientvit_msft_m0", None)),  # 3 stage network
            ("fcos", None, ("tiny_vit_5m", None)),
            ("fcos", None, ("vit_s32", None)),  # 1 stage network
            ("retinanet", None, ("mobilenet_v3_small", 1)),
            ("retinanet", None, ("efficientvit_msft_m0", None)),  # 3 stage network
            ("retinanet_sfp", None, ("vit_det_m16_rms", None)),
            ("ssd", None, ("efficientnet_v2_s", None)),
            ("ssd", None, ("vit_s16", None)),  # 1 stage network
            ("ssdlite", None, ("mobilenet_v2", 1), (512, 512)),
            ("ssdlite", None, ("vit_t16", None)),  # 1 stage network
            ("vitdet", None, ("vit_sam_b16", None)),
        ]
    )
    def test_net_detection(
        self,
        network_name: str,
        net_param: Optional[float],
        encoder: tuple[str, float],
        size: tuple[int, int] = (256, 256),
    ) -> None:
        backbone = registry.net_factory(encoder[0], 3, 10, net_param=encoder[1])
        n = registry.detection_net_factory(network_name, 10, backbone, net_param=net_param, size=size)
        backbone.adjust_size(size)

        # Ensure config is serializable
        _ = json.dumps(n.config)

        # Test network
        n.eval()
        out = n(torch.rand((1, 3, *size)))
        (detections, losses) = out
        self.assertEqual(len(losses), 0)
        for detection in detections:
            for key in ["boxes", "labels", "scores"]:
                self.assertFalse(torch.isnan(detection[key]).any())

        # Again in "dynamic size" mode
        (images, masks, image_sizes) = batch_images(
            [torch.rand((3, *size)), torch.rand((3, size[0] - 12, size[1] - 24))], size_divisible=4
        )
        out = n(images, masks=masks, image_sizes=image_sizes)

        # Reset classifier
        n.reset_classifier(20)
        n(torch.rand((1, 3, *size)))

        n.train()
        out = n(
            torch.rand((1, 3, *size)),
            targets=[
                {
                    "boxes": torch.tensor([[10.1, 10.1, 30.2, 40.2]]),
                    "labels": torch.tensor([1]),
                }
            ],
        )
        (detections, losses) = out
        self.assertGreater(len(losses), 0)
        for loss in losses.values():
            self.assertFalse(torch.isnan(loss).any())

        loss = sum(v for v in losses.values())
        self.assertEqual(loss.ndim, 0)

        for detection in detections:
            for key in ["boxes", "labels", "scores"]:
                self.assertFalse(torch.isnan(detection[key]).any())

        if n.scriptable is True:
            torch.jit.script(n)
        else:
            n.eval()
            torch.jit.trace(n, example_inputs=torch.rand((1, 3, *size)))
            n.train()

        # Freeze
        n.eval()
        n.freeze(freeze_classifier=False)
        n(torch.rand((1, 3, *size)))
