# バッチ処理ドキュメント

## 概要

書籍管理システムのバッチ処理は、Google Sheetsから承認済みの書籍購入申請を自動的に取り込み、Google Books APIで書籍情報を取得してデータベースに登録します。

## 処理フロー

```
1. Google Sheets APIで申請スプレッドシート取得
   ↓
2. 取り込み条件チェック
   - 承認者名(C列)が入力されている
   - 承認日(E列)が入力されている
   - DB取り込み済みフラグ(I列)が空
   ↓
3. 対象レコードをループ処理
   ├─ ISBNでGoogle Books API呼び出し
   ├─ 成功 → DBに書籍登録(status='ordered') → フラグ立て
   └─ 失敗 → error_logsに記録 → フラグ立てない（次回リトライ可能）
   ↓
4. スプレッドシートに結果を書き戻し
```

## スプレッドシート列構成

| 列 | 項目 | 必須 | 備考 |
|----|------|------|------|
| A | 申請番号 | ○ | 通し番号 |
| B | 申請者名 | ○ | |
| C | 承認者名 | ○ | 取り込み条件 |
| D | 申請日 | ○ | YYYY/MM/DD形式 |
| E | 承認日 | ○ | YYYY/MM/DD形式、取り込み条件 |
| F | 書籍名 | - | 参考情報（APIで上書きされる） |
| G | ISBNコード | ○ | 10桁または13桁 |
| H | 価格 | - | |
| I | DB取り込み済み | - | システムが自動記入（✓） |

## 実行方法

### 1. 手動実行（Django管理コマンド）

```bash
# コンテナ内で実行
docker-compose -f docker/docker-compose.yml exec app python manage.py import_from_sheets

# ローカルから実行（推奨）
./scripts/run_batch.sh
```

### 2. 定期実行（Cron）

```bash
# Crontab設定をインストール
crontab config/crontab

# Crontab確認
crontab -l

# Crontab削除
crontab -r
```

**スケジュール**: 毎時0分に実行（0 * * * *）

## テスト方法

### 事前テスト

バッチ処理を実行する前に、各種接続をテストします。

```bash
./scripts/test_batch.sh
```

このスクリプトは以下をチェックします：
1. Google Sheets API 接続
2. Google Books API 接続
3. データベース接続
4. Django管理コマンドの存在確認

### 動作確認手順

1. **テスト用スプレッドシート準備**
   - 実際のスプレッドシートまたはコピーを使用
   - テスト用データを1〜2行追加
   - 承認者名と承認日を入力
   - DB取り込み済みフラグは空にしておく

2. **バッチ実行**
   ```bash
   ./scripts/run_batch.sh
   ```

3. **結果確認**
   - ログファイル: `logs/batch_YYYYMMDD_HHMMSS.log`
   - スプレッドシートのI列に✓が付いているか
   - データベースに書籍が登録されているか
   - エラーログテーブルを確認

4. **管理画面で確認**
   - http://localhost:8001/admin/books/book/
   - 登録された書籍情報を確認

## エラーハンドリング

### エラー種別

| エラー種別 | 説明 | 対処方法 |
|-----------|------|---------|
| INITIALIZATION_ERROR | APIクライアント初期化失敗 | 認証情報を確認 |
| INVALID_ISBN | ISBN形式が不正 | スプレッドシートのISBNを修正 |
| BOOK_NOT_FOUND | Google Books APIで書籍が見つからない | ISBNが正しいか確認、手動で書籍情報を入力 |
| PROCESSING_ERROR | その他の処理エラー | ログを確認して原因を特定 |
| BATCH_ERROR | バッチ全体のエラー | システム設定を確認 |

### エラー時の動作

1. **個別エラー**: 該当行のみスキップし、他の行は処理を継続
2. **エラーログ記録**: `error_logs` テーブルに記録
3. **フラグなし**: エラーの行は「DB取り込み済み」フラグを立てない → 次回リトライ
4. **ログ出力**: ログファイルとDjangoログに詳細を記録

### エラーログ確認方法

#### 管理画面から
http://localhost:8001/admin/books/errorlog/

#### コマンドライン
```bash
docker-compose -f docker/docker-compose.yml exec app python manage.py shell
```

```python
from books.models import ErrorLog

# 最新10件のエラーログ
for log in ErrorLog.objects.all()[:10]:
    print(f"{log.created_at}: {log.error_type} - {log.error_message}")
```

## ログファイル

### 出力先

| ファイル | 説明 |
|---------|------|
| `logs/batch_YYYYMMDD_HHMMSS.log` | バッチ実行ごとのログ |
| `logs/cron.log` | Cron実行時の標準出力 |
| `/var/log/book-management/batch.log` | アプリケーションログ（コンテナ内） |

### ログローテーション

- バッチログ: 30日以上前のファイルは自動削除
- アプリケーションログ: 要設定（TODO）

## トラブルシューティング

### Google Sheets API接続エラー

```
FileNotFoundError: Credentials file not found
```

**対処**:
1. `credentials/google_sheets_credentials.json` が配置されているか確認
2. ファイルパスが正しいか確認（.envのGOOGLE_SHEETS_CREDENTIALS_PATH）

```
The caller does not have permission
```

**対処**:
1. サービスアカウントのメールアドレスをスプレッドシートに共有
2. 「編集者」権限を付与

### Google Books API接続エラー

```
Book not found for ISBN
```

**対処**:
1. ISBNが正しいか確認（ハイフンなし13桁）
2. Google Books APIで実際に検索可能か確認
3. APIキーが正しく設定されているか確認

### データベース接続エラー

```
Can't connect to MySQL server
```

**対処**:
1. MySQLコンテナが起動しているか確認: `docker-compose ps`
2. .envの接続情報が正しいか確認
3. コンテナを再起動: `docker-compose restart`

### Cron実行されない

**確認事項**:
1. `crontab -l` でCronが登録されているか確認
2. スクリプトのパスが正しいか確認
3. スクリプトに実行権限があるか確認: `ls -l scripts/run_batch.sh`
4. Cronログを確認: `cat logs/cron.log`

## パフォーマンス考慮事項

### 処理時間の目安

- 1件あたり: 約2〜3秒（Google Books API呼び出し含む）
- 10件: 約20〜30秒
- 100件: 約3〜5分

### APIレート制限

**Google Books API**:
- 制限: 1000リクエスト/日（無料）
- 対策: エラー時はリトライせず、次回実行時に再処理

**Google Sheets API**:
- 制限: 100リクエスト/100秒/ユーザー
- 対策: バッチ処理内では問題なし（1時間に1回のみ）

### 大量データ処理時の注意

- 1時間に100件以上の承認がある場合は、バッチ実行頻度を増やす
- または、複数回に分けて処理する仕組みを実装

## 監視・アラート（将来実装）

Phase 2以降で実装予定：

- [ ] Slack通知（エラー発生時）
- [ ] メール通知（バッチ失敗時）
- [ ] ダッシュボードでバッチ実行状況を可視化
- [ ] CloudWatchアラート設定

## 関連ファイル

| ファイル | 説明 |
|---------|------|
| `app/batch/import_books.py` | バッチ処理メインロジック |
| `app/books/management/commands/import_from_sheets.py` | Django管理コマンド |
| `app/books/utils/google_sheets_client.py` | Google Sheets APIクライアント |
| `app/books/utils/google_books_client.py` | Google Books APIクライアント |
| `scripts/run_batch.sh` | バッチ実行スクリプト |
| `scripts/test_batch.sh` | バッチテストスクリプト |
| `config/crontab` | Cron設定ファイル |

---

**作成日**: 2025年10月16日  
**バージョン**: 1.0  
**担当**: システム開発チーム

