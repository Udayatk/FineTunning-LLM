🧠 Gemma-2B Election Manifesto Summarizer (Fine-Tuned with Unsloth + LoRA)
This repository contains code to fine-tune Google’s gemma-2b-it model using Unsloth and LoRA with your custom dataset — specifically, political/election manifestos. The model is optimized to generate concise, objective summary responses using Retrieval-Augmented Generation (RAG)-like conversational patterns.

🚀 Features
✅ Fine-tune Gemma-2B with LoRA + QLoRA

✅ Supports system/user/model-style JSON datasets

✅ Uses transformers, trl, datasets, unsloth, and Hugging Face ecosystem

✅ Includes streamable chat interface for inference

✅ Fully reproducible and GPU-ready training pipeline

📁 Project Structure
text
.
├── manifesto_fine_tuning_data.json   # Custom dataset (chat JSON format)
├── lora_model_gemma2b_manifesto_summarizer/  # LoRA adapter output
├── training_script.py               # Main training + chat loop script
└── README.md
📦 Requirements
bash
pip install --upgrade pip
pip install "unsloth[cu124-torch260] @ git+https://github.com/unslothai/unsloth.git"
pip install "transformers>=4.38.0" "datasets>=2.18.0" "accelerate>=0.28.0" "bitsandbytes>=0.43.0" "trl>=0.8.0"
Additional Tools:

FFmpeg (optional for audio use)

huggingface-cli for model/tokenizer download

🧠 Data Format (JSON)
Your training data should be in JSON Lines format like this:

json
[
  {
    "messages": [
      { "role": "system", "content": "You summarize policies in neutral tone." },
      { "role": "user", "content": "Summarize the education agenda in Manifesto X." },
      { "role": "model", "content": "Manifesto X emphasizes free education, skill training, and funding for public schools." }
    ]
  }
]
✅ Supports alternate formats with just user and model roles.

🏋️‍♂️ Training (One Command)
bash
python training_script.py
This handles:

Loading gemma-2b-it with Unsloth

Applying QLoRA and LoRA adapters

Formatting your dataset with proper chat templates

Training and saving your model adapters

🧪 Inference Usage (Interactive)
After training, chat with your model via:

bash
python chat_inference.py
Sample session:

text
You: Summarize education policy of Manifesto A
Model: The manifesto proposes universal K-12 education with emphasis on rural inclusion and free digital devices.
💾 Output
Saves LoRA adapters to:

text
./lora_model_gemma2b_manifesto_summarizer/
Use these with any inference script or load using peft for scalable deployment.

🛠️ Customization Options
Parameter	Description	Default
max_seq_length	Max token length (Gemma supports 8192)	2048
learning_rate	Learning rate for optimizer	2e-4
batch_size	Set via per_device_train_batch_size param	1
eval_dataset	Optional eval split	10% of data
⚙️ Tech Stack
Model: Gemma 2B

Frameworks: Unsloth, PEFT, Transformers, TRL, Accelerate

Fine-tuning: LoRA + QLoRA

Chat UI: Terminal-based streaming interface

🔐 Credits / Acknowledgements
Unsloth for blazing fast fine-tuning

Google for releasing Gemma

Hugging Face ecosystem for models and datasets

📣 License
This project is intended for educational and research use only. It assumes your dataset complies with all data policies and privacy laws.

🙌 Contributing
Pull requests, dataset improvements, and feedback are welcome!

Let me know if you'd like a version for Colab, Docker, or with Streamlit web UI too!
