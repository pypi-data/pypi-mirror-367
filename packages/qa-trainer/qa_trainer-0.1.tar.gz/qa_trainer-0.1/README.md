# qa_trainer

A simple Python package to fine-tune **question-answering models** using user feedback data and **Optuna** for hyperparameter optimization.

This is built on top of [SimpleTransformers](https://github.com/ThilinaRajapakse/simpletransformers) and supports any HuggingFace-compatible QA model like BERT, RoBERTa, etc.

---

## 🚀 Features

- Accepts feedback-based QA data (`question`, `answer`, `feedback`)
- Converts data into SQuAD format
- Uses Optuna to optimize `learning_rate`, `batch_size`, and `epochs`
- Saves the fine-tuned model automatically
- Super simple API: just call a function with 3 parameters

---

## 🧠 Installation

```bash
pip install qa_trainer
