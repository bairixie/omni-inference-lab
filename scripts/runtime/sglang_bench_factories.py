"""Local benchmark factories that turn off MiniCPM encoder result caching."""
from sglang_omni.models.minicpm_o import stages


def create_image_encoder_executor(model_path, *, device=None, gpu_id=None, dtype=None):
    previous=(stages.ENCODER_CACHE_MAX_ENTRIES,stages.ENCODER_CACHE_MAX_BYTES)
    stages.ENCODER_CACHE_MAX_ENTRIES=0
    stages.ENCODER_CACHE_MAX_BYTES=0
    try:
        return stages.create_image_encoder_executor(model_path,device=device,gpu_id=gpu_id,dtype=dtype)
    finally:
        stages.ENCODER_CACHE_MAX_ENTRIES,stages.ENCODER_CACHE_MAX_BYTES=previous


def create_audio_encoder_executor(model_path, *, device=None, gpu_id=None, dtype=None):
    previous=(stages.ENCODER_CACHE_MAX_ENTRIES,stages.ENCODER_CACHE_MAX_BYTES)
    stages.ENCODER_CACHE_MAX_ENTRIES=0
    stages.ENCODER_CACHE_MAX_BYTES=0
    try:
        return stages.create_audio_encoder_executor(model_path,device=device,gpu_id=gpu_id,dtype=dtype)
    finally:
        stages.ENCODER_CACHE_MAX_ENTRIES,stages.ENCODER_CACHE_MAX_BYTES=previous
