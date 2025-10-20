#!/bin/bash

# 書籍管理システム セットアップスクリプト

set -e

echo "========================================="
echo "書籍管理システム セットアップ開始"
echo "========================================="
echo ""

# 1. 環境変数ファイルの確認
echo "[1/5] 環境変数ファイルの確認..."
if [ ! -f credentials/.env ]; then
    echo "  .envファイルが見つかりません。テンプレートからコピーします..."
    cp credentials/.env.example credentials/.env
    echo "  ✓ .envファイルを作成しました"
    echo "  ⚠ credentials/.env を編集して、必要な設定を行ってください"
else
    echo "  ✓ .envファイルが存在します"
fi
echo ""

# 2. Google API認証情報の確認
echo "[2/5] Google API認証情報の確認..."
if [ ! -f credentials/google_sheets_credentials.json ]; then
    echo "  ⚠ google_sheets_credentials.json が見つかりません"
    echo "  ℹ credentials/README.md を参照して認証情報を設定してください"
else
    echo "  ✓ Google Sheets認証情報が存在します"
fi
echo ""

# 3. Dockerコンテナのビルドと起動
echo "[3/5] Dockerコンテナのビルドと起動..."
docker-compose -f docker/docker-compose.yml up -d --build
echo "  ✓ コンテナを起動しました"
echo ""

# 4. データベースマイグレーション
echo "[4/5] データベースマイグレーション..."
sleep 5  # データベース起動を待機
docker-compose -f docker/docker-compose.yml exec -T app python manage.py migrate
echo "  ✓ マイグレーションが完了しました"
echo ""

# 5. 完了メッセージ
echo "[5/5] セットアップ完了"
echo ""
echo "========================================="
echo "セットアップが完了しました！"
echo "========================================="
echo ""
echo "次のステップ:"
echo "1. 管理ユーザーを作成:"
echo "   docker-compose -f docker/docker-compose.yml exec app python manage.py createsuperuser"
echo ""
echo "2. 管理画面にアクセス:"
echo "   http://localhost:8001/admin"
echo ""
echo "3. ログの確認:"
echo "   docker-compose -f docker/docker-compose.yml logs -f app"
echo ""
echo "4. コンテナの停止:"
echo "   docker-compose -f docker/docker-compose.yml down"
echo ""

