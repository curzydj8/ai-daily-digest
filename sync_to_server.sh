#!/bin/bash
# 同步 AI 日报到 6ix9ine 服务器（/ai-daily/），主页已指向站内。
# 同步 data/（当日文件 + index.json）与每日轮换的 knowledge/、prompts/、tools/；
# index.html 不常变，改动时手动同步。
set -e
cd "$(dirname "$0")"
BASE=/opt/web-platform/applications/ai-daily
rsync -rlptz --chmod=a+rX -e "ssh -F $HOME/.ssh/config" data/ --rsync-path="sudo rsync" 6ix9ine:$BASE/data/
rsync -rlptz --chmod=a+rX -e "ssh -F $HOME/.ssh/config" knowledge/ --rsync-path="sudo rsync" 6ix9ine:$BASE/knowledge/
rsync -rlptz --chmod=a+rX -e "ssh -F $HOME/.ssh/config" prompts/ --rsync-path="sudo rsync" 6ix9ine:$BASE/prompts/
rsync -rlptz --chmod=a+rX -e "ssh -F $HOME/.ssh/config" tools/ --rsync-path="sudo rsync" 6ix9ine:$BASE/tools/
TODAY=$(TZ=Asia/Shanghai date +%F)
ssh -F $HOME/.ssh/config 6ix9ine "grep -q $TODAY $BASE/data/index.json && echo SYNC_OK $TODAY || { echo SYNC_FAIL $TODAY; exit 1; }"
