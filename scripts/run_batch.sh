#!/bin/bash

# 書籍取り込みバッチ実行スクリプト

# エラー時は即座に終了
set -e

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# ログファイルの設定
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/batch_$(date +%Y%m%d_%H%M%S).log"

# ログディレクトリが存在しない場合は作成
mkdir -p "$LOG_DIR"

# バッチ実行
echo "========================================" | tee -a "$LOG_FILE"
echo "Book Import Batch Started" | tee -a "$LOG_FILE"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Dockerコンテナ内でDjango管理コマンドを実行
docker-compose -f docker/docker-compose.yml exec -T app python manage.py import_from_sheets 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "Batch Finished with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 古いログファイルを削除（30日以上前のもの）
find "$LOG_DIR" -name "batch_*.log" -type f -mtime +30 -delete

exit $EXIT_CODE

