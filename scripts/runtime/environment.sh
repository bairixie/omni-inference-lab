: "${OMNI_WORKSPACE:?Set OMNI_WORKSPACE to the existing run workspace}"
# Source from an existing Slurm GPU allocation.
source "${OMNI_WORKSPACE}/sglang-env/bin/activate"
export HF_HOME=${OMNI_WORKSPACE}/cache/huggingface
export HF_HUB_CACHE=${OMNI_WORKSPACE}/cache/huggingface/hub
export HF_MODULES_CACHE=${OMNI_WORKSPACE}/cache/sglang-hf-modules
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=8
export TMPDIR=${OMNI_WORKSPACE}/tmp
export XDG_CACHE_HOME=${OMNI_WORKSPACE}/cache/sglang-xdg
export TRITON_CACHE_DIR=${OMNI_WORKSPACE}/cache/sglang-triton
export TORCHINDUCTOR_CACHE_DIR=${OMNI_WORKSPACE}/cache/sglang-inductor
export SGLANG_OMNI_STARTUP_TIMEOUT=1800
export CUDA_HOME=${OMNI_WORKSPACE}/toolchains/cuda13
export PATH="$CUDA_HOME/bin:$PATH"
export LIBRARY_PATH="$CUDA_HOME/lib64${LIBRARY_PATH:+:$LIBRARY_PATH}"
export MAX_JOBS=8
export LD_LIBRARY_PATH="${OMNI_WORKSPACE}/toolchains/ffmpeg/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
