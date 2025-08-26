# NASA C Code Compliance ML System - Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying and using the NASA C Code Compliance ML system. The system enables machine learning models to learn and enforce NASA's safety-critical coding standards for C programming.

## System Architecture

The system consists of three main components:

1. **Training Infrastructure**: ML model training with both traditional and neural network approaches
2. **Evaluation Engine**: Compliance assessment using trained models
3. **Standalone Checker**: Rule-based compliance checking without ML models

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **Memory**: Minimum 8GB RAM (16GB+ recommended for training)
- **Storage**: 2GB+ free space for models and data
- **GPU**: Optional but recommended for neural network training

### Software Dependencies

- Python 3.8+
- pip or conda package manager
- Git (for cloning the repository)

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd nasaC
```

### Step 2: Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv nasa_env
source nasa_env/bin/activate  # On Windows: nasa_env\Scripts\activate

# Or using conda
conda create -n nasa_env python=3.9
conda activate nasa_env
```

### Step 3: Install Dependencies

```bash
# Install ML training dependencies
cd ml_models
pip install -r requirements.txt

# Install additional tools
cd ../tools
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Test basic functionality
python -c "import torch; import transformers; print('Installation successful')"
```

## Configuration

### Training Configuration

The training system uses `ml_models/training_config.json` for configuration:

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

**Key Configuration Options:**

- **model_name**: Pre-trained model to use (recommended: microsoft/codebert-base)
- **batch_size**: Adjust based on available memory
- **epochs**: Training iterations (increase for better accuracy)
- **learning_rate**: Learning rate for optimization

### Data Configuration

Ensure your training data follows the structure:

```
training_data/
├── compliant_examples/
│   ├── example_001.json
│   └── example_002.json
├── non_compliant_examples/
│   ├── example_001.json
│   └── example_002.json
└── dataset_metadata.json
```

## Usage

### 1. Training ML Models

#### Basic Training

```bash
cd ml_models

# Train both traditional ML and neural network models
python train_compliance_model.py --data-dir ../training_data --model-type both

# Train only traditional ML model (faster)
python train_compliance_model.py --model-type traditional

# Train only neural network model
python train_compliance_model.py --model-type neural
```

#### Advanced Training Options

```bash
# Custom output directory
python train_compliance_model.py --output-dir ./custom_models

# Custom configuration file
python train_compliance_model.py --config-file ./custom_config.json

# Train with specific data directory
python train_compliance_model.py --data-dir /path/to/custom/data
```

#### Training Output

Training creates:
- `trained_models/random_forest_model.joblib` (traditional ML)
- `trained_models/neural_network_model.pt` (neural network)
- Training logs and metrics

### 2. Evaluating Code Compliance

#### Using Trained Models

```bash
cd ml_models

# Evaluate code file
python evaluate_compliance.py --code-file ../sample.c

# Evaluate code string
python evaluate_compliance.py --code-string "int main() { return 0; }"

# Save report to file
python evaluate_compliance.py --code-file ../sample.c --output-file report.txt
```

#### Standalone Compliance Checking

```bash
cd tools

# Check compliance without ML models
python compliance_checker.py --code-file ../sample.c

# Generate JSON output
python compliance_checker.py --code-file ../sample.c --json

# Save report
python compliance_checker.py --code-file ../sample.c --output-file compliance.txt
```

### 3. Batch Processing

#### Process Multiple Files

```bash
#!/bin/bash
# batch_check.sh

for file in *.c; do
    echo "Processing $file..."
    python ../tools/compliance_checker.py --code-file "$file" --output-file "${file%.c}_report.txt"
done
```

#### Generate Training Data

```bash
#!/bin/bash
# generate_training_data.sh

# Process existing C code files to create training examples
for file in *.c; do
    python ../tools/compliance_checker.py --code-file "$file" --json > "${file%.c}_analysis.json"
done
```

## Training Data Management

### Creating Training Examples

#### Manual Creation

Create JSON files with the following structure:

```json
{
  "code_sample": "#include <stdint.h>\n\nint main() {\n    return 0;\n}",
  "compliance_score": 100,
  "compliance_level": "fully_compliant",
  "violations": [],
  "annotations": {
    "function_count": 1,
    "line_count": 4,
    "complexity_score": 1,
    "nesting_depth": 1,
    "variable_count": 0,
    "pointer_count": 0,
    "loop_count": 0,
    "conditional_count": 0
  },
  "tags": ["basic", "main_function"],
  "difficulty": "beginner"
}
```

#### Automated Generation

Use the compliance checker to analyze existing code:

```bash
# Analyze existing C files
python tools/compliance_checker.py --code-file existing_code.c --json > training_example.json
```

### Data Augmentation

The training system supports data augmentation:

```json
{
  "augmentation": {
    "enabled": true,
    "techniques": [
      "variable_renaming",
      "comment_variations",
      "whitespace_variations",
      "syntax_variations"
    ],
    "augmentation_factor": 2.0
  }
}
```

## Monitoring and Maintenance

### Training Monitoring

#### Logs and Metrics

Training generates detailed logs:
- Training progress per epoch
- Validation accuracy
- Loss curves
- Feature importance (for traditional ML)

#### TensorBoard Integration

```bash
# Start TensorBoard for training visualization
tensorboard --logdir ./logs

# Access at http://localhost:6006
```

### Model Performance

#### Evaluation Metrics

- **Accuracy**: Overall classification accuracy
- **Precision/Recall**: Per-class performance
- **F1 Score**: Balanced performance measure
- **MAE**: Mean absolute error for regression

#### Performance Tuning

```bash
# Adjust batch size for memory constraints
python train_compliance_model.py --config-file ./high_memory_config.json

# Increase epochs for better accuracy
python train_compliance_model.py --config-file ./high_accuracy_config.json
```

## Production Deployment

### Model Serving

#### REST API

Create a simple Flask API:

```python
from flask import Flask, request, jsonify
from ml_models.evaluate_compliance import ComplianceEvaluator

app = Flask(__name__)
evaluator = ComplianceEvaluator('./trained_models')

@app.route('/evaluate', methods=['POST'])
def evaluate_code():
    code = request.json['code']
    result = evaluator.predict_compliance(code)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### CI/CD Integration

#### GitHub Actions

```yaml
name: NASA Compliance Check
on: [push, pull_request]

jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r ml_models/requirements.txt
      - name: Check compliance
        run: |
          python tools/compliance_checker.py --code-file src/*.c --json > compliance_report.json
```

## Troubleshooting

### Common Issues

#### Training Failures

1. **Out of Memory**: Reduce batch size
2. **Model Loading Errors**: Check model file paths
3. **Data Format Issues**: Validate JSON structure

#### Performance Issues

1. **Slow Training**: Use GPU if available
2. **Poor Accuracy**: Increase training data or epochs
3. **Overfitting**: Add regularization or early stopping

### Debug Mode

Enable detailed logging:

```bash
export PYTHONPATH=.
python -u ml_models/train_compliance_model.py --data-dir ../training_data 2>&1 | tee training.log
```

### Support Resources

- Check the API reference documentation
- Review training data format
- Verify all dependencies are installed
- Check system resource usage

## Security Considerations

### Model Security

- Validate input code to prevent injection attacks
- Sanitize training data
- Use secure model storage

### Access Control

- Implement authentication for API endpoints
- Restrict model access to authorized users
- Log all compliance checks

## Scaling Considerations

### Horizontal Scaling

- Use multiple model instances
- Implement load balancing
- Use distributed training for large datasets

### Performance Optimization

- Model quantization for faster inference
- Batch processing for multiple files
- Caching for repeated code analysis

## Conclusion

The NASA C Code Compliance ML system provides a comprehensive solution for training machine learning models to enforce NASA coding standards. By following this deployment guide, you can successfully set up and operate the system for both development and production use.

For additional support and advanced usage scenarios, refer to the API reference documentation and the project's issue tracker.
