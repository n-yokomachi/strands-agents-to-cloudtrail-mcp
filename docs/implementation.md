# CloudTrail開発者行動予測システム 実装計画 (検証環境版)

## プロジェクト概要
AWS CloudTrailのAPIイベントログを分析し、Claude Sonnet 4を使って開発者の作業パターンを予測・分析するシステム。Strands AgentsとMCPサーバーを活用した最新のAIエージェント技術を使用。

**検証環境のため、セキュリティより開発速度とシンプルさを優先**

## CDKスタック構成

### 1. インフラストラクチャスタック (InfrastructureStack)

#### 最小構成
- **デフォルトVPC使用**: 新規VPC作成なし
- **パブリックサブネット**: ALB配置用
- **プライベートサブネット**: Fargateタスク配置用（セキュリティ向上）
- **セキュリティグループ**: 
  - ALB用: 自宅IP限定（203.0.113.100/32:80）
  - Fargate用: ALBからの通信のみ許可（8501）

### 2. IAMスタック (IAMStack)

#### CloudTrail MCP Lambda実行ロール
- **CloudTrail読み取り権限**
  - `cloudtrail:*` (検証環境なので全開放)
- **基本権限**
  - `logs:*` (ログ全開放)
- **Lambda Web Adapter権限**
  - Function URL実行権限

#### Fargate実行ロール（Strands Agents用）
- **Bedrock推論権限**
  - `bedrock:*` (検証環境なので全開放、エージェントが推論実行)
- **ECRアクセス権限**: `ecr:*`
- **基本権限**: `logs:*`

### 3. CloudTrail MCP サーバースタック (CloudTrailMCPStack)

#### CloudTrail MCP Lambda サーバー
- **Lambda Function URL + Web Adapter構成**
  - ランタイム: Python 3.12
  - メモリ: **1024MB**（MCP サーバー + CloudTrail API処理）
  - タイムアウト: 15分（最大値、長時間分析対応）
  - 機能: MCP プロトコル処理 + CloudTrail API統合
  - 権限: CloudTrail読み取り + 基本実行権限

#### 技術構成（FastMCP + Lambda Web Adapter）
- **Lambda Web Adapter**: HTTP/HTTPSサーバー対応
- **Function URL**: RESPONSE_STREAMモードでストリーミング対応
- **FastMCP**: MCP専用のPythonライブラリ（公式MCP SDKに統合済み）
- **Streamable HTTP**: セッションレス通信でLambdaに最適

#### 依存関係
- **Lambda Layer**: AWS Lambda Web Adapter
- **Python**: FastMCP + boto3（CloudTrail API用）

### 4. アプリケーションスタック (ApplicationStack)

#### ECR Repository
- **Strands Agentsアプリケーション用**
  - イメージスキャン有効
  - ライフサイクルポリシー（最新10バージョン保持）

#### ECS Fargate Service（検証用）
- **Strands Agents実行環境**
  - CPU: 256 (0.25 vCPU)（実際のStreamlit事例に基づく）
  - メモリ: **512MB**（実際のStreamlit事例に基づく）
  - タスク数: 1（固定、検証環境のため）
  - Streamlitアプリケーション
  - **ALB不要**: ECS Service Discovery使用

#### ALB経由アクセス（自宅IP限定）
- **Application Load Balancer**
  - パブリックサブネット配置
  - **自宅IPアドレスのみ許可**（203.0.113.100/32）
  - ターゲットグループでFargateタスクへルーティング
  - アクセス方法: `http://[ALB-DNS-Name]`
  
- **ECS Fargate Service**
  - プライベートサブネット配置（セキュリティ向上）
  - ALBからの通信のみ許可
  - ヘルスチェック設定（`/healthcheck` エンドポイント）

### 5. 監視・ログスタック (MonitoringStack)

#### CloudWatch Logs
- **Lambda関数ログ**
  - 保持期間: 30日
  - ログレベル: INFO以上
- **Fargateアプリケーションログ**
  - 保持期間: 14日
  - 構造化ログ

#### CloudWatch Metrics（基本のみ）
- **基本メトリクス自動収集**
  - Lambda実行回数・エラー数
  - Fargate CPU・メモリ使用率
  - ALBリクエスト数・レスポンス時間
- **アラーム設定なし**（検証環境のため）

## 実装フェーズ

### Phase 1: 基盤構築（週1）
1. ネットワーク・IAMスタックのデプロイ
2. Lambda MCPサーバーの基本実装（FastMCP使用）
3. CloudTrail API連携テスト

### Phase 2: AI分析機能（週2）
1. Strands Agents実装（Fargateエージェント）
2. Claude Sonnet 4統合（エージェント内）
3. 行動パターン分析ロジック（エージェント内）

### Phase 3: UI・統合（週3）
1. Streamlitアプリケーション開発
2. Fargateデプロイ

### Phase 4: 監視・最適化（週4）
1. CloudWatch監視設定
2. パフォーマンスチューニング
3. セキュリティ強化

## 技術スタック詳細

### フロントエンド
- **Streamlit**: Pythonベースの迅速なUI開発

### バックエンド
- **Strands Agents**: AIエージェントオーケストレーション
- **FastMCP**: MCP専用Pythonライブラリ（Lambda Web Adapter経由）
- **Claude Sonnet 4**: 高度な分析・予測エンジン

### インフラ
- **AWS CDK**: Infrastructure as Code
- **Docker**: コンテナ化
- **GitHub Actions**: CI/CDパイプライン

## 開発環境セットアップ

### 必要なツール
- Node.js 18+ (CDK用)
- Python 3.12+ (アプリケーション用)
- Docker Desktop
- AWS CLI v2
- AWS CDK v2

### 環境変数
- AWS_REGION: ap-northeast-1
- AWS_ACCOUNT_ID: 12桁のアカウントID
- BEDROCK_MODEL_ID: Claude Sonnet 4モデルID

### ローカル開発
1. **MCPサーバーローカル実行**
   - `lambda/`ディレクトリに移動
   - `python main.py`でFastMCPサーバー起動（ポート8000）
   - FastMCPでのMCP動作確認

2. **Streamlitアプリローカル実行**
   - `app/`ディレクトリに移動
   - `streamlit run main.py`でStreamlitアプリ起動（ポート8501）
   - ブラウザでの動作確認

### Lambda MCPサーバーの実装状況
- **✅ 完了**: FastMCP v2を使用したMCPサーバー実装
- **✅ 完了**: CloudTrail APIのlookup_events統合
- **✅ 完了**: 時間範囲・ユーザー名フィルタリング対応
- **✅ 完了**: JSON形式レスポンス
- **✅ 完了**: Lambda Web Adapter対応（ポート8000）

### 実装されたMCPツール
1. **lookup_cloudtrail_events**: CloudTrailイベント履歴取得
2. **get_cloudtrail_event_names**: イベント名の集計
3. **cloudtrail://status**: サーバー状態確認（リソース）

### ディレクトリ構造
```
strands-agents_and_mcp-on-lambda/
├── app/                     # Streamlitアプリ（Fargate用）
│   ├── main.py             # Streamlitメイン
│   └── requirements.txt    # Streamlit依存関係
├── lambda/                  # Lambda MCPサーバー
│   ├── main.py             # FastMCP MCPサーバー
│   └── requirements.txt    # Lambda依存関係
├── lib/                     # CDKスタック
├── bin/                     # CDKアプリ
└── docs/                    # ドキュメント
```

## セキュリティ考慮事項

### データ保護
- CloudTrailログは機密情報を含む可能性
- 最小権限の原則でIAMロール設定
- 自宅IP限定でのアクセス制御

### アクセス制御
- **ALB経由の自宅IP限定**: 203.0.113.100/32のみ許可
- セキュリティグループでALB→Fargate通信制限
- Lambda関数URL認証なし（検証環境のため）

### 監査・コンプライアンス
- 全API呼び出しのログ記録
- CloudTrail自体の監査ログ
- データ保持期間の適切な設定

## コスト最適化

### 予想月額コスト
- **Lambda Layer 1**: $1-5（128MB、CloudTrail API呼び出しのみ）
- **Lambda Layer 2**: $1-3（128MB、MCP Bridge軽量処理）
- **Fargate**: $10-25（0.25vCPU/512MB、常時稼働1タスク）
- **ALB**: $20-25（Application Load Balancer基本料金）
- **Bedrock**: $50-200（Fargateエージェントが推論実行）
- **その他**: $10-20
- **合計**: $92-273/月（ALB追加で安定性向上）

### コスト削減策
- Fargateのオートスケーリング
- Lambdaの適切なメモリ設定
- CloudWatch Logsの保持期間最適化
- 開発環境の自動停止

## デプロイ手順

### 1. 開発環境セットアップ
- プロジェクトクローンとディレクトリ移動
- CDK環境セットアップ（npm install）
- Python環境セットアップ（pip install）
- Docker環境確認

### 2. AWS環境準備
- CDKブートストラップ実行
- Amazon Bedrock（Claude Sonnet 4）有効化確認
- ECR Repository作成権限確認
- AWS CLI認証設定確認

### 3. Streamlitアプリケーション開発
#### ローカル開発・テスト
- アプリケーションディレクトリに移動
- Streamlitローカル実行（ポート8501）
- ブラウザでの動作確認
- 基本機能テスト

#### Dockerコンテナ化
- Dockerfile作成（Python 3.9ベース）
- 依存関係管理（requirements.txt）
- Streamlitポート設定（8501）
- ヘルスチェック用ポート追加（8080）

### 4. CDKスタックデプロイ
- 全スタック一括デプロイ（`cdk deploy --all`）
- または段階的デプロイ（InfrastructureStack → IAMStack → CloudTrailMCPStack → ApplicationStack）
- デプロイ進行状況確認
- CloudFormationスタック作成確認

### 5. コンテナイメージのビルド・プッシュ
- ECRログインとDocker認証
- イメージビルドとタグ付け
- ECRリポジトリへのプッシュ
- バージョン管理（latest + commit hash）

### 6. ECS Fargate Service起動
- ECSサービスの新規デプロイ実行
- タスク定義の更新とローリングアップデート
- ヘルスチェック確認

### 7. アクセス確認
- CDK OutputからALB URLを取得
- ブラウザでStreamlitアプリにアクセス
- ヘルスチェックエンドポイント動作確認
- 基本機能テスト実行

### 8. CDKでのStreamlit URL出力設定

#### ApplicationStackにOutput追加
- ALB DNS名をCDK Outputで出力
- StreamlitアプリURL自動生成
- ヘルスチェックURL出力
- Load Balancer ARN情報

#### Streamlitアプリでのヘルスチェック対応
- Flask APIサーバーを別スレッドで起動
- `/healthcheck` エンドポイント実装
- ALBターゲットグループ用ヘルスチェック
- Streamlitとの並行実行

## 運用・保守

### 基本チェック項目
- [ ] アプリケーションの動作確認
- [ ] コスト使用量確認
- [ ] ログ出力確認

### 定期メンテナンス
- [ ] 不要リソースの削除
- [ ] セキュリティ設定見直し
- [ ] 依存関係アップデート

この実装計画で、最新のAI技術を使った実用的なCloudTrail分析システムが構築できます！💕 