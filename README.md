
- [English](README-en.md)
- [日本語 (Japanese)](README-jp.md)

---

本项目使用千问模型构建一个本地的物理专家。你也可以根据自己的需求，修改`prompt.py`中的提示词，构建特定领域的大语言模型。

### 环境配置
- cd backend
- conda create -n local-qwen python=3.9 
- conda activate local-qwen
- pip instlal -r requirements.txt
- go mod init goService
- go get github.com/google/uuid
- go get github.com/rs/cors

### 下载模型
- cd download
- python qw_model_download.py
您可以修改`qw_model_download.py`中的模型存储路径为您自己的路径，并相应地修改`config/config.ini`中读取模型的路径

### 模型微调
这里以物理专家为例，让大模型自动生成用于微调的数据集，然后使用该数据集进行微调。你也可以使用任何其他数据集进行微调。
- cd backend/fine_tuning
- python prepare_data.py
- python qw_fine_tuning.py
此时，在`fine_tuning/output`中会生成相应的模型文件

### 启动后端
- cd backend
- python wsgi.py
- go run main.go

#### 启动前端
- cd frontend
- npm install
- npm run dev

如有任何问题，欢迎随时提issue
如果您觉得本项目对您有帮助，考虑请我喝杯咖啡吗？
<a href="https://buymeacoffee.com/johncachy" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-red.png" alt="Buy Me A Coffee" width="150" ></a>
