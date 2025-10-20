# 📘 書籍管理システム 実装計画書

## 1. システム概要

### 1.1 目的
Slackワークフローで申請・承認された書籍購入情報を一元管理し、書籍の貸出・返却状況を可視化・管理するシステム

### 1.2 システム要件

#### 1.2.1 機能要件

##### A. スプレッドシート連携機能
| 要件ID | 要件内容 | 優先度 |
|--------|----------|--------|
| FR-A01 | Google Sheets APIを使用して申請スプレッドシートからデータを取得できること | 必須 |
| FR-A02 | 1時間おきに自動でスプレッドシートを監視し、新規承認データを取得すること | 必須 |
| FR-A03 | 取り込み条件として「承認者名」「承認日」が入力されていることをチェックすること | 必須 |
| FR-A04 | 「DB取り込み済み」フラグを用いて重複取り込みを防止すること | 必須 |
| FR-A05 | 取り込み成功時にスプレッドシートへフラグを書き戻すこと | 必須 |
| FR-A06 | API取得失敗時は該当レコードのみフラグを立てず、他レコードは正常処理すること | 必須 |

##### B. 書籍情報管理機能
| 要件ID | 要件内容 | 優先度 |
|--------|----------|--------|
| FR-B01 | ISBNコードをキーにGoogle Books APIから書籍情報を自動取得できること | 必須 |
| FR-B02 | 取得する書籍情報：タイトル、著者、出版社、出版日、書影URL、書籍概要 | 必須 |
| FR-B03 | 申請情報（申請番号、申請者、承認者、申請日、承認日、価格）を保存できること | 必須 |
| FR-B04 | 書籍の初期ステータスは「購入中(ordered)」として登録されること | 必須 |
| FR-B05 | 書籍ごとに保管場所（本棚位置等）をフリーテキストで記録できること | 推奨 |
| FR-B06 | ISBNコードを編集後、書籍情報を再取得できる機能を提供すること | 必須 |
| FR-B07 | 同一ISBNの書籍が複数回申請された場合、別の書籍として登録すること | 必須 |

##### C. ステータス管理機能
| 要件ID | 要件内容 | 優先度 |
|--------|----------|--------|
| FR-C01 | 書籍のステータスとして「購入中」「本棚保管中」「貸出中」「その他」を管理できること | 必須 |
| FR-C02 | ステータス遷移：購入中 → 本棚保管中 → 貸出中 → 本棚保管中（返却） | 必須 |
| FR-C03 | 管理画面からステータスを変更できること | 必須 |

##### D. 貸出・返却管理機能
| 要件ID | 要件内容 | 優先度 |
|--------|----------|--------|
| FR-D01 | 本棚保管中の書籍を貸出中に変更する際、貸出人名を手入力できること | 必須 |
| FR-D02 | 貸出時に返却予定日を入力できること（初期値：貸出日の翌日） | 必須 |
| FR-D03 | 貸出履歴として、貸出人名、貸出日、返却予定日、実際の返却日を記録すること | 必須 |
| FR-D04 | 返却時に書籍ステータスを「本棚保管中」に戻し、返却日を記録すること | 必須 |
| FR-D05 | 書籍ごとに過去の貸出履歴を一覧表示できること | 必須 |

##### E. 検索・一覧表示機能
| 要件ID | 要件内容 | 優先度 |
|--------|----------|--------|
| FR-E01 | 書籍を書籍名（部分一致）、著者名（部分一致）、ISBNコード（完全一致）で検索できること | 必須 |
| FR-E02 | ステータス、貸出人名でフィルタリングできること | 必須 |
| FR-E03 | 申請日、書籍名、ステータス、貸出人名でソートできること | 必須 |
| FR-E04 | 一覧表示時に書影、書籍名、著者、ステータス、貸出人、返却予定日を表示すること | 必須 |
| FR-E05 | ページネーション機能（20件/50件/100件切替）を提供すること | 必須 |

##### F. エラー処理・ログ機能
| 要件ID | 要件内容 | 優先度 |
|--------|----------|--------|
| FR-F01 | API取得失敗時にエラーログをDBとログファイルに記録すること | 必須 |
| FR-F02 | エラーログに申請番号、ISBNコード、エラー種別、エラーメッセージ、発生日時を記録すること | 必須 |
| FR-F03 | 管理画面からエラーログを一覧表示できること | 必須 |
| FR-F04 | バッチ処理のログをファイル（/var/log/book-management/）に出力すること | 必須 |

---

#### 1.2.2 非機能要件

##### A. 性能要件
| 要件ID | 要件内容 | 目標値 |
|--------|----------|--------|
| NFR-A01 | バッチ処理は1時間以内に完了すること | < 60分 |
| NFR-A02 | 管理画面の書籍一覧表示は3秒以内に表示されること | < 3秒 |
| NFR-A03 | 書籍検索は2秒以内に結果を返すこと | < 2秒 |
| NFR-A04 | Google Books APIのレート制限を考慮した実装とすること | - |

##### B. 可用性要件
| 要件ID | 要件内容 | 目標値 |
|--------|----------|--------|
| NFR-B01 | システム稼働率 | > 99% (営業時間内) |
| NFR-B02 | バッチ処理失敗時も次回実行で自動リトライされること | - |
| NFR-B03 | API障害時も他の処理は継続すること | - |

##### C. 保守性要件
| 要件ID | 要件内容 | 
|--------|----------|
| NFR-C01 | コードはPEP 8に準拠したPythonコーディング規約に従うこと |
| NFR-C02 | 関数・クラスには適切なdocstringを記載すること |
| NFR-C03 | 環境変数は.envファイルで管理し、機密情報をコードに含めないこと |
| NFR-C04 | データベースマイグレーションはDjangoのマイグレーション機能を使用すること |

##### D. セキュリティ要件
| 要件ID | 要件内容 | 
|--------|----------|
| NFR-D01 | Google APIの認証情報は環境変数または専用ディレクトリで管理すること |
| NFR-D02 | SQLインジェクション対策としてDjango ORMを使用すること |
| NFR-D03 | 本番環境ではDEBUGモードを無効化すること |
| NFR-D04 | 初期フェーズでは認証機能は実装しない（将来的に追加予定） |

##### E. ユーザビリティ要件
| 要件ID | 要件内容 | 
|--------|----------|
| NFR-E01 | 管理画面は直感的で使いやすいUIであること |
| NFR-E02 | ステータスは色分け表示で視認性を高めること |
| NFR-E03 | 書影を表示することで書籍を視覚的に識別しやすくすること |
| NFR-E04 | エラーメッセージは具体的で対処方法が分かる内容とすること |

##### F. 拡張性要件
| 要件ID | 要件内容 | 
|--------|----------|
| NFR-F01 | 将来的なSlack通知機能追加を考慮した設計とすること |
| NFR-F02 | 将来的なユーザー認証機能追加を考慮した設計とすること |
| NFR-F03 | 新規ステータスの追加が容易な設計とすること |

---

#### 1.2.3 外部連携要件

##### A. Google Sheets API連携
| 要件ID | 要件内容 | 詳細 |
|--------|----------|------|
| EXT-A01 | Google Sheets API v4を使用すること | - |
| EXT-A02 | OAuth 2.0またはサービスアカウント認証を使用すること | - |
| EXT-A03 | スプレッドシートの列構成に依存しない柔軟な実装とすること | 列位置はコンフィグ管理 |
| EXT-A04 | 読み取りと書き込み権限が必要 | 「DB取り込み済み」フラグ書き込み |

##### B. Google Books API連携
| 要件ID | 要件内容 | 詳細 |
|--------|----------|------|
| EXT-B01 | Google Books API v1を使用すること | - |
| EXT-B02 | ISBNコードをキーに書籍情報を検索すること | volumes?q=isbn:{isbn} |
| EXT-B03 | API呼び出し失敗時は適切にエラーハンドリングすること | タイムアウト、404等 |
| EXT-B04 | レート制限を考慮した実装とすること | 1秒あたりのリクエスト数制限 |

---

#### 1.2.4 データ要件

##### A. データモデル
| 要件ID | 要件内容 |
|--------|----------|
| DATA-A01 | 書籍マスタ、貸出履歴、エラーログの3テーブルで構成すること |
| DATA-A02 | 書籍と貸出履歴は1対多の関係とすること |
| DATA-A03 | 日付フォーマットは「YYYY/MM/DD」で統一すること |
| DATA-A04 | 文字コードはUTF-8（utf8mb4）を使用すること |

##### B. データ整合性
| 要件ID | 要件内容 |
|--------|----------|
| DATA-B01 | データベースを唯一の真実の情報源（Single Source of Truth）とすること |
| DATA-B02 | スプレッドシートは新規データのインプット元としてのみ機能すること |
| DATA-B03 | 外部キー制約を適切に設定すること（貸出履歴 → 書籍） |
| DATA-B04 | NOT NULL制約、デフォルト値を適切に設定すること |

##### C. データ保持期間
| 要件ID | 要件内容 |
|--------|----------|
| DATA-C01 | 書籍データは削除せず永続的に保持すること |
| DATA-C02 | 貸出履歴は全て保持すること（監査目的） |
| DATA-C03 | エラーログは初期フェーズでは削除しない（運用後、定期削除検討） |

---

#### 1.2.5 制約事項

##### A. 技術的制約
| 制約ID | 制約内容 | 理由 |
|--------|----------|------|
| CON-A01 | 開発言語はPythonに限定 | 組織標準 |
| CON-A02 | データベースはMySQLに限定 | インフラ制約 |
| CON-A03 | 本番環境はAWSを使用 | インフラ制約 |
| CON-A04 | 認証機能は初期フェーズでは実装しない | 要件の優先順位 |

##### B. 運用上の制約
| 制約ID | 制約内容 | 理由 |
|--------|----------|------|
| CON-B01 | バッチ処理は1時間おきに実行 | 要件定義 |
| CON-B02 | 貸出人名は手入力方式 | 初期フェーズの要件 |
| CON-B03 | Slack通知は初期フェーズでは実装しない | 要件の優先順位 |
| CON-B04 | 延滞アラートは初期フェーズでは実装しない | 要件の優先順位 |

##### C. スコープ外
| 項目 | 備考 |
|------|------|
| ユーザー認証・権限管理 | Phase 2以降で検討 |
| Slack通知機能 | Phase 2以降で検討 |
| 延滞アラート機能 | Phase 2以降で検討 |
| 統計ダッシュボード | Phase 2以降で検討 |
| QRコード管理 | Phase 2以降で検討 |
| 書籍レビュー・評価機能 | Phase 2以降で検討 |
| モバイルアプリ | スコープ外 |

---

#### 1.2.6 前提条件

| 前提ID | 前提内容 |
|--------|----------|
| PRE-01 | Slackワークフローで書籍購入申請・承認が既に運用されていること |
| PRE-02 | 申請・承認データがGoogle Sheetsに蓄積される仕組みが構築されていること |
| PRE-03 | Google Sheets APIの利用権限が取得できること |
| PRE-04 | Google Books APIの利用権限が取得できること（APIキー取得済み） |
| PRE-05 | AWS環境の利用権限があること（本番デプロイ時） |
| PRE-06 | 開発・運用を行うメンバーがPython、Django、MySQLの基礎知識を持っていること |

---

### 1.3 技術スタック
| 項目 | 技術 |
|------|------|
| 言語 | Python 3.11+ |
| フレームワーク | Django 5.x |
| データベース | MySQL 8.0 |
| 外部API | Google Books API, Google Sheets API |
| インフラ（開発） | Docker, Docker Compose |
| インフラ（本番） | AWS (EC2/ECS, RDS) |
| バッチ処理 | Cron + Python script |

---

## 2. データベース設計

### 2.1 ER図（テキスト表現）
```
books (書籍マスタ)
  ├─ 1:N → rental_history (貸出履歴)
  
error_logs (エラーログ) ※独立テーブル
```

### 2.2 テーブル定義

#### books（書籍マスタ）
```sql
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_number VARCHAR(50) NOT NULL COMMENT '申請番号',
    isbn VARCHAR(13) NOT NULL COMMENT 'ISBNコード',
    title VARCHAR(255) NOT NULL COMMENT '書籍名',
    author VARCHAR(255) COMMENT '著者',
    publisher VARCHAR(255) COMMENT '出版社',
    published_date VARCHAR(50) COMMENT '出版日',
    description TEXT COMMENT '書籍概要',
    thumbnail_url VARCHAR(512) COMMENT '書影URL',
    applicant_name VARCHAR(100) NOT NULL COMMENT '申請者名',
    approver_name VARCHAR(100) NOT NULL COMMENT '承認者名',
    application_date VARCHAR(10) NOT NULL COMMENT '申請日(YYYY/MM/DD)',
    approval_date VARCHAR(10) NOT NULL COMMENT '承認日(YYYY/MM/DD)',
    price DECIMAL(10, 2) COMMENT '価格',
    status ENUM('ordered', 'available', 'rented', 'other') DEFAULT 'ordered' COMMENT 'ステータス',
    location VARCHAR(255) COMMENT '保管場所',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_isbn (isbn),
    INDEX idx_status (status),
    INDEX idx_application_number (application_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='書籍マスタ';
```

#### rental_history（貸出履歴）
```sql
CREATE TABLE rental_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL COMMENT '書籍ID',
    borrower_name VARCHAR(100) NOT NULL COMMENT '貸出人名',
    rental_date DATE NOT NULL COMMENT '貸出日',
    expected_return_date DATE NOT NULL COMMENT '返却予定日',
    actual_return_date DATE COMMENT '実際の返却日',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    INDEX idx_book_id (book_id),
    INDEX idx_borrower_name (borrower_name),
    INDEX idx_rental_date (rental_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='貸出履歴';
```

#### error_logs（エラーログ）
```sql
CREATE TABLE error_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    application_number VARCHAR(50) COMMENT '申請番号',
    isbn VARCHAR(13) COMMENT 'ISBNコード',
    error_type VARCHAR(50) NOT NULL COMMENT 'エラー種別',
    error_message TEXT NOT NULL COMMENT 'エラーメッセージ',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_application_number (application_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='エラーログ';
```

---

## 3. システム構成

### 3.1 アーキテクチャ図（テキスト表現）
```
[Google Sheets] ←→ [バッチ処理(Cron)] → [Django App] → [MySQL]
                           ↓
                   [Google Books API]
                           
[管理者] → [Webブラウザ] → [Django Admin + カスタム管理画面] → [MySQL]
```

### 3.2 Docker構成（開発環境）
```yaml
services:
  - app (Django)
  - db (MySQL)
  - nginx (Optional)
```

### 3.3 AWS構成（本番環境）
- **EC2 or ECS Fargate**: Djangoアプリケーション
- **RDS for MySQL**: データベース
- **EventBridge + Lambda or EC2 Cron**: バッチスケジューリング
- **S3**: ログ保存（オプション）
- **CloudWatch**: 監視・ログ集約

---

## 4. 機能要件詳細

### 4.1 バッチ処理（スプレッドシート連携）

#### 処理フロー
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

#### スプレッドシート列構成
| 列 | 項目 | 備考 |
|----|------|------|
| A | 申請番号 | 通し番号 |
| B | 申請者名 | |
| C | 承認者名 | 取り込み条件 |
| D | 申請日 | YYYY/MM/DD |
| E | 承認日 | YYYY/MM/DD、取り込み条件 |
| F | 書籍名 | |
| G | ISBNコード | |
| H | 価格 | |
| I | DB取り込み済み | システムが自動記入 |

#### 実行頻度
- 1時間おき（Cron: `0 * * * *`）

### 4.2 管理画面機能

#### 4.2.1 書籍一覧画面
**表示項目**
- 書影（サムネイル）
- 書籍名
- 著者
- ステータス（色分け表示）
- 現在の貸出人（rentedの場合）
- 返却予定日（rentedの場合）
- アクション（詳細/編集ボタン）

**検索・フィルター機能**
- 書籍名（部分一致）
- 著者名（部分一致）
- ISBNコード（完全一致）
- ステータス（プルダウン）
- 貸出人名（テキスト検索）

**ソート機能**
- 申請日
- 書籍名
- ステータス
- 貸出人名

**ページネーション**
- 20件/50件/100件 切り替え可能

#### 4.2.2 書籍詳細・編集画面
**表示・編集項目**
- 書籍情報
  - ISBNコード（編集可能）
  - 書籍名
  - 著者
  - 出版社
  - 出版日
  - 書籍概要
  - 書影
  - 「書籍情報を再取得」ボタン（ISBN変更後にAPI再呼び出し）
  
- 申請情報（閲覧のみ）
  - 申請番号
  - 申請者名
  - 承認者名
  - 申請日
  - 承認日
  - 価格
  
- 管理情報（編集可能）
  - ステータス（プルダウン）
  - 保管場所（フリーテキスト、任意）
  
- 貸出履歴一覧
  - 過去の貸出・返却履歴を表形式で表示

#### 4.2.3 ステータス変更機能

**パターン1: 詳細画面でのステータス変更**

```
ステータス = "available" → "rented" に変更時
  ↓
モーダルまたは入力欄が表示
  - 貸出人名（必須、手入力）
  - 返却予定日（必須、初期値：翌日）
  ↓
保存時
  - books.status = 'rented'
  - rental_historyに新規レコード作成
    - actual_return_dateはNULL
```

```
ステータス = "rented" → "available" に変更時
  ↓
確認モーダル表示
  ↓
保存時
  - books.status = 'available'
  - rental_historyの最新レコードにactual_return_date設定
```

#### 4.2.4 エラーログ閲覧画面
- error_logsテーブルの内容を一覧表示
- 申請番号、ISBN、エラー種別、エラーメッセージ、発生日時

---

## 5. 実装タスク一覧

### Phase 1: 環境構築・基盤整備 ✅ 優先度：高
- [ ] 1-1. Dockerfileの作成（Django + MySQL）
- [ ] 1-2. docker-compose.ymlの作成
- [ ] 1-3. Djangoプロジェクト初期化
- [ ] 1-4. データベース接続設定
- [ ] 1-5. マイグレーションファイル作成（books, rental_history, error_logs）
- [ ] 1-6. Google Sheets API認証設定
- [ ] 1-7. Google Books API認証設定

### Phase 2: バッチ処理実装 ✅ 優先度：高
- [ ] 2-1. Google Sheets API連携モジュール作成
- [ ] 2-2. Google Books API連携モジュール作成
- [ ] 2-3. スプレッドシート取り込みバッチスクリプト作成
- [ ] 2-4. エラーハンドリング実装
- [ ] 2-5. ログ出力機能実装
- [ ] 2-6. Cron設定ファイル作成
- [ ] 2-7. バッチ処理のテスト

### Phase 3: Django管理画面カスタマイズ ✅ 優先度：高
- [ ] 3-1. Djangoモデル定義（Book, RentalHistory, ErrorLog）
- [ ] 3-2. Django Admin基本設定
- [ ] 3-3. 書籍一覧画面のカスタマイズ
  - [ ] 検索・フィルター機能
  - [ ] ソート機能
  - [ ] ページネーション
  - [ ] 書影表示
- [ ] 3-4. 書籍詳細・編集画面のカスタマイズ
  - [ ] フォームレイアウト調整
  - [ ] ISBN再取得機能
- [ ] 3-5. ステータス変更機能実装
  - [ ] 貸出処理（モーダル/フォーム）
  - [ ] 返却処理
- [ ] 3-6. 貸出履歴表示機能
- [ ] 3-7. エラーログ閲覧画面

### Phase 4: テスト・デバッグ ✅ 優先度：中
- [ ] 4-1. 単体テスト作成
- [ ] 4-2. 統合テスト（バッチ〜管理画面）
- [ ] 4-3. エラーケーステスト
- [ ] 4-4. パフォーマンステスト

### Phase 5: デプロイ準備 ⭐ 優先度：中
- [ ] 5-1. AWS環境構築（EC2/ECS, RDS）
- [ ] 5-2. 本番用設定ファイル作成
- [ ] 5-3. デプロイスクリプト作成
- [ ] 5-4. バッチスケジューリング設定（EventBridge or Cron）
- [ ] 5-5. 監視・アラート設定（CloudWatch）

### Phase 6: ドキュメント作成 ⭐ 優先度：低
- [ ] 6-1. システム運用マニュアル
- [ ] 6-2. トラブルシューティングガイド
- [ ] 6-3. API仕様書（内部用）

---

## 6. ディレクトリ構造

```
book-management-system/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf (optional)
├── app/
│   ├── manage.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── books/
│   │   ├── __init__.py
│   │   ├── models.py (Book, RentalHistory, ErrorLog)
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   └── templates/
│   │       └── admin/
│   │           └── books/ (カスタムテンプレート)
│   ├── batch/
│   │   ├── __init__.py
│   │   ├── import_books.py (メインバッチスクリプト)
│   │   ├── google_sheets_client.py
│   │   ├── google_books_client.py
│   │   └── utils.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── requirements.txt
├── logs/
│   └── batch.log
├── credentials/
│   ├── google_sheets_credentials.json
│   └── .env (環境変数)
├── scripts/
│   ├── setup.sh
│   └── deploy.sh
└── README.md
```

---

## 7. 開発スケジュール案

| Phase | タスク | 想定工数 | 開始日 | 完了予定日 |
|-------|--------|----------|--------|-----------|
| Phase 1 | 環境構築 | 1-2日 | Day 1 | Day 2 |
| Phase 2 | バッチ処理 | 3-4日 | Day 3 | Day 6 |
| Phase 3 | 管理画面 | 5-7日 | Day 7 | Day 13 |
| Phase 4 | テスト | 2-3日 | Day 14 | Day 16 |
| Phase 5 | デプロイ | 2-3日 | Day 17 | Day 19 |
| Phase 6 | ドキュメント | 1日 | Day 20 | Day 20 |

**合計想定工数: 約3-4週間**

---

## 8. リスクと対策

| リスク | 対策 |
|--------|------|
| Google Books APIでISBN取得失敗 | ISBN編集→再取得機能実装済み |
| スプレッドシート接続エラー | リトライロジック、エラーログ記録 |
| 同時編集による競合 | Djangoの楽観的ロック機能活用 |
| バッチ処理の遅延 | 処理時間監視、必要に応じて並列化 |

---

## 9. 今後の拡張機能（Phase 2以降）

- [ ] Slack通知機能
  - 新規書籍登録通知
  - 返却期限リマインダー
  - エラー通知
- [ ] 延滞アラート機能
- [ ] 書籍レビュー・評価機能
- [ ] 統計ダッシュボード（人気書籍、貸出ランキング等）
- [ ] QRコード管理（本にQRコード貼付→スキャンで貸出・返却）
- [ ] ユーザー認証機能

---

## 10. 付録

### 10.1 Google Books API エンドポイント例
```
GET https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN_CODE}
```

**レスポンス例（抜粋）:**
```json
{
  "items": [
    {
      "volumeInfo": {
        "title": "書籍タイトル",
        "authors": ["著者名"],
        "publisher": "出版社",
        "publishedDate": "2024-01-01",
        "description": "書籍の概要...",
        "imageLinks": {
          "thumbnail": "https://..."
        }
      }
    }
  ]
}
```

### 10.2 Google Sheets API 認証設定
1. Google Cloud Consoleでプロジェクト作成
2. Google Sheets API有効化
3. サービスアカウント作成
4. 認証情報JSONファイルダウンロード
5. スプレッドシートにサービスアカウントのメールアドレスを共有

### 10.3 環境変数設定例（.env）
```bash
# Django設定
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# データベース設定
DB_NAME=book_management
DB_USER=root
DB_PASSWORD=password
DB_HOST=db
DB_PORT=3306

# Google API設定
GOOGLE_SHEETS_CREDENTIALS_PATH=/app/credentials/google_sheets_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id
GOOGLE_BOOKS_API_KEY=your-api-key

# ログ設定
LOG_LEVEL=INFO
LOG_FILE_PATH=/var/log/book-management/batch.log
```

---

**文書作成日**: 2025年10月16日  
**バージョン**: 1.0  
**作成者**: システム開発チーム
