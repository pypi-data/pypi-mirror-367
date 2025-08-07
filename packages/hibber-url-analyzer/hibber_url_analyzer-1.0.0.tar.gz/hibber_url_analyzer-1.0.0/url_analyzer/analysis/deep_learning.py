"""
Deep Learning Module for URL Analysis

This module provides deep learning capabilities for URL analysis,
including neural network models for classification, anomaly detection,
and predictive analytics.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set
import logging
import os
import json

logger = logging.getLogger(__name__)

# Optional imports with fallbacks
try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, optimizers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class DeepLearningClassifier:
    """
    Deep Learning Classifier for URL data.
    
    This class provides deep learning-based classification capabilities
    for URL data using neural networks.
    """
    
    def __init__(self, framework: str = "auto"):
        """
        Initialize the deep learning classifier.
        
        Args:
            framework: Deep learning framework to use ("tensorflow", "pytorch", or "auto")
        """
        self.framework = framework
        
        if framework == "auto":
            if TENSORFLOW_AVAILABLE:
                self.framework = "tensorflow"
            elif PYTORCH_AVAILABLE:
                self.framework = "pytorch"
            else:
                self.framework = "none"
                logger.warning("No deep learning framework available. Classification will not work.")
        
        self.model = None
        self.scaler = None
        self.classes = None
    
    def build_model(self, input_dim: int, num_classes: int) -> None:
        """
        Build a neural network model.
        
        Args:
            input_dim: Dimension of input features
            num_classes: Number of output classes
        """
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Build TensorFlow model
            model = models.Sequential([
                layers.Dense(128, activation='relu', input_shape=(input_dim,)),
                layers.Dropout(0.3),
                layers.Dense(64, activation='relu'),
                layers.Dropout(0.2),
                layers.Dense(num_classes, activation='softmax')
            ])
            
            model.compile(
                optimizer=optimizers.Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            self.model = model
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Build PyTorch model
            class URLClassifier(nn.Module):
                def __init__(self, input_dim, num_classes):
                    super(URLClassifier, self).__init__()
                    self.fc1 = nn.Linear(input_dim, 128)
                    self.dropout1 = nn.Dropout(0.3)
                    self.fc2 = nn.Linear(128, 64)
                    self.dropout2 = nn.Dropout(0.2)
                    self.fc3 = nn.Linear(64, num_classes)
                
                def forward(self, x):
                    x = torch.relu(self.fc1(x))
                    x = self.dropout1(x)
                    x = torch.relu(self.fc2(x))
                    x = self.dropout2(x)
                    x = self.fc3(x)
                    return x
            
            self.model = URLClassifier(input_dim, num_classes)
        
        else:
            logger.error(f"Cannot build model: framework {self.framework} not available")
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 20,
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train the neural network model.
        
        Args:
            X: Input features
            y: Target labels
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data to use for validation
            
        Returns:
            Dictionary containing training history
        """
        if self.model is None:
            num_classes = len(np.unique(y))
            self.build_model(X.shape[1], num_classes)
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Store classes
        self.classes = np.unique(y)
        
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Train TensorFlow model
            history = self.model.fit(
                X_scaled, y,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=0
            )
            
            return {
                "accuracy": history.history['accuracy'][-1],
                "val_accuracy": history.history['val_accuracy'][-1],
                "loss": history.history['loss'][-1],
                "val_loss": history.history['val_loss'][-1]
            }
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Train PyTorch model
            X_train, X_val, y_train, y_val = train_test_split(
                X_scaled, y, test_size=validation_split, random_state=42
            )
            
            # Convert to PyTorch tensors
            X_train_tensor = torch.FloatTensor(X_train)
            y_train_tensor = torch.LongTensor(y_train)
            X_val_tensor = torch.FloatTensor(X_val)
            y_val_tensor = torch.LongTensor(y_val)
            
            # Define loss function and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            
            # Training loop
            self.model.train()
            train_losses = []
            val_losses = []
            train_accs = []
            val_accs = []
            
            for epoch in range(epochs):
                # Training
                optimizer.zero_grad()
                outputs = self.model(X_train_tensor)
                loss = criterion(outputs, y_train_tensor)
                loss.backward()
                optimizer.step()
                
                # Calculate training accuracy
                _, predicted = torch.max(outputs.data, 1)
                train_acc = (predicted == y_train_tensor).sum().item() / y_train_tensor.size(0)
                
                # Validation
                self.model.eval()
                with torch.no_grad():
                    val_outputs = self.model(X_val_tensor)
                    val_loss = criterion(val_outputs, y_val_tensor)
                    _, val_predicted = torch.max(val_outputs.data, 1)
                    val_acc = (val_predicted == y_val_tensor).sum().item() / y_val_tensor.size(0)
                
                self.model.train()
                
                # Store metrics
                train_losses.append(loss.item())
                val_losses.append(val_loss.item())
                train_accs.append(train_acc)
                val_accs.append(val_acc)
            
            return {
                "accuracy": train_accs[-1],
                "val_accuracy": val_accs[-1],
                "loss": train_losses[-1],
                "val_loss": val_losses[-1]
            }
        
        else:
            logger.error(f"Cannot train model: framework {self.framework} not available")
            return {
                "error": f"Framework {self.framework} not available"
            }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions with the trained model.
        
        Args:
            X: Input features
            
        Returns:
            Predicted class labels
        """
        if self.model is None:
            logger.error("Model not trained yet")
            return np.array([])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Predict with TensorFlow model
            probas = self.model.predict(X_scaled)
            return np.argmax(probas, axis=1)
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Predict with PyTorch model
            X_tensor = torch.FloatTensor(X_scaled)
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(X_tensor)
                _, predicted = torch.max(outputs.data, 1)
            return predicted.numpy()
        
        else:
            logger.error(f"Cannot predict: framework {self.framework} not available")
            return np.array([])
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.
        
        Args:
            X: Input features
            
        Returns:
            Class probabilities
        """
        if self.model is None:
            logger.error("Model not trained yet")
            return np.array([])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Predict with TensorFlow model
            return self.model.predict(X_scaled)
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Predict with PyTorch model
            X_tensor = torch.FloatTensor(X_scaled)
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(X_tensor)
                probas = torch.softmax(outputs, dim=1)
            return probas.numpy()
        
        else:
            logger.error(f"Cannot predict: framework {self.framework} not available")
            return np.array([])
    
    def save(self, path: str) -> bool:
        """
        Save the model to disk.
        
        Args:
            path: Path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        if self.model is None:
            logger.error("No model to save")
            return False
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
                # Save TensorFlow model
                self.model.save(path)
                
                # Save scaler and classes
                metadata = {
                    "framework": self.framework,
                    "scaler": {
                        "mean": self.scaler.mean_.tolist(),
                        "scale": self.scaler.scale_.tolist()
                    },
                    "classes": self.classes.tolist()
                }
                
                with open(f"{path}_metadata.json", "w") as f:
                    json.dump(metadata, f)
                
                return True
                
            elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
                # Save PyTorch model
                torch.save(self.model.state_dict(), path)
                
                # Save scaler and classes
                metadata = {
                    "framework": self.framework,
                    "scaler": {
                        "mean": self.scaler.mean_.tolist(),
                        "scale": self.scaler.scale_.tolist()
                    },
                    "classes": self.classes.tolist(),
                    "input_dim": self.model.fc1.in_features,
                    "num_classes": self.model.fc3.out_features
                }
                
                with open(f"{path}_metadata.json", "w") as f:
                    json.dump(metadata, f)
                
                return True
            
            else:
                logger.error(f"Cannot save model: framework {self.framework} not available")
                return False
                
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load(self, path: str) -> bool:
        """
        Load the model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load metadata
            with open(f"{path}_metadata.json", "r") as f:
                metadata = json.load(f)
            
            self.framework = metadata["framework"]
            
            # Create scaler
            self.scaler = StandardScaler()
            self.scaler.mean_ = np.array(metadata["scaler"]["mean"])
            self.scaler.scale_ = np.array(metadata["scaler"]["scale"])
            
            # Load classes
            self.classes = np.array(metadata["classes"])
            
            if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
                # Load TensorFlow model
                self.model = models.load_model(path)
                return True
                
            elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
                # Get model dimensions
                input_dim = metadata["input_dim"]
                num_classes = metadata["num_classes"]
                
                # Create model
                self.build_model(input_dim, num_classes)
                
                # Load weights
                self.model.load_state_dict(torch.load(path))
                self.model.eval()
                
                return True
            
            else:
                logger.error(f"Cannot load model: framework {self.framework} not available")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False


class DeepAnomalyDetector:
    """
    Deep Learning-based Anomaly Detector.
    
    This class provides deep learning-based anomaly detection capabilities
    using autoencoders.
    """
    
    def __init__(self, framework: str = "auto"):
        """
        Initialize the deep anomaly detector.
        
        Args:
            framework: Deep learning framework to use ("tensorflow", "pytorch", or "auto")
        """
        self.framework = framework
        
        if framework == "auto":
            if TENSORFLOW_AVAILABLE:
                self.framework = "tensorflow"
            elif PYTORCH_AVAILABLE:
                self.framework = "pytorch"
            else:
                self.framework = "none"
                logger.warning("No deep learning framework available. Anomaly detection will not work.")
        
        self.model = None
        self.scaler = None
        self.threshold = None
    
    def build_model(self, input_dim: int) -> None:
        """
        Build an autoencoder model for anomaly detection.
        
        Args:
            input_dim: Dimension of input features
        """
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Build TensorFlow autoencoder
            # Encoder
            encoder_inputs = tf.keras.Input(shape=(input_dim,))
            encoder = layers.Dense(128, activation='relu')(encoder_inputs)
            encoder = layers.Dense(64, activation='relu')(encoder)
            encoder = layers.Dense(32, activation='relu')(encoder)
            
            # Decoder
            decoder = layers.Dense(64, activation='relu')(encoder)
            decoder = layers.Dense(128, activation='relu')(decoder)
            decoder_outputs = layers.Dense(input_dim, activation='linear')(decoder)
            
            # Autoencoder
            autoencoder = models.Model(encoder_inputs, decoder_outputs)
            autoencoder.compile(optimizer='adam', loss='mse')
            
            self.model = autoencoder
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Build PyTorch autoencoder
            class Autoencoder(nn.Module):
                def __init__(self, input_dim):
                    super(Autoencoder, self).__init__()
                    # Encoder
                    self.encoder = nn.Sequential(
                        nn.Linear(input_dim, 128),
                        nn.ReLU(),
                        nn.Linear(128, 64),
                        nn.ReLU(),
                        nn.Linear(64, 32),
                        nn.ReLU()
                    )
                    # Decoder
                    self.decoder = nn.Sequential(
                        nn.Linear(32, 64),
                        nn.ReLU(),
                        nn.Linear(64, 128),
                        nn.ReLU(),
                        nn.Linear(128, input_dim)
                    )
                
                def forward(self, x):
                    encoded = self.encoder(x)
                    decoded = self.decoder(encoded)
                    return decoded
            
            self.model = Autoencoder(input_dim)
        
        else:
            logger.error(f"Cannot build model: framework {self.framework} not available")
    
    def train(
        self,
        X: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
        validation_split: float = 0.1,
        contamination: float = 0.05
    ) -> Dict[str, Any]:
        """
        Train the autoencoder model.
        
        Args:
            X: Input features (normal data)
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of data to use for validation
            contamination: Expected proportion of anomalies
            
        Returns:
            Dictionary containing training history
        """
        if self.model is None:
            self.build_model(X.shape[1])
        
        # Scale features
        self.scaler = MinMaxScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Train TensorFlow model
            history = self.model.fit(
                X_scaled, X_scaled,
                epochs=epochs,
                batch_size=batch_size,
                validation_split=validation_split,
                verbose=0
            )
            
            # Compute reconstruction errors
            reconstructions = self.model.predict(X_scaled)
            mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            
            # Set threshold based on contamination
            self.threshold = np.percentile(mse, 100 * (1 - contamination))
            
            return {
                "loss": history.history['loss'][-1],
                "val_loss": history.history['val_loss'][-1],
                "threshold": self.threshold
            }
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Train PyTorch model
            X_train, X_val = train_test_split(
                X_scaled, test_size=validation_split, random_state=42
            )
            
            # Convert to PyTorch tensors
            X_train_tensor = torch.FloatTensor(X_train)
            X_val_tensor = torch.FloatTensor(X_val)
            
            # Define loss function and optimizer
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.model.parameters(), lr=0.001)
            
            # Training loop
            self.model.train()
            train_losses = []
            val_losses = []
            
            for epoch in range(epochs):
                # Training
                optimizer.zero_grad()
                outputs = self.model(X_train_tensor)
                loss = criterion(outputs, X_train_tensor)
                loss.backward()
                optimizer.step()
                
                # Validation
                self.model.eval()
                with torch.no_grad():
                    val_outputs = self.model(X_val_tensor)
                    val_loss = criterion(val_outputs, X_val_tensor)
                
                self.model.train()
                
                # Store metrics
                train_losses.append(loss.item())
                val_losses.append(val_loss.item())
            
            # Compute reconstruction errors
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X_scaled)
                reconstructions = self.model(X_tensor).numpy()
            
            mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            
            # Set threshold based on contamination
            self.threshold = np.percentile(mse, 100 * (1 - contamination))
            
            return {
                "loss": train_losses[-1],
                "val_loss": val_losses[-1],
                "threshold": self.threshold
            }
        
        else:
            logger.error(f"Cannot train model: framework {self.framework} not available")
            return {
                "error": f"Framework {self.framework} not available"
            }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Detect anomalies in the data.
        
        Args:
            X: Input features
            
        Returns:
            Binary array (1 for anomalies, 0 for normal)
        """
        if self.model is None or self.threshold is None:
            logger.error("Model not trained yet")
            return np.array([])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Predict with TensorFlow model
            reconstructions = self.model.predict(X_scaled)
            mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            return (mse > self.threshold).astype(int)
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Predict with PyTorch model
            X_tensor = torch.FloatTensor(X_scaled)
            self.model.eval()
            with torch.no_grad():
                reconstructions = self.model(X_tensor).numpy()
            
            mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            return (mse > self.threshold).astype(int)
        
        else:
            logger.error(f"Cannot predict: framework {self.framework} not available")
            return np.array([])
    
    def anomaly_scores(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly scores for the data.
        
        Args:
            X: Input features
            
        Returns:
            Array of anomaly scores
        """
        if self.model is None:
            logger.error("Model not trained yet")
            return np.array([])
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
            # Predict with TensorFlow model
            reconstructions = self.model.predict(X_scaled)
            return np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            
        elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
            # Predict with PyTorch model
            X_tensor = torch.FloatTensor(X_scaled)
            self.model.eval()
            with torch.no_grad():
                reconstructions = self.model(X_tensor).numpy()
            
            return np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
        
        else:
            logger.error(f"Cannot predict: framework {self.framework} not available")
            return np.array([])
    
    def save(self, path: str) -> bool:
        """
        Save the model to disk.
        
        Args:
            path: Path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        if self.model is None:
            logger.error("No model to save")
            return False
        
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
                # Save TensorFlow model
                self.model.save(path)
                
                # Save scaler and threshold
                metadata = {
                    "framework": self.framework,
                    "scaler": {
                        "min": self.scaler.min_.tolist(),
                        "scale": self.scaler.scale_.tolist()
                    },
                    "threshold": float(self.threshold)
                }
                
                with open(f"{path}_metadata.json", "w") as f:
                    json.dump(metadata, f)
                
                return True
                
            elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
                # Save PyTorch model
                torch.save(self.model.state_dict(), path)
                
                # Save scaler and threshold
                metadata = {
                    "framework": self.framework,
                    "scaler": {
                        "min": self.scaler.min_.tolist(),
                        "scale": self.scaler.scale_.tolist()
                    },
                    "threshold": float(self.threshold),
                    "input_dim": self.model.encoder[0].in_features
                }
                
                with open(f"{path}_metadata.json", "w") as f:
                    json.dump(metadata, f)
                
                return True
            
            else:
                logger.error(f"Cannot save model: framework {self.framework} not available")
                return False
                
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def load(self, path: str) -> bool:
        """
        Load the model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Load metadata
            with open(f"{path}_metadata.json", "r") as f:
                metadata = json.load(f)
            
            self.framework = metadata["framework"]
            
            # Create scaler
            self.scaler = MinMaxScaler()
            self.scaler.min_ = np.array(metadata["scaler"]["min"])
            self.scaler.scale_ = np.array(metadata["scaler"]["scale"])
            
            # Load threshold
            self.threshold = metadata["threshold"]
            
            if self.framework == "tensorflow" and TENSORFLOW_AVAILABLE:
                # Load TensorFlow model
                self.model = models.load_model(path)
                return True
                
            elif self.framework == "pytorch" and PYTORCH_AVAILABLE:
                # Get model dimensions
                input_dim = metadata["input_dim"]
                
                # Create model
                self.build_model(input_dim)
                
                # Load weights
                self.model.load_state_dict(torch.load(path))
                self.model.eval()
                
                return True
            
            else:
                logger.error(f"Cannot load model: framework {self.framework} not available")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False