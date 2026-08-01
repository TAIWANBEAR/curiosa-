#!/usr/bin/env bash
# 建置並就地部署:產生 site/ 後複製到 repo 根目錄(GitHub Pages 從 main/root 供應)
set -e
python build.py
cp -r site/* .
rm -rf site __pycache__
echo "OK deployed to repo root"
