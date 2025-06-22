# CloudTrail開発者行動予測システム

AWS CloudTrailのAPIイベントログを分析し、Claude Sonnet 4を使って開発者の作業パターンを予測・分析するシステム。Strands AgentsとMCPサーバーを活用した最新のAIエージェント技術を使用。

## 🚀 プロジェクト概要

- **フロントエンド**: Streamlit (Python)
- **バックエンド**: Strands Agents + MCP Lambda サーバー
- **AI**: Claude Sonnet 4 (Amazon Bedrock)
- **インフラ**: AWS CDK (TypeScript)
- **コンテナ**: Docker + Amazon ECS Fargate

## 📋 前提条件

- Node.js 18+
- Python 3.12+
- Docker Desktop
- AWS CLI v2
- AWS CDK v2

## 🔧 セットアップ

### 1. リポジトリクローン

```bash
git clone <repository-url>
cd cloudtrail-behavior-prediction
```

### 2. 環境変数設定

```bash
# env.exampleをコピーして.envファイルを作成
cp env.example .env

# .envファイルを編集して実際の値を設定
vi .env
```

**重要**: `.env`ファイルには機密情報が含まれるため、Gitにコミットしないでください。

### 3. 依存関係インストール

```bash
# CDK依存関係
npm install

# Python依存関係（Streamlitアプリ用）
pip install -r requirements.txt
```

### 4. AWS環境準備

```bash
# CDKブートストラップ
cdk bootstrap

# Amazon Bedrock（Claude Sonnet 4）の有効化
# AWSコンソールから手動で設定
```

## 🚀 デプロイ

### 1. 全スタック一括デプロイ

```bash
npm run deploy
```

### 2. 段階的デプロイ（推奨）

```bash
cdk deploy InfrastructureStack
cdk deploy SimpleIAMStack
cdk deploy LambdaMCPStack
cdk deploy ApplicationStack
cdk deploy MonitoringStack
```

### 3. Streamlitアプリのデプロイ

```bash
# ECRログイン
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin <ACCOUNT-ID>.dkr.ecr.ap-northeast-1.amazonaws.com

# Dockerイメージビルド・プッシュ
cd fargate/strands-app
docker build -t strands-app .
docker tag strands-app:latest <ACCOUNT-ID>.dkr.ecr.ap-northeast-1.amazonaws.com/strands-app:latest
docker push <ACCOUNT-ID>.dkr.ecr.ap-northeast-1.amazonaws.com/strands-app:latest

# ECSサービス更新
aws ecs update-service --cluster strands-cluster --service strands-service --force-new-deployment
```

## 🔒 セキュリティ

### 環境変数管理

- ✅ `.env`: ローカル開発用（Gitで除外）
- ✅ `env.example`: サンプル設定（Gitで管理）
- ❌ **絶対にコミットしないもの**: AWS認証情報、IPアドレス、シークレット

### アクセス制御

- 自宅IPアドレス限定でのALBアクセス
- IAMロールによる最小権限の原則
- VPCプライベートサブネットでのFargate実行

## 📊 アーキテクチャ

```
Internet
    ↓ (自宅IPのみ)
Application Load Balancer
    ↓
ECS Fargate (Streamlit + Strands Agents)
    ↓
Lambda MCP Bridge
    ↓
Lambda CloudTrail API
    ↓
AWS CloudTrail
```

## 🛠️ 開発

### ローカル開発

```bash
# Streamlitアプリ
cd fargate/strands-app
streamlit run app.py

# Lambda関数（MCP）
cd lambda/mcp-server
python app.py
```

### CDKコマンド

```bash
npm run build     # TypeScriptコンパイル
npm run watch     # 監視モード
npm run test      # テスト実行
npm run synth     # CloudFormationテンプレート生成
npm run diff      # 差分確認
npm run deploy    # デプロイ
npm run destroy   # 削除
```

## 📝 TODO

- [ ] Lambda関数の実装（MCP、CloudTrail API）
- [ ] Streamlitアプリの実装（Strands Agents統合）
- [ ] Dockerfileの作成
- [ ] CI/CDパイプライン設定
- [ ] テストコード追加

## 🤝 コントリビューション

1. Forkしてブランチ作成
2. 変更をコミット
3. プルリクエスト作成

## 📄 ライセンス

MIT License

## 🆘 トラブルシューティング

### よくある問題

1. **CDKデプロイエラー**: AWS認証情報とリージョン設定を確認
2. **Streamlitアクセス不可**: セキュリティグループとIPアドレス設定を確認
3. **Lambda実行エラー**: IAMロール権限を確認

### サポート

Issue作成またはDiscussionで質問してください。

