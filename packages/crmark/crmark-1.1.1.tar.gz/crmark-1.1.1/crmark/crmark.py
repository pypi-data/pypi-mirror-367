# Copyright (c) 2025 chenoly@outlook.com. Licensed under MIT.
import os
import torch
import random
import platform
import requests
import numpy as np
from PIL import Image
from tqdm import tqdm
from numpy import ndarray
from crmark.nets import Model
from torchvision import transforms
from typing import Tuple, Union, Any
from crmark.compressor.rdh import CustomRDH
from crmark.compressor.utils import sha256_of_image_array
from crmark.compressor.utils_compressors import TensorCoder
from crmark.compressor.utils import sha256_to_bitstream, BCH
import warnings

warnings.filterwarnings("ignore")

__all__ = ["CRMark"]

_gray_512_256_MODEL_URL = "https://github.com/chenoly/CRMark/releases/download/v1.0/crmark_gray_size_512_bit_256.pth"
_color_256_64_MODEL_URL = "https://github.com/chenoly/CRMark/releases/download/v1.0/crmark_color_size_256_bit_64.pth"
_color_256_64_complex_MODEL_URL = "https://github.com/chenoly/CRMark/releases/download/v1.0/crmark_color_size_256_bit_64_complex.pth"


def _download_from_github_release(url: str, save_path: str) -> bool:
    """
    Download a file from a GitHub release URL, saving only if complete.

    Parameters:
        url (str): URL of the file to download (e.g., model weights file).
        save_path (str): Local path to save the downloaded file.

    Returns:
        bool: True if download and save are successful, False otherwise.
    """
    temp_path = None
    file_handle = None
    try:
        print("download:", url)
        headers = {"Authorization": f"token {os.getenv('GITHUB_TOKEN', '')}"}
        response = requests.get(url, stream=True, allow_redirects=True, headers=headers, timeout=30)

        if response.status_code != 200:
            print(f"Failed to download from {url}. Status code: {response.status_code}")
            print(f"\nPlease manually download the file from:\n{url} \nand place it in: {os.path.dirname(save_path)}")
            return False

        total_size = int(response.headers.get('content-length', 0))
        if total_size < 1024:
            print(f"Expected file size too small: {total_size} bytes")
            return False

        temp_path = save_path + '.tmp'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(temp_path, 'wb') as file_handle:
            with tqdm(
                    desc=save_path,
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    file_handle.write(data)
                    bar.update(len(data))

        downloaded_size = os.path.getsize(temp_path)
        if downloaded_size != total_size:
            print(f"Incomplete download. Downloaded: {downloaded_size} bytes, expected: {total_size} bytes")
            return False

        os.rename(temp_path, save_path)
        print(f"Successfully downloaded and saved to {save_path}")
        return True

    except (requests.RequestException, KeyboardInterrupt) as e:
        print(f"Download failed or interrupted: {e}")
        print(f"\nPlease manually download the file from:\n{url}\nand place it in:\n{os.path.dirname(save_path)}")
        return False

    finally:
        if file_handle is not None:
            try:
                file_handle.close()
            except Exception as e:
                print(f"Failed to close file handle: {e}")

        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                print(f"Cleaned up temporary file: {temp_path}")
            except OSError as e:
                print(f"Failed to delete temporary file {temp_path}: {e}")


def _download_models(model_mode):
    """
    Download pre-trained model weights for the specified color mode if not already cached.

    Parameters:
        model_mode (str): The image mode ("gray" for grayscale, "color" for RGB).

    Returns:
        None: The function downloads and caches the model weights if necessary.
    """
    if platform.system() == "Windows":
        base_cache_dir = os.path.join(os.environ["USERPROFILE"], ".cache", "crmark")
    else:
        base_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "crmark")
    os.makedirs(base_cache_dir, exist_ok=True)

    if model_mode == "gray_512_256":
        gray_model_path = os.path.join(base_cache_dir, "crmark_gray_size_512_bit_256.pth")
        if not os.path.exists(gray_model_path):
            _download_from_github_release(_gray_512_256_MODEL_URL, gray_model_path)

    if model_mode == "color_256_64":
        model_model_path = os.path.join(base_cache_dir, "crmark_color_size_256_bit_64.pth")
        if not os.path.exists(model_model_path):
            _download_from_github_release(_color_256_64_MODEL_URL, model_model_path)

    if model_mode == "color_256_64_complex":
        model_model_path = os.path.join(base_cache_dir, "crmark_color_size_256_bit_64_complex.pth")
        if not os.path.exists(model_model_path):
            _download_from_github_release(_color_256_64_complex_MODEL_URL, model_model_path)


class CRMark(object):
    """
    A class for reversible image watermarking using integer invertible flow and reversible data hiding (RDH).

    This class supports encoding a message or binary watermark into an image and recovering both the
    original image and the watermark. It supports grayscale and color images with pre-trained models.
    """

    def __init__(self, model_mode="color_256_64_complex", model_path: str = None, level_bits_len=10, freq_bits_len=32,
                 device="cpu", float64=False):
        """
        Initialize the CRMark instance with the specified configuration.

        Parameters:
            model_mode (str): The model variant to use. Must be one of:
                - "color_256_64": For RGB images, embeds 64 bits total, allowing 5 characters (24 bits) after BCH coding.
                - "gray_512_256": For grayscale images, embeds 256 bits total, allowing 20 characters (160 bits) after BCH coding.
            model_path (str): the pretrained model path for load. Default is None.
            level_bits_len (int): Number of bits allocated to encode the "level" component during tensor quantization,
                which represents the offset of overflow pixels. For example, if there are N distinct overflow values,
                `level_bits_len` should satisfy 2^level_bits_len >= N. A value of 10 allows up to 1024 levels.
                Default is 10.
            freq_bits_len (int): Number of bits used to encode each variable in the latent variable z.
                Larger values allow higher precision and support larger perturbations in z,
                but increase the auxiliary bitstream length. Use smaller values for common distortions;
                increase for complex distortion. Default is 20.
            device (str): The device used for computation, e.g., "cpu" or "cuda". Default is "cpu".
            float64 (bool): If True, uses float64 precision; otherwise, uses float32. Default is False.

        Returns:
            None: This constructor loads the appropriate model weights and prepares the instance for encoding/decoding.

        Raises:
            AssertionError: If the given model_mode is not one of the supported options.
        """
        assert model_mode in ["color_256_64_complex", "color_256_64",
                              "gray_512_256"], "model_mode must be 'color_256_64_complex', 'color_256_64' or 'gray_512_256'"

        self.k = None
        self.fc = None
        self.rdh = None
        self.iIWN = None
        self.device = device
        self.float64 = float64
        self.img_size = None
        self.bit_length = None
        self.model_mode = model_mode
        if model_mode in ["color_256_64", "color_256_64_complex"]:
            self.channel_dim = 3
            BCH_POLYNOMIAL_ = 137
            BCH_BITS_ = 3
        else:
            self.channel_dim = 1
            BCH_POLYNOMIAL_ = 501
            BCH_BITS_ = 12

        self.tensorcoder = None
        self.model_mode = model_mode
        self.net_min_size = None
        self.freq_bits_len = freq_bits_len
        self.level_bits_len = level_bits_len
        self.bch = BCH(BCH_POLYNOMIAL_, BCH_BITS_)
        self.transform = transforms.Compose([transforms.ToTensor()])

        if platform.system() == "Windows":
            base_cache_dir = os.path.join(os.environ["USERPROFILE"], ".cache", "crmark")
        else:
            base_cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "crmark")
        os.makedirs(base_cache_dir, exist_ok=True)

        gray_model_path = os.path.join(base_cache_dir, "crmark_gray_size_512_bit_256.pth")
        color_256_64_model_path = os.path.join(base_cache_dir, "crmark_color_size_256_bit_64.pth")
        color_256_64_complex_model_path = os.path.join(base_cache_dir, "crmark_color_size_256_bit_64_complex.pth")

        if model_path is None:
            _download_models(model_mode)
            if model_mode == "color_256_64":
                self.load_model(color_256_64_model_path)
            elif model_mode == "gray_512_256":
                self.load_model(gray_model_path)
            else:
                self.load_model(color_256_64_complex_model_path)
        else:
            self.load_model(model_path)

    def load_model(self, model_path: str):
        """
        Load pre-trained model weights and configure the watermarking model.

        Parameters:
            model_path (str): Path to the pre-trained model weights file.

        Returns:
            None: Configures the model and related components.
        """
        load_dict = torch.load(model_path, map_location="cpu", weights_only=False)

        self.k = load_dict['param_dict']['k']
        self.net_min_size = load_dict['param_dict']['min_size']
        self.fc = load_dict['param_dict']['fc']
        self.bit_length = load_dict['param_dict']['bit_length']
        self.img_size = load_dict['param_dict']['img_size']
        self.channel_dim = load_dict['param_dict']['channel_dim']

        if self.float64:
            torch.set_default_dtype(torch.float64)

        self.rdh = CustomRDH((self.img_size, self.img_size, self.channel_dim), self.device)

        self.tensorcoder = TensorCoder(
            (self.img_size, self.img_size, self.channel_dim),
            (1, self.bit_length),
            self.level_bits_len,
            self.freq_bits_len
        )

        self.iIWN = Model(self.img_size, self.channel_dim, self.bit_length, self.k, self.net_min_size, self.fc)
        self.iIWN.load_state_dict(load_dict['model_state_dict'])
        self.iIWN.to(self.device)
        self.iIWN.eval()

    def encode(self, cover_img: ndarray, message: str) -> Tuple[bool, Any]:
        """
        Embed a text message into an image as a watermark.

        Parameters:
            cover_img (ndarray): The cover image in which the message will be embedded.
            message (str): The text message to embed.
                           The required message length depends on the model's mode:
                               - "color_256_64": message length must be 5
                               - "gray_512_256": message length must be 20

        Returns:
            Tuple[bool, PIL.Image or None]:
                - (True, PIL.Image):
                    Embedding succeeded. The returned image is the final stego image
                    that contains both the watermark and the auxiliary information
                    (used for recovery) embedded via reversible data hiding (RDH).
                - (False, None):
                    otherwise. No meaningful image can be returned.
        """
        cover_img = np.uint8(cover_img)

        if self.model_mode in ["color_256_64", "color_256_64_complex"]:
            assert len(message) == 5 and cover_img.ndim == 3, \
                "For color_256_64 model, the image size should be (256, 256, 3), the message length should be 5 and image must be RGB"
        if self.model_mode == "gray_512_256":
            assert len(message) == 20 and cover_img.ndim == 2, \
                "For gray_512_256 model, the image size should be (512, 512), the message length should be 20 and image must be grayscale"

        cover_img_hash = sha256_of_image_array(cover_img)
        cover_img_hash_bitstream = sha256_to_bitstream(cover_img_hash)

        cover_img_tensor = self.transform(cover_img).unsqueeze(0).to(self.device)

        watermark = self.bch.Encode(message)
        watermark += [random.randint(0, 1) for _ in range(self.bit_length - len(watermark))]
        secret_tensor = torch.as_tensor(watermark, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            if self.float64:
                cover_img_tensor = cover_img_tensor.to(torch.float64)
                secret_tensor = secret_tensor.to(torch.float64)
            overflow_stego, z = self.iIWN.forward(cover_img_tensor, secret_tensor, True, False)

        stego_255 = torch.round(overflow_stego * 255.)
        z_round = torch.round(z)

        iscompressok, clip_stego_img, auxbits = self.tensorcoder.compress(stego_255, z_round)

        if iscompressok:
            issuccessful, rdh_stego_img = self.rdh.embed(clip_stego_img, auxbits + cover_img_hash_bitstream)
            if issuccessful:
                return issuccessful, Image.fromarray(np.uint8(rdh_stego_img))
        return False, None

    def recover(self, stego_img: ndarray) -> Union[Tuple[bool, Any, Any], Tuple[bool, None, None]]:
        """
        Recovers the original image and embedded message from a stego image.

        The method first attempts to extract auxiliary data (e.g., compressed features and hash)
        using RDH. If integrity verification passes (hash match), it returns the successfully
        recovered image and decoded message with `is_attacked = False`.

        If extraction or decompression fails, or the image has been tampered with,
        it falls back to a blind recovery using random noise, returning `is_attacked = True`
        along with best-effort results.

        Returns:
            Tuple[bool, PIL.Image or None, str or list or None]:
                - is_attacked (bool):
                    False if no attack detected and full recovery succeeded.
                    True if attack detected or recovery failed, indicating unreliable outputs.
                - recovered_image (PIL.Image): The reconstructed cover image.
                - recovered_message (str): The decoded watermark message (after BCH decoding).
        """
        stego_img = np.uint8(stego_img)

        issuccessful, clipped_stego_img, ext_auxbits = self.rdh.extract(stego_img)
        if issuccessful:
            cover_img_hash_bitstream = ext_auxbits[-256:]
            isdecompressok, rec_overflow_stego, rec_z = self.tensorcoder.decompress(clipped_stego_img,
                                                                                    ext_auxbits[:-256])
            if isdecompressok:
                with torch.no_grad():
                    if self.float64:
                        rec_z = rec_z.to(torch.float64)
                        rec_overflow_stego = rec_overflow_stego.to(torch.float64)
                    rec_cover_tensor, rec_watermark = self.iIWN.forward(rec_overflow_stego / 255., rec_z, True, True)

                if rec_cover_tensor.shape[1] == 1:
                    rec_cover = torch.round(rec_cover_tensor * 255.)[0][0].detach().cpu().numpy()
                else:
                    rec_cover = torch.round(rec_cover_tensor * 255.)[0].permute(1, 2, 0).detach().cpu().numpy()
                rec_cover = np.uint8(np.clip(rec_cover, 0, 255))

                rec_cover_img_hash = sha256_of_image_array(rec_cover)
                rec_cover_img_hash_bitstream = sha256_to_bitstream(rec_cover_img_hash)

                rec_watermark = torch.round(torch.clip(rec_watermark, 0., 1.))
                rec_watermark = rec_watermark[0].detach().cpu().numpy().astype(int).tolist()
                valid_part = rec_watermark[:(len(rec_watermark) // 8) * 8]

                if np.array_equal(rec_cover_img_hash_bitstream, cover_img_hash_bitstream):
                    isdecode, decoded_data = self.bch.Decode(valid_part)
                    return False, Image.fromarray(rec_cover), decoded_data

        stego_img_tensor = self.transform(stego_img).unsqueeze(0).to(self.device)
        sampled_z = torch.randn(size=(1, self.bit_length)).to(self.device)
        with torch.no_grad():
            if self.float64:
                sampled_z = sampled_z.to(torch.float64)
                stego_img_tensor = stego_img_tensor.to(torch.float64)
            rec_cover_tensor, rec_watermark = self.iIWN.forward(stego_img_tensor, sampled_z, True, True)
        if rec_cover_tensor.shape[1] == 1:
            rec_cover = torch.round(rec_cover_tensor * 255.)[0][0].detach().cpu().numpy()
        else:
            rec_cover = torch.round(rec_cover_tensor * 255.)[0].permute(1, 2, 0).detach().cpu().numpy()
        rec_cover = np.uint8(np.clip(rec_cover, 0, 255))
        rec_watermark = torch.round(torch.clip(rec_watermark, 0., 1.))
        rec_watermark = rec_watermark[0].detach().cpu().numpy().astype(int).tolist()
        valid_part = rec_watermark[:(len(rec_watermark) // 8) * 8]
        isdecode, decoded_data = self.bch.Decode(valid_part)
        return True, Image.fromarray(rec_cover), decoded_data

    def decode(self, stego_img: ndarray) -> Tuple[bool, str]:
        """
        Extract and decode the embedded message from a stego image.

        Parameters:
            stego_img (ndarray): The stego image containing the embedded watermark.

        Returns:
            Tuple[bool, str]:
                - bool: True if the embedded message was successfully decoded, False otherwise.
                - str: The decoded message string if decoding was successful; otherwise, this may be an empty string or invalid data.
        """
        stego_img = np.uint8(stego_img)
        stego_img_tensor = self.transform(stego_img).unsqueeze(0).to(self.device)

        sampled_z = torch.randn(size=(1, self.bit_length)).to(self.device)

        with torch.no_grad():
            _, _ext_watermark = self.iIWN.forward(stego_img_tensor, sampled_z, True, True)

        _ext_watermark = torch.round(torch.clip(_ext_watermark, 0., 1.))
        ext_watermark = _ext_watermark[0].detach().cpu().numpy().astype(int).tolist()
        valid_part = ext_watermark[:(len(ext_watermark) // 8) * 8]
        isdecode, decoded_data = self.bch.Decode(valid_part)
        return isdecode, decoded_data

    def encode_bits(self, cover_img: ndarray, watermark: list) -> Tuple[bool, Any]:
        """
        Embed the watermark bits into an image as a watermark.

        Parameters:
            cover_img (ndarray): The cover image in which the message will be embedded.
            watermark (str): The watermark bits to embed.
                           The required message length depends on the model's mode:
                               - "color_256_64": watermark bits length must be 64
                               - "color_256_100": watermark bits length must be

        Returns:
            Tuple[bool, PIL.Image or None]:
                - (True, PIL.Image):
                    Embedding succeeded. The returned image is the final stego image
                    that contains both the watermark and the auxiliary information
                    (used for recovery) embedded via reversible data hiding (RDH).
                - (False, None):
                    Otherwise. No meaningful image can be returned.
        """
        cover_img = np.uint8(cover_img)

        cover_img_hash = sha256_of_image_array(cover_img)
        cover_img_hash_bitstream = sha256_to_bitstream(cover_img_hash)

        cover_img_tensor = self.transform(cover_img).unsqueeze(0).to(self.device)
        secret_tensor = torch.as_tensor(watermark, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            if self.float64:
                cover_img_tensor = cover_img_tensor.to(torch.float64)
                secret_tensor = secret_tensor.to(torch.float64)
            overflow_stego, z = self.iIWN.forward(cover_img_tensor, secret_tensor, True, False)

        stego_255 = torch.round(overflow_stego * 255.)
        z_round = torch.round(z)
        iscompressok, clip_stego_img, auxbits = self.tensorcoder.compress(stego_255, z_round)
        if iscompressok:
            issuccessful, rdh_stego_img = self.rdh.embed(clip_stego_img, auxbits + cover_img_hash_bitstream)
            if issuccessful:
                return issuccessful, Image.fromarray(np.uint8(rdh_stego_img))
        return False, None

    def recover_bits(self, stego_img: ndarray) -> Union[Tuple[bool, Any, Any], Tuple[bool, None, None]]:
        """
        Recovers the original image and embedded watermark bits from a stego image.

        First attempts to extract compressed features and hash via RDH. If integrity check passes
        (hash match), returns the recovered image and raw watermark bits with `is_attacked = False`.

        If extraction fails or tampering is detected, falls back to blind recovery using random z,
        returning `is_attacked = True` with best-effort results.

        Returns:
            Tuple[bool, PIL.Image or None, list or None]:
                - is_attacked (bool):
                    False if no attack detected and recovery succeeded.
                    True if image was modified or recovery failed.
                - recovered_image (PIL.Image): The reconstructed cover image.
                - recovered_watermark_bits (list of int): The extracted binary watermark (0/1).
        """
        stego_img = np.uint8(stego_img)
        issuccessful, clipped_stego_img, ext_auxbits = self.rdh.extract(stego_img)
        if issuccessful:
            cover_img_hash_bitstream = ext_auxbits[-256:]
            isdecompressok, rec_overflow_stego, rec_z = self.tensorcoder.decompress(clipped_stego_img,
                                                                                    ext_auxbits[:-256])
            if isdecompressok:
                with torch.no_grad():
                    if self.float64:
                        rec_z = rec_z.to(torch.float64)
                        rec_overflow_stego = rec_overflow_stego.to(torch.float64)
                    rec_cover_tensor, rec_watermark = self.iIWN.forward(rec_overflow_stego / 255., rec_z, True, True)

                if rec_cover_tensor.shape[1] == 1:
                    rec_cover = torch.round(rec_cover_tensor * 255.)[0][0].detach().cpu().numpy()
                else:
                    rec_cover = torch.round(rec_cover_tensor * 255.)[0].permute(1, 2, 0).detach().cpu().numpy()
                rec_cover = np.uint8(np.clip(rec_cover, 0, 255))

                rec_cover_img_hash = sha256_of_image_array(rec_cover)
                rec_cover_img_hash_bitstream = sha256_to_bitstream(rec_cover_img_hash)

                rec_watermark = torch.round(torch.clip(rec_watermark, 0., 1.))
                rec_watermark = rec_watermark.squeeze(0).detach().cpu().numpy().astype(int).tolist()

                if np.array_equal(rec_cover_img_hash_bitstream, cover_img_hash_bitstream):
                    return False, Image.fromarray(rec_cover), rec_watermark

        stego_img_to_rec = self.transform(stego_img).unsqueeze(0).to(self.device)
        sampled_z = torch.randn(size=(1, self.bit_length)).to(self.device)
        with torch.no_grad():
            if self.float64:
                sampled_z = sampled_z.to(torch.float64)
                stego_img_to_rec = stego_img_to_rec.to(torch.float64)
            rec_cover_tensor, rec_watermark = self.iIWN.forward(stego_img_to_rec, sampled_z, True, True)
        if rec_cover_tensor.shape[1] == 1:
            rec_cover = torch.round(rec_cover_tensor * 255.)[0][0].detach().cpu().numpy()
        else:
            rec_cover = torch.round(rec_cover_tensor * 255.)[0].permute(1, 2, 0).detach().cpu().numpy()
        rec_cover = np.uint8(np.clip(rec_cover, 0, 255))
        rec_watermark = torch.round(torch.clip(rec_watermark, 0., 1.))
        rec_watermark = rec_watermark.squeeze(0).detach().cpu().numpy().astype(int).tolist()
        return True, Image.fromarray(rec_cover), rec_watermark

    def decode_bits(self, stego_img: ndarray) -> list:
        """
        Extract the binary watermark from a stego image.

        Parameters:
            stego_img (ndarray): The stego image containing the watermark.

        Returns:
            list: The extracted watermark as a list of binary values (0 or 1).
        """
        stego_img = np.uint8(stego_img)
        stego_img_tensor = self.transform(stego_img).unsqueeze(0).to(self.device)

        sampled_z = torch.randn(size=(1, self.bit_length)).to(self.device)

        with torch.no_grad():
            _, _ext_watermark = self.iIWN.forward(stego_img_tensor, sampled_z, True, True)

        _ext_watermark = torch.round(torch.clip(_ext_watermark, 0., 1.))
        ext_watermark = _ext_watermark[0].detach().cpu().numpy().astype(int).tolist()
        return ext_watermark