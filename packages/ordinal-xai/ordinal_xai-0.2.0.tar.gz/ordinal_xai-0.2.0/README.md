# Ordinal XAI

A Python package for explainable ordinal regression models and interpretation methods.

## Overview

This package provides a comprehensive suite of ordinal regression models and interpretation methods, designed to handle ordinal data while providing transparent and interpretable results. The implementation follows scikit-learn's API design, making it easy to integrate with existing machine learning workflows.

## Features

### Models

1. **Cumulative Link Model (CLM)**
   - Supports both logit and probit link functions
   - Handles categorical and numerical features automatically
   - Provides probability estimates for each class

2. **Ordinal Neural Network (ONN)**
   - Neural network architecture for ordinal regression
   - Configurable hidden layers
   - Supports various output layers and loss functions
   - Parameters like learning rate, batch size, dropout, etc. can be tuned
   - Automatic GPU acceleration when available
   - Early stopping to prevent overfitting

3. **Ordinal Binary Decomposition (OBD)**
   - Decomposes ordinal problem into binary classification tasks
   - Supports two decomposition strategies:
     - One-vs-following: Each class vs all higher classes
     - One-vs-next: Each class vs next class only
   - Multiple base classifier options:
     - Logistic Regression
     - SVM
     - Random Forest
     - XGBoost
   - Base classifier parameters can be tuned

4. **Ordinal Gradient Boosting (OGBoost)**
   - Gradient Boosting implementation for ordinal regression
   - Based on the ogboost.GradientBoostingOrdinal model
   - Supports standard gradient boosting parameters:
     - n_estimators: Number of boosting stages
     - learning_rate: Shrinks the contribution of each tree
     - max_depth: Maximum depth of the individual trees
     - min_samples_split: Minimum samples required to split a node
   - Handles both categorical and numerical features
   - Provides feature importance scores

The models provided in this package are only examples. The interpretation methods are model-agnostic and designed to work with any ordinal regression model. Necessary requirements for custom models are that they implement the BaseOrdinalModel and sklearn BaseEstimator interfaces.

### Interpretation Methods

1. **Feature Effects Analysis**
   - **Partial Dependence Plots (PDP)**
     - Shows average effect of features on predictions
     - Handles both categorical and numerical features
     - Automatic subplot arrangement
   - **PDP with Probabilities (PDPProb)**
     - Visualizes average probability distributions across feature values
     - Shows class probability changes
     - Detailed probability annotations
   - **Individual Conditional Expectation (ICE)**
     - Analyzes individual instance behavior
     - Shows heterogeneous effects across samples
     - Displays either entire population or individual instances (recommended)
   - **ICE with Probabilities (ICEProb)**
     - Visualizes individual probability distributions across feature values
     - Shows class probability changes per instance
     - Detailed probability annotations at original values
     - Displays either entire population or individual instances (recommended)

2. **Feature Importance Analysis**
   - **Permutation Feature Importance (PFI)**
     - Global feature importance through permutation
     - Multiple evaluation metrics support, subset can be specified
     - Handles both categorical and numerical features
     - Subset of features to perform analysis on can be specified
     - Visualizes feature importance scores in a bar plot
   - **Leave-One-Covariate-Out (LOCO)**
     - Global feature importance through feature removal and refitting
     - Uses train - test split to fit the models and evaluate performance
     - Supports multiple evaluation metrics, subset can be specified
     - Visualizes feature importance scores in a bar plot

3. **Local Explanations**
   - **Local Interpretable Model-agnostic Explanations (LIME)**
     - Provides local explanations for individual predictions
     - Supports both logistic regression and decision tree surrogate models
     - Multiple sampling strategies (grid, uniform, permutation)
     - Customizable kernel functions for sample weighting
     - Visualizes feature importance through coefficients or tree plot

### Datasets

The package includes several benchmark datasets for ordinal regression:

1. **Wine Quality** ([winequality.csv](https://archive.ics.uci.edu/dataset/186/wine+quality))
   - Combined dataset of red and white wines
   - 6499 samples, 12 features
   - Separate datasets available for red (winequality-red.csv) and white (winequality-white.csv) wines
   - Ordinal target: 3-9 (wine quality rating)
   - Features include physicochemical properties (acidity, sugar, alcohol, etc.)

2. **Student Performance** ([student-mat.csv](https://archive.ics.uci.edu/dataset/320/student+performance), [student-por.csv](https://archive.ics.uci.edu/dataset/320/student+performance))
   - Two datasets: Mathematics and Portuguese
   - Mathematics: 395 samples, 33 features
   - Portuguese: 649 samples, 33 features
   - Ordinal targets: G1, G2, G3 (grades in three periods)
   - Features include demographic, social, and educational factors
   - Mixed numerical and categorical features

3. **Abalone** ([abalone.csv](https://archive.ics.uci.edu/dataset/1/abalone))
   - 4,177 samples, 8 features
   - Predicts the age of abalone from physical measurements
   - Features include length, diameter, height, and various weight measurements
   - Target variable 'Rings' represents age (1-29)

4. **Automobile** ([automobile.csv](https://www.kaggle.com/datasets/a165079/automobilecsv))
   - 205 samples, 26 features
   - Predicts automobile price based on various specifications
   - Mixed numerical and categorical features
   - Features include make, fuel-type, engine-size, horsepower, etc.

5. **Balance Scale** ([balance_scale.csv](https://archive.ics.uci.edu/dataset/12/balance+scale))
   - 625 samples, 4 features
   - Predicts balance scale state (left, balanced, right)
   - Simple dataset useful for testing ordinal classification

6. **Car Evaluation** ([car_evaluation.csv](https://archive.ics.uci.edu/dataset/19/car+evaluation))
   - 1,728 samples, 6 features
   - Predicts car acceptability (unacc, acc, good, vgood)
   - All features are categorical

7. **FI Test Dataset** (FI_test.csv)
   - Synthetic benchmark for feature importance methods
   - 1,000 samples, 10 features
   - First 5 features have predefined importance: [1.0, 0.8, 0.4, 0.2, 0.1]
   - Last 5 features are irrelevant noise variables
   - Includes both clean (y) and noisy (y_noisy) target variables
   - Designed to evaluate feature importance ranking and robustness to label noise

8. **Dummy Dataset** (dummy.csv)
   - 1,000 samples of synthetic data
   - Used for testing and demonstration purposes
   - Contains synthetic data with known patterns
   - Labels represent a health risk level influenced by health and gender
   - Latent variable: 0.006*age + 0.0005*height + 0.3*gender_w + 0.05*normal(0,1)
   - Ranks generated by creating 3 equal-sized buckets based on the latent variable

## Installation

```bash
pip install ordinal-xai
```

## Quick Start

```python
from ordinal_xai.models import CLM, ONN, OBD, OGBoost
from ordinal_xai.interpretation import LIME, LOCO, ICE, ICEProb, PDP, PDPProb, PFI
import pandas as pd
import numpy as np

# Create sample data
X = pd.DataFrame(np.random.randn(100, 5))
y = pd.Series(np.random.randint(0, 3, 100))

# Initialize and train model
model = CLM(link='logit')
model.fit(X, y)

# Make predictions
predictions = model.predict(X)
probabilities = model.predict_proba(X)

# Generate explanations
# Feature Effects
pdp = PDP(model, X, y)
pdp_effects = pdp.explain(features=['feature1', 'feature2'], plot=True)

pdp_prob = PDPProb(model, X, y)
pdp_prob_effects = pdp_prob.explain(features=['feature1', 'feature2'], plot=True)

ice = ICE(model, X, y)
ice_effects = ice.explain(features=['feature1', 'feature2'], plot=True)

ice_prob = ICEProb(model, X, y)
ice_prob_effects = ice_prob.explain(features=['feature1', 'feature2'], plot=True)

# Feature Importance
pfi = PFI(model, X, y)
pfi_importance = pfi.explain(plot=True)

loco = LOCO(model, X, y)
loco_importance = loco.explain(plot=True)

# Local Explanations
lime = LIME(model, X, y)
lime_explanation = lime.explain(observation_idx=0, plot=True)
```

## Documentation

For detailed documentation, including API reference and examples, visit our [documentation page](https://ordinal-xai.readthedocs.io/).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
