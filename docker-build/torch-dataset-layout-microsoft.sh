#!/bin/sh
mkdir -p /app/share-storage/dataset
mv -f /app-dataset/huggingface/models--microsoft--layoutlm-base-uncased /app/share-storage/dataset
mv -f /app-dataset/huggingface/hub /app/share-storage/dataset
mv -f /app-dataset/huggingface/metrics /app/share-storage/dataset
mv -f /app-dataset/huggingface/modules /app/share-storage/dataset


mkdir -p /app/share-storage/dataset/torch-dataset-layout-microsoft-installed