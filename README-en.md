# Local-Qwen

This project uses the Qwen model to build a local physics expert. You can also modify the prompts in `prompt.py` to build a large language model for specific domains.

### Environment Setup
- cd backend
- conda create -n local-qwen python=3.9 
- conda activate local-qwen
- pip install -r requirements.txt
- go mod init goService
- go get github.com/google/uuid
- go get github.com/rs/cors

### Download Model
- cd download
- python qw_model_download.py
You can modify the model storage path in `qw_model_download.py` to your own path and accordingly modify the path to read the model in `config/config.ini`.

### Model Fine-Tuning
Here, we take the physics expert as an example to let the large model automatically generate a dataset for fine-tuning, and then use this dataset for fine-tuning. You can also use any other dataset for fine-tuning.
- cd backend/fine_tuning
- python prepare_data.py
- python qw_fine_tuning.py
At this point, the corresponding model files will be generated in `fine_tuning/output`.

### Start Backend
- cd backend
- python wsgi.py
- go run main.go

#### Start Frontend
- cd frontend
- npm install
- npm run dev

If you have any questions, feel free to open an issue.
If you find this project helpful, consider buying me a coffee?
<a href="https://buymeacoffee.com/johncachy" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-red.png" alt="Buy Me A Coffee" width="150" ></a>
