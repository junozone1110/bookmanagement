# Google API 認証情報設定ガイド

このディレクトリには、Google Sheets API と Google Books API の認証情報を配置します。

## 必要なファイル

### 1. Google Sheets API 認証情報

**ファイル名:** `google_sheets_credentials.json`

**取得手順:**

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成（または既存のプロジェクトを選択）
3. 「APIとサービス」→「ライブラリ」から「Google Sheets API」を有効化
4. 「APIとサービス」→「認証情報」へ移動
5. 「認証情報を作成」→「サービスアカウント」を選択
6. サービスアカウント名を入力して作成
7. 作成したサービスアカウントをクリック
8. 「キー」タブ→「鍵を追加」→「新しい鍵を作成」
9. JSON形式を選択してダウンロード
10. ダウンロードしたファイルを `google_sheets_credentials.json` にリネームしてこのディレクトリに配置

**重要:** サービスアカウントのメールアドレス（例: `xxxxx@xxxxxxx.iam.gserviceaccount.com`）を
対象のスプレッドシートに共有（閲覧者または編集者権限）してください。

### 2. Google Books API キー

**設定場所:** `.env` ファイルの `GOOGLE_BOOKS_API_KEY`

**取得手順:**

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 同じプロジェクトで「APIとサービス」→「ライブラリ」から「Google Books API」を有効化
3. 「APIとサービス」→「認証情報」へ移動
4. 「認証情報を作成」→「APIキー」を選択
5. 作成されたAPIキーをコピー
6. `.env` ファイルの `GOOGLE_BOOKS_API_KEY` に設定

### 3. スプレッドシートID

**設定場所:** `.env` ファイルの `GOOGLE_SHEETS_SPREADSHEET_ID`

**取得方法:**

スプレッドシートのURLから取得します。

```
https://docs.google.com/spreadsheets/d/【この部分がスプレッドシートID】/edit
```

例:
```
URL: https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/edit
ID: 1AbCdEfGhIjKlMnOpQrStUvWxYz
```

## .env ファイルの設定例

```bash
# Google API設定
GOOGLE_SHEETS_CREDENTIALS_PATH=/app/credentials/google_sheets_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=1AbCdEfGhIjKlMnOpQrStUvWxYz
GOOGLE_BOOKS_API_KEY=AIzaSyXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx
```

## セキュリティ注意事項

- `google_sheets_credentials.json` は機密情報です
- このファイルは `.gitignore` に含まれており、Gitにコミットされません
- 本番環境では環境変数または AWS Secrets Manager などで管理してください
- APIキーは定期的にローテーションすることを推奨します

## トラブルシューティング

### エラー: "Credentials file not found"

- `google_sheets_credentials.json` がこのディレクトリに配置されているか確認
- ファイル名が正確に一致しているか確認

### エラー: "The caller does not have permission"

- サービスアカウントのメールアドレスがスプレッドシートに共有されているか確認
- 共有時に「編集者」権限を付与しているか確認（読み取りと書き込みが必要）

### エラー: "API key not valid"

- Google Books API が有効化されているか確認
- APIキーが正しく `.env` に設定されているか確認
- APIキーに制限が設定されている場合は、適切に設定されているか確認
