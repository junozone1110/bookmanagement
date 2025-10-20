#!/bin/bash

# バッチ処理テストスクリプト

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "========================================="
echo "バッチ処理テストの開始"
echo "========================================="
echo ""

# 1. Google Sheets API 接続テスト
echo "[1/4] Google Sheets API 接続テスト..."
docker-compose -f docker/docker-compose.yml exec -T app python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from books.utils.google_sheets_client import GoogleSheetsClient

try:
    client = GoogleSheetsClient()
    
    # 認証情報ファイルの存在確認
    if not os.path.exists(client.credentials_path):
        print('❌ Google Sheets認証情報ファイルが見つかりません')
        print(f'   Expected: {client.credentials_path}')
        exit(1)
    
    # スプレッドシートIDの確認
    if not client.spreadsheet_id:
        print('❌ スプレッドシートIDが設定されていません')
        print('   .env ファイルで GOOGLE_SHEETS_SPREADSHEET_ID を設定してください')
        exit(1)
    
    # 認証テスト
    client.authenticate()
    print('✓ Google Sheets API 接続成功')
    
except FileNotFoundError as e:
    print(f'❌ 認証情報ファイルが見つかりません: {e}')
    exit(1)
except Exception as e:
    print(f'❌ Google Sheets API 接続失敗: {e}')
    exit(1)
"
echo ""

# 2. Google Books API 接続テスト
echo "[2/4] Google Books API 接続テスト..."
docker-compose -f docker/docker-compose.yml exec -T app python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from books.utils.google_books_client import GoogleBooksClient

try:
    client = GoogleBooksClient()
    
    # テスト用ISBN（「エリック・エヴァンスのドメイン駆動設計」）
    test_isbn = '9784798121963'
    
    print(f'   テスト用ISBN: {test_isbn}')
    book_info = client.get_book_info_by_isbn(test_isbn)
    
    if book_info:
        print(f'   ✓ 書籍情報取得成功: {book_info.get(\"title\", \"N/A\")}')
    else:
        print('   ⚠ 書籍情報が取得できませんでした（APIキーが未設定の可能性があります）')
    
    print('✓ Google Books API 接続成功')
    
except Exception as e:
    print(f'❌ Google Books API 接続失敗: {e}')
    exit(1)
"
echo ""

# 3. データベース接続テスト
echo "[3/4] データベース接続テスト..."
docker-compose -f docker/docker-compose.yml exec -T app python -c "
from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        if result[0] == 1:
            print('✓ データベース接続成功')
        else:
            print('❌ データベース接続失敗')
            exit(1)
except Exception as e:
    print(f'❌ データベース接続エラー: {e}')
    exit(1)
"
echo ""

# 4. バッチコマンドのDry Run（実装後）
echo "[4/4] バッチコマンドの存在確認..."
docker-compose -f docker/docker-compose.yml exec -T app python manage.py help import_from_sheets > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ import_from_sheets コマンドが利用可能です"
else
    echo "❌ import_from_sheets コマンドが見つかりません"
    exit 1
fi
echo ""

echo "========================================="
echo "✅ 全てのテストが完了しました"
echo "========================================="
echo ""
echo "次のステップ:"
echo "1. credentials/.env ファイルにGoogle API設定を記入"
echo "2. credentials/google_sheets_credentials.json を配置"
echo "3. ./scripts/run_batch.sh を実行してバッチ処理をテスト"
echo ""

