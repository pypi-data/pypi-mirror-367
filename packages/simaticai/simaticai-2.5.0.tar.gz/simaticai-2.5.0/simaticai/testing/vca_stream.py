# Copyright (C) Siemens AG 2021. All Rights Reserved. Confidential.

import os
import datetime
import cv2
import numpy as np
import uuid
from pathlib import Path
from simaticai.testing.data_stream import DataStream

_supported_image_formats = ['BGR', 'BGR8', 'RGB', 'RGB8', 'BayerRG8', 'BayerGR8', 'BayerBG8', 'BayerGB8',
                            'Mono8', 'YUV422Packed', 'YUV422_YUYV_Packed']

class VCAStream(DataStream):
    """
    This class creates a generator from a folder of images.

    The generate function returns a generator that walks over the image folder and converts
    each image into the specified format, BayerRG8 by default. The resulting object is in the
    ImageSet format, as if it were received from AI Inference Server.
    """

    def __init__(self, data: os.PathLike, variable_name: str = 'vision_payload', image_format: str = 'BayerRG8', filter: str = None):
        """
        Creates a new VCAStream object

        Args:
            data (os.Pathlike): Path to the directory of images
            variable_name (str): Name of the variable to store the images (default: 'vision_payload')
            image_format (str): Supported image formats: 'BGR' (equivalently: 'BGR8'), 'RGB' (equivalently: 'RGB8'), 'BayerRG8' (default),
                'BayerGR8', 'BayerBG8', 'BayerGB8', 'Mono8', 'YUV422Packed', 'YUV422_YUYV_Packed'
            filter (rglob_pattern): Pattern to filter the images (see also: pathlib.rglob())
        """
        self.seq = 0
        self.data = data
        if filter is None or "" == filter.strip():
            self.filter = "**/*.[jJpP][pPnN][gGeE]*"
        else:
            self.filter = filter
        if variable_name is None or "" == variable_name.strip():
            self.variable_name = 'vision_payload'
        else:
            self.variable_name = variable_name
        if image_format is None:
            image_format = 'BayerRG8'
        elif image_format not in _supported_image_formats:
            raise AssertionError(f'ERROR Provided image format is not supported. image_format must be one of {_supported_image_formats}')
        self.image_format = image_format
        self.camera_id = uuid.uuid4()

    def __iter__(self):
        """
        Creates the input data generator.

        Walks recursively the image folder and converts each image into an ImageSet variable.

        Returns: a generator
        """
        for image_path in Path(self.data).rglob(self.filter):
            yield self._create_imageset(image_path)

    @staticmethod
    def _bgr_to_bayer(bgr_image: np.ndarray, bayer_order: str) -> np.ndarray:
        (height, width) = bgr_image.shape[:2]
        bayer_image = np.zeros((height, width), dtype=np.uint8)

        BLUE, GREEN, RED = 0, 1, 2
        match bayer_order:
            case 'BayerRG8':
                channels = (RED, GREEN, GREEN, BLUE)
            case 'BayerGR8':
                channels = (GREEN, RED, BLUE, GREEN)
            case 'BayerBG8':
                channels = (BLUE, GREEN, GREEN, RED)
            case 'BayerGB8':
                channels = (GREEN, BLUE, RED, GREEN)
            case _:
                raise ValueError(f"Unsupported bayer order: {bayer_order}")

        top_left_ch, top_right_ch, bottom_left_ch, bottom_right_ch = channels
        bayer_image[0::2, 0::2] = bgr_image[0::2, 0::2, top_left_ch]
        bayer_image[0::2, 1::2] = bgr_image[0::2, 1::2, top_right_ch]
        bayer_image[1::2, 0::2] = bgr_image[1::2, 0::2, bottom_left_ch]
        bayer_image[1::2, 1::2] = bgr_image[1::2, 1::2, bottom_right_ch]
        return bayer_image

    @staticmethod
    def convert_image_from_BGR(bgr_image: np.ndarray, target_format: str) -> tuple[bytes, int, int]:
        match target_format:
            case "BGR" | "BGR8":
                res_image = bgr_image
            case "RGB" | "RGB8":
                res_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
            case "Mono8":
                res_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            case "BayerRG8":
                res_image = VCAStream._bgr_to_bayer(bgr_image, "BayerRG8")
            case "BayerGR8":
                res_image = VCAStream._bgr_to_bayer(bgr_image, "BayerGR8")
            case "BayerBG8":
                res_image = VCAStream._bgr_to_bayer(bgr_image, "BayerBG8")
            case "BayerGB8":
                res_image = VCAStream._bgr_to_bayer(bgr_image, "BayerGB8")
            case "YUV422Packed":
                # COLOR_BGR2YUV_Y422 is the 4:2:2 sampling format of YUV, with coefficients correspond to the BT.601 standard.
                # After ravel() it becomes a packed format, where the order of the channels is UYVY.
                res_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2YUV_Y422)
            case "YUV422_YUYV_Packed":
                # Same as the above but with YUYV order.
                res_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2YUV_YUYV)
            case _:
                raise ValueError(f"Unsupported target format: {target_format}")
        height, width = res_image.shape[:2]
        res_image = res_image.ravel().tobytes()
        return res_image, height, width

    def _create_imageset(self, image_path):
        timestamp = f"{datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
        bgr_image = cv2.imread(str(image_path))
        image_array, height, width = VCAStream.convert_image_from_BGR(bgr_image, self.image_format)
        result = {
            self.variable_name: {
                'version': '1',
                'cameraid': str(self.camera_id),
                'timestamp': timestamp,
                'customfields': '',
                'detail': [{
                    'id': f'VCA Stream : {image_path}',
                    'seq': self.seq,
                    'timestamp': timestamp,
                    'format': self.image_format,
                    'width': width,
                    'height': height,
                    'metadata': '{"ptpstatus":"Disabled","ptptimestamp":"0"}',
                    'image': image_array,
                }]}
        }
        self.seq += 1
        return result
