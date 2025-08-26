#!/usr/bin/env python3
"""
NASA C Code Compliance ML Training Script

This script trains machine learning models to assess C code compliance
with NASA's safety-critical coding standards.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel
import click

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NASACodeDataset(Dataset):
    """Dataset class for NASA C code compliance training data."""
    
    def __init__(self, data: List[Dict[str, Any]], tokenizer, max_length: int = 512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        code = item['code_sample']
        
        # Tokenize the code
        encoding = self.tokenizer(
            code,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Prepare labels
        compliance_score = torch.tensor(item['compliance_score'] / 100.0, dtype=torch.float32)
        compliance_level = self._encode_compliance_level(item['compliance_level'])
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'compliance_score': compliance_score,
            'compliance_level': compliance_level
        }
    
    def _encode_compliance_level(self, level: str) -> int:
        """Encode compliance level as integer."""
        level_mapping = {
            'fully_compliant': 0,
            'minor_issues': 1,
            'moderate_issues': 2,
            'major_issues': 3,
            'non_compliant': 4
        }
        return level_mapping.get(level, 0)

class ComplianceClassifier(nn.Module):
    """Neural network classifier for NASA C code compliance."""
    
    def __init__(self, model_name: str, num_classes: int = 5):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(self.encoder.config.hidden_size, num_classes)
        self.regressor = nn.Linear(self.encoder.config.hidden_size, 1)
        
    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        pooled_output = self.dropout(pooled_output)
        
        classification_logits = self.classifier(pooled_output)
        regression_score = self.regressor(pooled_output)
        
        return classification_logits, regression_score

class ComplianceTrainer:
    """Main trainer class for NASA C compliance models."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
        self.model = ComplianceClassifier(config['model_name']).to(self.device)
        
        # Training parameters
        self.learning_rate = config.get('learning_rate', 2e-5)
        self.batch_size = config.get('batch_size', 16)
        self.epochs = config.get('epochs', 10)
        
    def load_training_data(self, data_dir: str) -> Tuple[List[Dict], List[Dict]]:
        """Load training data from directory."""
        compliant_data = []
        non_compliant_data = []
        
        # Load compliant examples
        compliant_dir = Path(data_dir) / 'compliant_examples'
        if compliant_dir.exists():
            for file_path in compliant_dir.glob('*.json'):
                with open(file_path, 'r') as f:
                    compliant_data.append(json.load(f))
        
        # Load non-compliant examples
        non_compliant_dir = Path(data_dir) / 'non_compliant_examples'
        if non_compliant_dir.exists():
            for file_path in non_compliant_dir.glob('*.json'):
                with open(file_path, 'r') as f:
                    non_compliant_data.append(json.load(f))
        
        logger.info(f"Loaded {len(compliant_data)} compliant and {len(non_compliant_data)} non-compliant examples")
        return compliant_data, non_compliant_data
    
    def prepare_features(self, data: List[Dict]) -> pd.DataFrame:
        """Extract features from code samples for traditional ML."""
        features = []
        
        for item in data:
            feature_vector = {
                'code_length': len(item['code_sample']),
                'function_count': item['annotations']['function_count'],
                'line_count': item['annotations']['line_count'],
                'complexity_score': item['annotations']['complexity_score'],
                'nesting_depth': item['annotations']['nesting_depth'],
                'variable_count': item['annotations']['variable_count'],
                'pointer_count': item['annotations']['pointer_count'],
                'loop_count': item['annotations']['loop_count'],
                'conditional_count': item['annotations']['conditional_count'],
                'violation_count': len(item['violations']),
                'compliance_score': item['compliance_score']
            }
            features.append(feature_vector)
        
        return pd.DataFrame(features)
    
    def train_traditional_ml(self, X_train: pd.DataFrame, y_train: pd.Series,
                           X_test: pd.DataFrame, y_test: pd.Series) -> RandomForestClassifier:
        """Train traditional ML model (Random Forest)."""
        logger.info("Training Random Forest classifier...")
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Random Forest Accuracy: {accuracy:.4f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature Importance:")
        for _, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        return model
    
    def train_neural_network(self, train_data: List[Dict], val_data: List[Dict]):
        """Train neural network model."""
        logger.info("Training neural network classifier...")
        
        # Prepare datasets
        train_dataset = NASACodeDataset(train_data, self.tokenizer)
        val_dataset = NASACodeDataset(val_data, self.tokenizer)
        
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size)
        
        # Loss functions and optimizer
        classification_criterion = nn.CrossEntropyLoss()
        regression_criterion = nn.MSELoss()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.learning_rate)
        
        # Training loop
        for epoch in range(self.epochs):
            self.model.train()
            total_loss = 0
            
            for batch in train_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                compliance_level = batch['compliance_level'].to(self.device)
                compliance_score = batch['compliance_score'].to(self.device)
                
                optimizer.zero_grad()
                
                classification_logits, regression_score = self.model(input_ids, attention_mask)
                
                # Calculate losses
                cls_loss = classification_criterion(classification_logits, compliance_level)
                reg_loss = regression_criterion(regression_score.squeeze(), compliance_score)
                total_loss = cls_loss + reg_loss
                
                total_loss.backward()
                optimizer.step()
            
            # Validation
            self.model.eval()
            val_accuracy = 0
            val_samples = 0
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch['input_ids'].to(self.device)
                    attention_mask = batch['attention_mask'].to(self.device)
                    compliance_level = batch['compliance_level'].to(self.device)
                    
                    classification_logits, _ = self.model(input_ids, attention_mask)
                    predictions = torch.argmax(classification_logits, dim=1)
                    
                    val_accuracy += (predictions == compliance_level).sum().item()
                    val_samples += compliance_level.size(0)
            
            val_accuracy /= val_samples
            logger.info(f"Epoch {epoch+1}/{self.epochs} - Loss: {total_loss:.4f}, Val Accuracy: {val_accuracy:.4f}")
    
    def save_model(self, model, output_dir: str, model_type: str):
        """Save trained model."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if model_type == 'random_forest':
            import joblib
            model_path = output_path / 'random_forest_model.joblib'
            joblib.dump(model, model_path)
            logger.info(f"Random Forest model saved to {model_path}")
        
        elif model_type == 'neural_network':
            model_path = output_path / 'neural_network_model.pt'
            torch.save(self.model.state_dict(), model_path)
            logger.info(f"Neural network model saved to {model_path}")

@click.command()
@click.option('--data-dir', default='../training_data', help='Directory containing training data')
@click.option('--output-dir', default='./trained_models', help='Directory to save trained models')
@click.option('--model-type', type=click.Choice(['both', 'traditional', 'neural']), 
              default='both', help='Type of model to train')
@click.option('--config-file', default='./training_config.json', help='Training configuration file')
def main(data_dir: str, output_dir: str, model_type: str, config_file: str):
    """Main training function."""
    
    # Load configuration
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {
            'model_name': 'microsoft/codebert-base',
            'learning_rate': 2e-5,
            'batch_size': 16,
            'epochs': 10
        }
    
    # Initialize trainer
    trainer = ComplianceTrainer(config)
    
    # Load data
    compliant_data, non_compliant_data = trainer.load_training_data(data_dir)
    
    if not compliant_data and not non_compliant_data:
        logger.error("No training data found!")
        sys.exit(1)
    
    # Combine data
    all_data = compliant_data + non_compliant_data
    
    if model_type in ['traditional', 'both']:
        # Prepare features for traditional ML
        features_df = trainer.prepare_features(all_data)
        
        # Split data
        X = features_df.drop('compliance_score', axis=1)
        y = pd.cut(features_df['compliance_score'], 
                   bins=[0, 60, 70, 80, 90, 100], 
                   labels=[0, 1, 2, 3, 4])
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train traditional ML model
        rf_model = trainer.train_traditional_ml(X_train, y_train, X_test, y_test)
        trainer.save_model(rf_model, output_dir, 'random_forest')
    
    if model_type in ['neural', 'both']:
        # Split data for neural network
        train_data, val_data = train_test_split(all_data, test_size=0.2, random_state=42)
        
        # Train neural network
        trainer.train_neural_network(train_data, val_data)
        trainer.save_model(None, output_dir, 'neural_network')
    
    logger.info("Training completed successfully!")

if __name__ == '__main__':
    main()
