# 📘 書籍管理システム

Slackワークフローで申請・承認された書籍購入情報を一元管理し、書籍の貸出・返却状況を可視化・管理するシステムです。

## 🚀 特徴

- **自動データ取り込み**: Google Sheetsから承認済み申請を1時間ごとに自動取り込み
- **書籍情報自動取得**: ISBNコードからGoogle Books APIで書籍情報を自動取得
- **ステータス管理**: 購入中 → 本棚保管中 → 貸出中の状態遷移を管理
- **貸出・返却履歴**: 誰がいつ借りて、いつ返却したかの履歴を記録
- **管理画面**: Django管理画面で検索・編集が可能

## 📋 システム要件

- Docker & Docker Compose
- Python 3.11+
- MySQL 8.0
- Google Sheets API 認証情報
- Google Books API キー

## 🛠️ セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd 18_bookmanagement
```

### 2. 環境変数の設定

```bash
# .env.example をコピーして .env を作成
cp credentials/.env.example credentials/.env

# .env ファイルを編集して必要な情報を設定
vi credentials/.env
```

### 3. Google API 認証情報の設定

`credentials/README.md` を参照して、以下を設定してください：

- Google Sheets API 認証情報（JSONファイル）
- Google Books API キー
- スプレッドシートID

### 4. Dockerコンテナの起動

```bash
# コンテナをビルド＆起動
docker-compose -f docker/docker-compose.yml up -d

# ログを確認
docker-compose -f docker/docker-compose.yml logs -f
```

### 5. データベースのマイグレーション

```bash
# マイグレーションを実行
docker-compose -f docker/docker-compose.yml exec app python manage.py migrate

# 管理ユーザーを作成
docker-compose -f docker/docker-compose.yml exec app python manage.py createsuperuser
```

### 6. サンプルデータの投入（オプション）

すぐに管理画面を試したい場合は、サンプルデータを投入できます。

```bash
# サンプルデータを作成
docker-compose -f docker/docker-compose.yml exec app python manage.py create_sample_data

# 既存データを削除して再作成
docker-compose -f docker/docker-compose.yml exec app python manage.py create_sample_data --clear
```

**作成されるデータ**:
- 7冊の書籍（技術書）
- 5件の貸出履歴（現在貸出中2件、返却済み3件）
- 2件のエラーログ

### 7. 管理画面へアクセス

ブラウザで http://localhost:8001/admin にアクセスしてログインしてください。

**ログイン情報**:
- **ユーザー名**: `admin`
- **パスワード**: `admin123`

**注意**: 
- ポート番号は8001です（8000は他のサービスで使用されている場合があるため）
- 本番環境では必ずパスワードを変更してください

詳しい操作方法は [管理画面操作ガイド](docs/ADMIN_GUIDE.md) を参照してください。

## 📂 ディレクトリ構造

```
18_bookmanagement/
├── docker/                          # Docker関連ファイル
│   ├── Dockerfile
│   └── docker-compose.yml
├── app/                             # Djangoアプリケーション
│   ├── manage.py
│   ├── config/                      # Django設定
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── books/                       # 書籍管理アプリ
│       ├── models.py               # データモデル
│       ├── admin.py                # 管理画面設定
│       ├── views.py
│       ├── tests.py                # テストコード
│       ├── utils/                  # ユーティリティ
│       │   ├── google_books_client.py
│       │   └── google_sheets_client.py
│       └── management/commands/    # Django管理コマンド
│           ├── import_from_sheets.py  # バッチ処理
│           ├── test_sheets_connection.py
│           └── create_sample_data.py
├── credentials/                     # API認証情報
│   ├── .env                        # 環境変数（.gitignore）
│   ├── .env.example                # 環境変数のサンプル
│   ├── google_sheets_credentials.json  # Google Sheets認証（.gitignore）
│   └── README.md                   # 認証情報設定ガイド
├── docs/                            # ドキュメント
│   ├── ADMIN_GUIDE.md
│   ├── BATCH_PROCESSING.md
│   └── archive/                    # 開発過程のレポート
├── logs/                            # ログファイル
└── README.md                        # このファイル
```

## 🎯 主な機能

### 1. スプレッドシート連携（バッチ処理）

- 1時間ごとに自動で承認済み申請を取り込み
- 重複取り込みを防止（DB取り込み済みフラグ）
- エラー時は該当レコードのみスキップし、他は処理継続
- エラーログをDBに記録し、管理画面から確認可能
- 詳細は [バッチ処理ドキュメント](docs/BATCH_PROCESSING.md) を参照

### 2. 書籍情報管理

- ISBNから書籍情報を自動取得（タイトル、著者、出版社、書影など）
- 書籍のステータス管理（購入中/本棚保管中/貸出中/その他）
- 保管場所の記録

### 3. 貸出・返却管理

- 貸出人名、貸出日、返却予定日の記録
- 返却時の実返却日の記録
- 過去の貸出履歴の閲覧

### 4. 検索・フィルタリング

- 書籍名、著者、ISBNコードでの検索
- ステータス、貸出人名でのフィルタリング
- ページネーション対応

## 📦 バッチ処理

### バッチ実行

```bash
# 手動実行（Djangoコマンド）
docker-compose -f docker/docker-compose.yml exec app python manage.py import_from_sheets

# テスト（接続確認）
docker-compose -f docker/docker-compose.yml exec app python manage.py test_sheets_connection

# または、スクリプトを使用
./scripts/run_batch.sh
./scripts/test_batch.sh
```

### Cron設定（定期実行）

```bash
# Cron設定をインストール（1時間おきに自動実行）
crontab config/crontab

# Cron確認
crontab -l

# Cron削除
crontab -r
```

### ログ確認

```bash
# バッチ実行ログ
ls -lt logs/batch_*.log | head -5

# 最新ログの表示
tail -f logs/batch_$(ls -t logs/batch_*.log | head -1 | xargs basename)
```

詳細は [バッチ処理ドキュメント](docs/BATCH_PROCESSING.md) を参照してください。

## 🔧 開発コマンド

### コンテナの操作

```bash
# コンテナの起動
docker-compose -f docker/docker-compose.yml up -d

# コンテナの停止
docker-compose -f docker/docker-compose.yml down

# コンテナの再起動
docker-compose -f docker/docker-compose.yml restart

# ログの表示
docker-compose -f docker/docker-compose.yml logs -f app
```

### Django管理コマンド

```bash
# マイグレーションファイルの作成
docker-compose -f docker/docker-compose.yml exec app python manage.py makemigrations

# マイグレーションの実行
docker-compose -f docker/docker-compose.yml exec app python manage.py migrate

# 管理ユーザーの作成
docker-compose -f docker/docker-compose.yml exec app python manage.py createsuperuser

# Djangoシェルの起動
docker-compose -f docker/docker-compose.yml exec app python manage.py shell

# テストの実行
docker-compose -f docker/docker-compose.yml exec app python manage.py test books
```

### テスト

```bash
# すべてのテストを実行
docker-compose -f docker/docker-compose.yml exec app python manage.py test

# 詳細な出力でテストを実行
docker-compose -f docker/docker-compose.yml exec app python manage.py test books --verbosity=2

# 特定のテストクラスのみ実行
docker-compose -f docker/docker-compose.yml exec app python manage.py test books.tests.BookModelTests
```

**実装済みテスト**:
- 書籍モデルのテスト（作成、重複チェック、貸出人取得など）
- 貸出履歴モデルのテスト（延滞判定など）
- エラーログモデルのテスト
- Google Books APIクライアントのテスト（ISBN妥当性チェックなど）
- APIエンドポイントのテスト

### データベース操作

```bash
# MySQLに接続
docker-compose -f docker/docker-compose.yml exec db mysql -u bookadmin -p book_management

# データベースのバックアップ
docker-compose -f docker/docker-compose.yml exec db mysqldump -u bookadmin -p book_management > backup.sql
```

## 📊 データモデル

### Book（書籍マスタ）
- 申請情報（申請番号、申請者、承認者、日付、価格）
- 書籍情報（ISBN、タイトル、著者、出版社、書影URL、概要）
- 管理情報（ステータス、保管場所）

### RentalHistory（貸出履歴）
- 書籍、貸出人名、貸出日、返却予定日、実返却日

### ErrorLog（エラーログ）
- 申請番号、ISBN、エラー種別、エラーメッセージ、発生日時

## 🔒 セキュリティ

- 認証情報は環境変数で管理
- 機密情報は `.gitignore` でバージョン管理から除外
- 本番環境では `DEBUG=False` に設定
- Django ORM使用でSQLインジェクション対策

## 📝 今後の拡張予定（Phase 2以降）

- [ ] Slack通知機能
- [ ] 返却期限リマインダー
- [ ] 延滞アラート
- [ ] 書籍レビュー・評価機能
- [ ] 統計ダッシュボード
- [ ] QRコード管理
- [ ] ユーザー認証機能

## 📖 ドキュメント

- [実装計画書](book-management-system-implementation-plan.md)
- [管理画面操作ガイド](docs/ADMIN_GUIDE.md)
- [バッチ処理ドキュメント](docs/BATCH_PROCESSING.md)
- [Google API設定ガイド](credentials/README.md)
- [開発過程のレポート](docs/archive/) - Phase1/Phase2の完了レポート

## 🤝 サポート

問題が発生した場合は、以下を確認してください：

1. Docker コンテナが正常に起動しているか
2. `.env` ファイルが正しく設定されているか
3. Google API 認証情報が正しく配置されているか
4. ログファイルでエラーメッセージを確認

## 📜 ライセンス

社内利用のため、ライセンスは設定されていません。

---

**作成日**: 2025年10月16日  
**最終更新**: 2025年10月20日  
**バージョン**: 1.1  
**作成者**: システム開発チーム

### 更新履歴

- **v1.1** (2025/10/20)
  - バッチ処理のリファクタリング（batch/ → books/management/commands/）
  - テストコードの実装（20テストケース）
  - .env.exampleの追加
  - ドキュメント整理（archive化）
  - 申請番号での重複チェック機能追加

- **v1.0** (2025/10/16)
  - 初回リリース
  - 基本機能実装完了

