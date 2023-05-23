#!/bin/sh
mkdir -p /app/share-storage/dataset
mkdir -p /app/share-storage/dataset/chek-version

mv -f /app-dataset/deepdoctection /app/share-storage/dataset
mv -f /app-dataset/doctr /app/share-storage/dataset
mv -f /app-dataset/easyocr /app/share-storage/dataset
mv -f /app-dataset/huggingface /app/share-storage/dataset
mv -f /app-dataset/matplotlib /app/share-storage/dataset
mv -f /app-dataset/torch /app/share-storage/dataset
mv -f /app-dataset/weights /app/share-storage/dataset
mv -f /app-dataset/conf_dd_one.yaml /app/share-storage/dataset
