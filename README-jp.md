# Local-Qwen

このプロジェクトは、Qwenモデルを使用してローカルの物理学専門家を構築します。`prompt.py`のプロンプトを変更して、特定の分野の大規模言語モデルを構築することもできます。

### 環境設定
- cd backend
- conda create -n local-qwen python=3.9 
- conda activate local-qwen
- pip install -r requirements.txt
- go mod init goService
- go get github.com/google/uuid
- go get github.com/rs/cors

### モデルのダウンロード
- cd download
- python qw_model_download.py
`qw_model_download.py`のモデル保存パスを自分のパスに変更し、`config/config.ini`のモデル読み込みパスもそれに応じて変更できます。

### モデルの微調整
ここでは、物理学専門家を例に、大規模モデルが自動的に微調整用のデータセットを生成し、そのデータセットを使用して微調整を行います。他のデータセットを使用して微調整することもできます。
- cd backend/fine_tuning
- python prepare_data.py
- python qw_fine_tuning.py
この時点で、`fine_tuning/output`に対応するモデルファイルが生成されます。

### バックエンドの起動
- cd backend
- python wsgi.py
- go run main.go

#### フロントエンドの起動
- cd frontend
- npm install
- npm run dev

何か質問があれば、いつでもissueを開いてください。
このプロジェクトが役に立ったと感じたら、コーヒーをおごっていただけますか？
<a href="https://buymeacoffee.com/johncachy" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-red.png" alt="Buy Me A Coffee" width="150" ></a>
