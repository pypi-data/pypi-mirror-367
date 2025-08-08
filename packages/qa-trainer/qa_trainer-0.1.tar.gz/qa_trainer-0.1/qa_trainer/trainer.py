import json
import logging
import optuna
from simpletransformers.question_answering import QuestionAnsweringModel, QuestionAnsweringArgs

logging.basicConfig(level=logging.INFO)

def load_feedback_data(path):
    with open(path, "r") as f:
        raw_data = json.load(f)
    return [ex for ex in raw_data if ex["feedback"] > 0]

def convert_to_squad_format(data):
    squad_data = []
    for i, entry in enumerate(data):
        context = entry["answer"]
        question = entry["question"]
        answer_text = entry["answer"]
        squad_data.append({
            "context": context,
            "qas": [{
                "id": str(i),
                "question": question,
                "is_impossible": False,
                "answers": [{
                    "text": answer_text,
                    "answer_start": context.find(answer_text)
                }]
            }]
        })
    return squad_data

def build_model_args(trial=None, output_dir="outputs/optuna_trial", overwrite=True):
    args = QuestionAnsweringArgs()
    args.reprocess_input_data = True
    args.overwrite_output_dir = overwrite
    args.output_dir = output_dir
    args.no_cache = True
    args.use_multiprocessing = False

    if trial:
        args.num_train_epochs = trial.suggest_int("num_train_epochs", 1, 4)
        args.learning_rate = trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True)
        args.train_batch_size = trial.suggest_categorical("train_batch_size", [4, 8, 16])
        args.eval_batch_size = args.train_batch_size
    return args

def train_with_feedback(feedback_data_path, model_type, model_path):
    # Step 1: Load and preprocess data
    feedback_data = load_feedback_data(feedback_data_path)
    train_data = convert_to_squad_format(feedback_data)

    # Step 2: Optimize with Optuna
    def objective(trial):
        model_args = build_model_args(trial)
        model = QuestionAnsweringModel(
            model_type=model_type,
            model_name=model_path,
            args=model_args,
            use_cuda=False
        )
        model.train_model(train_data)
        result, *_ = model.eval_model(train_data)
        return result["f1"]

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=5)

    print("✅ Best Hyperparameters:")
    print(study.best_trial.params)

    # Step 3: Retrain final model
    best_args = build_model_args(output_dir="fine_tuned_model", overwrite=False)
    best_args.num_train_epochs = study.best_trial.params["num_train_epochs"]
    best_args.learning_rate = study.best_trial.params["learning_rate"]
    best_args.train_batch_size = study.best_trial.params["train_batch_size"]
    best_args.eval_batch_size = best_args.train_batch_size
    best_args.save_model_every_epoch = False

    final_model = QuestionAnsweringModel(
        model_type=model_type,
        model_name=model_path,
        args=best_args,
        use_cuda=False
    )
    final_model.train_model(train_data)

    # Step 4: Save final model
    final_model.save_model("fine_tuned_model")

    print("🎉 Model training completed and saved to 'fine_tuned_model'")
