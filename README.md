# 🤖 Strands Agents + Streamlit on ECS

Amazon Bedrock Claude 3.5 Sonnet v2を使ったシンプルなAIチャットアプリです！

## ✨ 特徴

- **Strands Agents**: AWS製のシンプルなAIエージェントSDK
- **Claude 3.5 Sonnet v2**: Amazon Bedrockの最新モデル
- **Streamlit**: 美しいWebUI
- **ECS Fargate**: サーバーレスコンテナ実行
- **Application Load Balancer**: 高可用性

## 🚀 クイックスタート

### 1. 環境設定

```bash
cp env.example .env
# .envを編集: AWS_ACCOUNT_ID と HOME_IP_ADDRESS を設定
```

### 2. デプロイ

```bash
npm install
./app/deploy.sh
```

## 📁 プロジェクト構造

```
.
├── app/
│   ├── main.py          # Streamlitアプリ
│   ├── requirements.txt # Python依存関係
│   ├── Dockerfile       # コンテナ設定
│   └── deploy.sh        # デプロイスクリプト
├── lib/
│   ├── config.ts           # 設定管理
│   ├── infrastructure-stack.ts # VPC, セキュリティグループ
│   ├── iam-stack.ts           # IAMロール
│   └── application-stack.ts   # ECS, ALB, ECR
└── bin/
    └── app.ts           # CDKメインアプリ
```

## 🔧 主要設定

| 設定項目 | デフォルト値 | 説明 |
|---------|-------------|------|
| `BEDROCK_MODEL_ID` | `anthropic.claude-3-5-sonnet-20241022-v2:0` | Bedrockモデル |
| `AWS_REGION` | `ap-northeast-1` | AWSリージョン |
| `ECR_REPOSITORY_NAME` | `strands-app` | ECRレポジトリ名 |
| `ECS_CLUSTER_NAME` | `strands-cluster` | ECSクラスター名 |

## 🛡️ セキュリティ

- ALBへのアクセスは設定したIPアドレスのみ
- ECSタスクはBedrockとCloudWatchLogsのみアクセス可能
- インターネットゲートウェイ経由でのアウトバウンド通信

## 💡 使い方

1. デプロイ完了後に表示されるALB URLにアクセス
2. チャット画面でClaude 3.5 Sonnet v2と対話
3. サイドバーでモデル情報確認・チャット履歴クリア

## 🧹 クリーンアップ

```bash
npm run destroy
```

## 📊 アーキテクチャ

```
Internet -> ALB -> ECS Fargate -> Bedrock Claude 3.5 Sonnet v2
```

---

**💖 シンプル・最小構成・エラーハンドリングなし**のコンセプトで作成されています！
