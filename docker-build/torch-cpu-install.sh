#!/bin/sh
#export NO_CACHE="--no-cache-dir"
export NO_CACHE=""
pip uninstall torchvision -y
pip uninstall torchaudio -y
pip uninstall timm -y
pip uninstall easyocr -y
pip uninstall torch -y
pip install torch --extra-index-url https://download.pytorch.org/whl/cpu $NO_CACHE
pip install torchvision --extra-index-url https://download.pytorch.org/whl/cpu $NO_CACHE
pip install torchaudio --extra-index-url https://download.pytorch.org/whl/cpu $NO_CACHE
pip install timm
pip install easyocr
pip install librosa
pip install soundfile