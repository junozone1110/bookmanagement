FROM python:3.11-slim

# 環境変数の設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# requirements.txtをコピーして依存関係をインストール
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ /app/

# ログディレクトリの作成
RUN mkdir -p /var/log/book-management

# ポート8000を公開
EXPOSE 8000

# Django開発サーバーの起動
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

