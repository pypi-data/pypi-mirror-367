import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, roc_curve, auc, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import matplotlib.pyplot as plt
import seaborn as sns
from hyperopt import hp, fmin, tpe, space_eval

def pick_classifier(df:pd.DataFrame, target:str, features=[], test_size=0.2, visualize=False, mode="standard", decimals=4, fold_count=6, random_state=None):
    """Finds the best classifier"""

    if random_state is not None:
        np.random.seed(random_state)
        print(f"Random Seed set: {random_state}")

    X = df.drop(target, axis=1).values
    if len(features) == 0:
        X = X[features]

    y = df[target].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
    kf = KFold(n_splits=fold_count, random_state=42, shuffle=True)
    
    mode_to_models = {
        "standard": [LogisticRegression, KNeighborsClassifier, SVC],
        "extensive": [LogisticRegression, KNeighborsClassifier, SVC, RandomForestClassifier, GradientBoostingClassifier]
    }
    
    model_names = ["logistic_regression", "k_neighbors", "SVC", "random_forest", "gradient_boosting"]
    models = {model_names[i]: model() for i, model in enumerate(mode_to_models[mode])}
    
    accuracy_scores, f1_scores, cv_results = [], [], []
    
    for model in models.values():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        cv_score = cross_val_score(model, X_train, y_train, cv=kf, scoring="roc_auc")
        
        accuracy_scores.append(str(round(accuracy, decimals)))
        f1_scores.append(str(round(f1, decimals)))
        cv_results.append(str(round(cv_score.mean(), decimals)))
    
    print(f"Model:           {' '.join(models.keys())}")
    print(f"Cross Val Score {' '.join(cv_results)}")
    print(f"Accuracy Score:  {' '.join(accuracy_scores)}")
    print(f"F1 Score:        {' '.join(f1_scores)}")
    
    choice = input("Which model to proceed?")
    while choice not in models:
        print("Please choose from the following", " ".join(models.keys()))
        choice = input("Which model to proceed?")
    print(f"\nChosen {choice}")
    
    chosen_model = models[choice]
    
    binary_models_param_grid = {
    "logistic_regression": {"C": hp.loguniform("C", np.log(0.1), np.log(100)),"penalty": hp.choice("penalty", ["l1", "l2"]), 'solver': hp.choice("solver", ['liblinear', 'saga']), "max_iter":hp.choice("max_iter", [1000])},
    "SVC": {"C": hp.loguniform("C", np.log(0.1), np.log(100)), "gamma": hp.choice("gamma", [0.1, 1, 10, 'auto']), 'kernel': hp.choice("kernel", ['linear', 'rbf', 'poly']), 'degree': hp.choice("degree", [2, 3, 4])},
    "k_neighbors": {"n_neighbors": range(1, 10)}
    }

    multiclass_models_param_grid = {
        "logistic_regression": {"C": [0.001, 0.01, 0.1, 1, 10, 100], "penalty": ["l2"], 'solver': ['newton-cg', 'sag', 'saga', 'lbfgs'], 'multi_class': ['multinomial', 'ovr']},
        "SVC": {"C": [0.001, 0.01, 0.1, 1, 10, 100], "gamma": [0.1, 1, 10, 'auto'], 'kernel': ['linear', 'rbf', 'poly'], 'degree': [2, 3, 4], 'decision_function_shape': ['ovo', 'ovr']},
        "k_neighbors": {"n_neighbors": range(1, 10)}
    }
    
    def objective_binary(params):
        model_params = {key: params[key] for key in binary_models_param_grid[choice]}
        clf = chosen_model.set_params(**model_params)
        score = cross_val_score(clf, X_train, y_train, cv=kf, scoring="roc_auc").mean()
        return 1-score
    
    def objective_multi(params):
        model_params = {key: params[key] for key in multiclass_models_param_grid[choice]}
        clf = chosen_model.set_params(**model_params)
        score = cross_val_score(clf, X_train, y_train, cv=kf, scoring="roc_auc").mean()
        return 1-score

    if df[target].unique().size <= 2:
        print("Binary Classification")
        best = fmin(fn=objective_binary, space=binary_models_param_grid[choice], algo=tpe.suggest, max_evals=100)
        best_params = space_eval(binary_models_param_grid[choice], best)
    else:
        best = fmin(fn=objective_multi, space=multiclass_models_param_grid[choice], algo=tpe.suggest, max_evals=100)
        best_params = space_eval(multiclass_models_param_grid[choice], best)

    chosen_model = chosen_model.set_params(**best_params)
    chosen_model.fit(X_train, y_train)

    res_score = cross_val_score(chosen_model, X_train, y_train).mean()

    print(f"Tuned {choice} parameters: {best_params}")
    print(f"Tuned {choice} test score: {round(res_score, decimals)}")

    if visualize:
        train_pred = chosen_model.predict(X_train)
        test_pred = chosen_model.predict(X_test)
        fig, axes = plt.subplots(1, 3, figsize=(12, 5))

        cm = confusion_matrix(y_test, test_pred)

        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
            xticklabels=["Predicted 0", "Predicted 1"],
            yticklabels=["Actual 0", "Actual 1"], ax=axes[0])

        test_probs = chosen_model.predict_proba(X_test)[:, 1]
        fpr, tpr, thresholds = roc_curve(y_test, test_probs)
        roc_auc = auc(fpr, tpr)

        sns.lineplot(x=fpr, y=tpr, color='darkorange', label='ROC curve (AUC = {:.2f})'.format(roc_auc), ax=axes[1])
        sns.lineplot(x=[0, 1], y=[0, 1], color='navy', linestyle='--', label='Random Guess', ax=axes[1])

        axes[1].set_xlim([0.0, 1.0])
        axes[1].set_ylim([0.0, 1.05])
        axes[1].set_xlabel("False Positive Rate")
        axes[1].set_xlabel("True Positive Rate")
        axes[1].set_title("Roc Curve")
        axes[1].legend(loc="lower right")

        print(chosen_model.coef_)
    
        plt.show()

    return chosen_model