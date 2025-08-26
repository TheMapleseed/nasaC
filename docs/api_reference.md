# NASA C Code Compliance API Reference

## Overview

This document provides the API reference for the NASA C Code Compliance ML training and evaluation system. The system consists of several components that work together to train machine learning models and evaluate C code for compliance with NASA standards.

## Core Components

### 1. Compliance Trainer (`ml_models/train_compliance_model.py`)

The main training script that trains both traditional ML and neural network models for NASA C code compliance.

#### Usage

```bash
python train_compliance_model.py [OPTIONS]
```

#### Options

- `--data-dir`: Directory containing training data (default: `../training_data`)
- `--output-dir`: Directory to save trained models (default: `./trained_models`)
- `--model-type`: Type of model to train (`both`, `traditional`, `neural`)
- `--config-file`: Training configuration file (default: `./training_config.json`)

#### Example

```bash
# Train both traditional ML and neural network models
python train_compliance_model.py --data-dir ../training_data --model-type both

# Train only traditional ML model
python train_compliance_model.py --model-type traditional --output-dir ./models
```

#### Configuration

The training configuration is defined in `training_config.json`:

```json
{
  "model_config": {
    "model_name": "microsoft/codebert-base",
    "max_length": 512,
    "num_classes": 5
  },
  "training_params": {
    "learning_rate": 2e-5,
    "batch_size": 16,
    "epochs": 10
  }
}
```

### 2. Compliance Evaluator (`ml_models/evaluate_compliance.py`)

Evaluates C code for compliance using trained ML models.

#### Usage

```bash
python evaluate_compliance.py [OPTIONS]
```

#### Options

- `--code-file`: Path to C code file
- `--code-string`: C code as string
- `--models-dir`: Directory containing trained models (default: `./trained_models`)
- `--output-file`: Output file for report

#### Example

```bash
# Evaluate code from file
python evaluate_compliance.py --code-file sample.c --output-file report.txt

# Evaluate code string
python evaluate_compliance.py --code-string "int main() { return 0; }"
```

### 3. Compliance Checker (`tools/compliance_checker.py`)

Standalone tool for checking C code compliance without requiring trained ML models.

#### Usage

```bash
python compliance_checker.py [OPTIONS]
```

#### Options

- `--code-file`: Path to C code file
- `--code-string`: C code as string
- `--output-file`: Output file for report
- `--json`: Output results in JSON format

#### Example

```bash
# Check compliance and generate report
python compliance_checker.py --code-file sample.c --output-file compliance_report.txt

# Check compliance and output JSON
python compliance_checker.py --code-string "int main() { return 0; }" --json
```

## API Classes and Methods

### ComplianceTrainer Class

Main trainer class for NASA C compliance models.

#### Constructor

```python
ComplianceTrainer(config: Dict[str, Any])
```

**Parameters:**
- `config`: Training configuration dictionary

#### Methods

##### `load_training_data(data_dir: str) -> Tuple[List[Dict], List[Dict]]`

Loads training data from directory.

**Parameters:**
- `data_dir`: Directory containing training data

**Returns:**
- Tuple of (compliant_data, non_compliant_data)

##### `prepare_features(data: List[Dict]) -> pd.DataFrame`

Extracts features from code samples for traditional ML.

**Parameters:**
- `data`: List of code sample dictionaries

**Returns:**
- DataFrame with extracted features

##### `train_traditional_ml(X_train, y_train, X_test, y_test) -> RandomForestClassifier`

Trains traditional ML model (Random Forest).

**Parameters:**
- `X_train`: Training features
- `y_train`: Training labels
- `X_test`: Test features
- `y_test`: Test labels

**Returns:**
- Trained Random Forest classifier

##### `train_neural_network(train_data, val_data)`

Trains neural network model.

**Parameters:**
- `train_data`: Training data
- `val_data`: Validation data

##### `save_model(model, output_dir: str, model_type: str)`

Saves trained model.

**Parameters:**
- `model`: Trained model
- `output_dir`: Output directory
- `model_type`: Type of model ('random_forest' or 'neural_network')

### ComplianceEvaluator Class

Evaluates C code for NASA compliance using trained models.

#### Constructor

```python
ComplianceEvaluator(models_dir: str)
```

**Parameters:**
- `models_dir`: Directory containing trained models

#### Methods

##### `extract_features(code: str) -> Dict[str, Any]`

Extracts features from C code for analysis.

**Parameters:**
- `code`: C code string

**Returns:**
- Dictionary of extracted features

##### `check_power_of_10_rules(code: str) -> List[Dict[str, Any]]`

Checks code against NASA Power of 10 rules.

**Parameters:**
- `code`: C code string

**Returns:**
- List of rule violations

##### `predict_compliance(code: str) -> Dict[str, Any]`

Predicts compliance using trained models.

**Parameters:**
- `code`: C code string

**Returns:**
- Dictionary with compliance predictions and violations

##### `generate_report(code: str, result: Dict[str, Any]) -> str`

Generates a detailed compliance report.

**Parameters:**
- `code`: C code string
- `result`: Compliance analysis result

**Returns:**
- Formatted compliance report string

### NASAComplianceChecker Class

Standalone compliance checker without ML models.

#### Constructor

```python
NASAComplianceChecker()
```

#### Methods

##### `load_code(code: str)`

Loads code for analysis.

**Parameters:**
- `code`: C code string

##### `check_all_rules() -> List[Violation]`

Checks all NASA coding standards.

**Returns:**
- List of Violation objects

##### `calculate_compliance_score() -> int`

Calculates overall compliance score.

**Returns:**
- Compliance score (0-100)

##### `get_compliance_level() -> str`

Gets compliance level based on score.

**Returns:**
- Compliance level string

##### `generate_report() -> str`

Generates compliance report.

**Returns:**
- Formatted compliance report string

## Data Structures

### Violation Class

Represents a coding standard violation.

```python
@dataclass
class Violation:
    rule_id: str
    rule_name: str
    description: str
    severity: Severity
    line_number: int
    suggestion: str
    code_snippet: str = ""
```

### Training Data Format

Training data should be in JSON format with the following structure:

```json
{
  "code_sample": "C code string",
  "compliance_score": 95,
  "compliance_level": "fully_compliant",
  "violations": [],
  "annotations": {
    "function_count": 3,
    "line_count": 65,
    "complexity_score": 3,
    "nesting_depth": 3,
    "variable_count": 8,
    "pointer_count": 4,
    "loop_count": 1,
    "conditional_count": 6
  },
  "tags": ["sensor_processing", "data_validation"],
  "difficulty": "intermediate"
}
```

## Error Handling

All API methods include proper error handling and logging. Errors are logged using Python's logging module and appropriate error messages are returned to the caller.

## Performance Considerations

- **Traditional ML**: Fast training and inference, good for rule-based violations
- **Neural Network**: Slower training, better for complex pattern recognition
- **Compliance Checker**: Fastest option, no ML model loading required

## Dependencies

### Required Python Packages

- `numpy>=1.21.0`
- `pandas>=1.3.0`
- `scikit-learn>=1.0.0`
- `torch>=1.9.0`
- `transformers>=4.11.0`
- `click>=8.0.0`
- `rich>=10.0.0`

### Optional Dependencies

- `tensorboard` for training visualization
- `wandb` for experiment tracking
- `joblib` for model serialization

## Examples

### Training a Model

```python
from ml_models.train_compliance_model import ComplianceTrainer

# Load configuration
config = {
    'model_name': 'microsoft/codebert-base',
    'learning_rate': 2e-5,
    'batch_size': 16,
    'epochs': 10
}

# Initialize trainer
trainer = ComplianceTrainer(config)

# Load data
compliant_data, non_compliant_data = trainer.load_training_data('./training_data')

# Train models
if compliant_data and non_compliant_data:
    all_data = compliant_data + non_compliant_data
    train_data, val_data = train_test_split(all_data, test_size=0.2)
    
    # Train neural network
    trainer.train_neural_network(train_data, val_data)
    trainer.save_model(None, './models', 'neural_network')
```

### Evaluating Code

```python
from ml_models.evaluate_compliance import ComplianceEvaluator

# Initialize evaluator
evaluator = ComplianceEvaluator('./trained_models')

# Evaluate code
code = """
int main() {
    int x = 5;
    return x;
}
"""

result = evaluator.predict_compliance(code)
report = evaluator.generate_report(code, result)
print(report)
```

### Standalone Compliance Checking

```python
from tools.compliance_checker import NASAComplianceChecker

# Initialize checker
checker = NASAComplianceChecker()

# Load and check code
checker.load_code(code)
violations = checker.check_all_rules()

# Generate report
report = checker.generate_report()
print(report)
```

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure trained models exist in the specified directory
2. **Memory Issues**: Reduce batch size for large code samples
3. **Training Failures**: Check training data format and configuration
4. **Performance Issues**: Use GPU if available for neural network training

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the training data format
3. Verify all dependencies are installed
4. Check the compliance rules documentation
