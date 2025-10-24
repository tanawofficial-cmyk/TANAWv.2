# data_transformer.py
"""
Data Transformation Engine with Feature-engine + Scikit-learn
Implements scaling, normalization, encoding, and feature engineering.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
import warnings
warnings.filterwarnings('ignore')

# Feature-engine for advanced transformations
try:
    from feature_engine.encoding import (
        OneHotEncoder as FEOneHotEncoder,
        CountFrequencyEncoder,
        MeanEncoder,
        WoEEncoder
    )
    from feature_engine.transformation import (
        LogTransformer,
        ReciprocalTransformer,
        PowerTransformer,
        BoxCoxTransformer,
        YeoJohnsonTransformer
    )
    from feature_engine.outliers import Winsorizer
    from feature_engine.imputation import (
        MeanMedianImputer,
        ArbitraryNumberImputer,
        CategoricalImputer
    )
    FEATURE_ENGINE_AVAILABLE = True
except ImportError:
    FEATURE_ENGINE_AVAILABLE = False
    print("⚠️ Feature-engine not available. Install with: pip install feature-engine")


class DataTransformer:
    """
    Comprehensive data transformation with:
    - Feature-engine for advanced transformations
    - Scikit-learn for standard scaling and encoding
    - Automatic transformation selection based on data characteristics
    """
    
    def __init__(self):
        self.feature_engine_available = FEATURE_ENGINE_AVAILABLE
        self.transformers = {}
        self.transformation_history = []
        self.fitted = False
        
        print(f"🔧 Data Transformer initialized")
        print(f"   Feature-engine: {'✅' if self.feature_engine_available else '❌'}")
    
    def transform_dataset(self, df: pd.DataFrame, 
                         column_mapping: Dict[str, Any] = None,
                         transform_config: Dict[str, Any] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Comprehensive data transformation pipeline.
        
        Args:
            df: DataFrame to transform
            column_mapping: Column mapping information
            transform_config: Configuration for transformations
            
        Returns:
            Tuple of (transformed_dataframe, transformation_report)
        """
        if transform_config is None:
            transform_config = {
                'scaling_method': 'standard',  # standard, minmax, robust
                'encoding_method': 'onehot',    # onehot, label, mean, woe
                'handle_skewness': True,
                'dimensionality_reduction': False,
                'feature_selection': False
            }
        
        transformation_report = {
            'transformations_applied': [],
            'numeric_transformations': [],
            'categorical_transformations': [],
            'feature_engineering': [],
            'dimensionality_reduction': {},
            'warnings': []
        }
        
        original_df = df.copy()
        
        try:
            print("🔄 Starting data transformation pipeline...")
            
            # Step 1: Identify column types
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            print(f"   Numeric columns: {len(numeric_cols)}")
            print(f"   Categorical columns: {len(categorical_cols)}")
            
            # Step 2: Handle skewed numeric features
            if transform_config.get('handle_skewness', True) and numeric_cols:
                df, skewness_report = self._handle_skewness(df, numeric_cols)
                transformation_report['numeric_transformations'].extend(skewness_report)
            
            # Step 3: Scale numeric features
            if numeric_cols:
                df, scaling_report = self._scale_numeric_features(
                    df, numeric_cols, transform_config.get('scaling_method', 'standard')
                )
                transformation_report['numeric_transformations'].extend(scaling_report)
            
            # Step 4: Encode categorical features
            if categorical_cols:
                df, encoding_report = self._encode_categorical_features(
                    df, categorical_cols, transform_config.get('encoding_method', 'onehot')
                )
                transformation_report['categorical_transformations'].extend(encoding_report)
            
            # Step 5: Feature engineering (create computed features)
            df, feature_engineering_report = self._engineer_features(df, column_mapping)
            transformation_report['feature_engineering'] = feature_engineering_report
            
            # Step 6: Dimensionality reduction (optional)
            if transform_config.get('dimensionality_reduction', False) and len(df.columns) > 10:
                df, dim_reduction_report = self._reduce_dimensions(df)
                transformation_report['dimensionality_reduction'] = dim_reduction_report
            
            # Step 7: Feature selection (optional)
            if transform_config.get('feature_selection', False):
                df, selection_report = self._select_features(df, original_df)
                transformation_report['feature_selection'] = selection_report
            
            transformation_report['original_shape'] = original_df.shape
            transformation_report['final_shape'] = df.shape
            transformation_report['transformation_success'] = True
            
            print(f"✅ Transformation completed: {original_df.shape} → {df.shape}")
            
        except Exception as e:
            transformation_report['error'] = str(e)
            transformation_report['transformation_success'] = False
            print(f"❌ Transformation error: {e}")
        
        return df, transformation_report
    
    def _handle_skewness(self, df: pd.DataFrame, numeric_cols: List[str]) -> Tuple[pd.DataFrame, List[Dict]]:
        """Handle skewed distributions in numeric features."""
        skewness_report = []
        
        for col in numeric_cols:
            try:
                # Calculate skewness
                skewness = df[col].skew()
                
                if abs(skewness) > 1.0:  # Highly skewed
                    transformation_applied = None
                    
                    # Choose transformation based on data characteristics
                    if self.feature_engine_available:
                        # Use Feature-engine transformers
                        if skewness > 1.0:  # Right-skewed
                            if (df[col] > 0).all():  # All positive values
                                transformer = LogTransformer(variables=[col])
                                df = transformer.fit_transform(df)
                                transformation_applied = 'log'
                                self.transformers[f'{col}_skew'] = transformer
                            else:
                                transformer = YeoJohnsonTransformer(variables=[col])
                                df = transformer.fit_transform(df)
                                transformation_applied = 'yeo_johnson'
                                self.transformers[f'{col}_skew'] = transformer
                        else:  # Left-skewed
                            transformer = PowerTransformer(variables=[col])
                            df = transformer.fit_transform(df)
                            transformation_applied = 'power'
                            self.transformers[f'{col}_skew'] = transformer
                    else:
                        # Fallback to numpy transformations
                        if (df[col] > 0).all():
                            df[col] = np.log1p(df[col])
                            transformation_applied = 'log1p'
                        else:
                            # Square root for positive skewness, square for negative
                            if skewness > 0:
                                df[col] = np.sqrt(df[col] - df[col].min() + 1)
                                transformation_applied = 'sqrt'
                    
                    if transformation_applied:
                        new_skewness = df[col].skew()
                        skewness_report.append({
                            'column': col,
                            'transformation': 'skewness_correction',
                            'method': transformation_applied,
                            'original_skewness': round(skewness, 2),
                            'new_skewness': round(new_skewness, 2),
                            'improvement': round(abs(skewness) - abs(new_skewness), 2)
                        })
                        print(f"   ✓ {col}: {transformation_applied} (skew: {skewness:.2f} → {new_skewness:.2f})")
                
            except Exception as e:
                print(f"   ⚠️ Skewness handling failed for {col}: {e}")
        
        return df, skewness_report
    
    def _scale_numeric_features(self, df: pd.DataFrame, numeric_cols: List[str], 
                               method: str = 'standard') -> Tuple[pd.DataFrame, List[Dict]]:
        """Scale numeric features."""
        scaling_report = []
        
        try:
            # Choose scaler
            if method == 'standard':
                scaler = StandardScaler()
                scaler_name = 'StandardScaler'
            elif method == 'minmax':
                scaler = MinMaxScaler()
                scaler_name = 'MinMaxScaler'
            elif method == 'robust':
                scaler = RobustScaler()
                scaler_name = 'RobustScaler'
            else:
                scaler = StandardScaler()
                scaler_name = 'StandardScaler'
            
            # Fit and transform
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            self.transformers['scaler'] = scaler
            
            scaling_report.append({
                'transformation': 'scaling',
                'method': scaler_name,
                'columns': numeric_cols,
                'num_columns': len(numeric_cols)
            })
            
            print(f"   ✓ Scaled {len(numeric_cols)} numeric columns using {scaler_name}")
            
        except Exception as e:
            print(f"   ⚠️ Scaling failed: {e}")
        
        return df, scaling_report
    
    def _encode_categorical_features(self, df: pd.DataFrame, categorical_cols: List[str], 
                                    method: str = 'onehot') -> Tuple[pd.DataFrame, List[Dict]]:
        """Encode categorical features."""
        encoding_report = []
        
        for col in categorical_cols:
            try:
                n_categories = df[col].nunique()
                
                # Skip if too many categories
                if n_categories > 50:
                    print(f"   ⚠️ Skipping {col}: too many categories ({n_categories})")
                    continue
                
                transformation_applied = None
                
                if method == 'onehot' or n_categories <= 10:
                    # One-hot encoding for low cardinality
                    if self.feature_engine_available:
                        encoder = FEOneHotEncoder(variables=[col], drop_last=True)
                        df = encoder.fit_transform(df)
                        self.transformers[f'{col}_encoder'] = encoder
                        transformation_applied = 'onehot_fe'
                    else:
                        # Fallback to pandas
                        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
                        df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
                        transformation_applied = 'onehot_pandas'
                    
                elif method == 'label':
                    # Label encoding
                    encoder = LabelEncoder()
                    df[col] = encoder.fit_transform(df[col].astype(str))
                    self.transformers[f'{col}_encoder'] = encoder
                    transformation_applied = 'label'
                
                elif method == 'frequency' and self.feature_engine_available:
                    # Frequency encoding
                    encoder = CountFrequencyEncoder(variables=[col])
                    df = encoder.fit_transform(df)
                    self.transformers[f'{col}_encoder'] = encoder
                    transformation_applied = 'frequency'
                
                elif method == 'mean' and self.feature_engine_available:
                    # Mean target encoding (requires target variable)
                    # Skip for now as we don't have target
                    transformation_applied = 'mean_skipped'
                
                if transformation_applied and transformation_applied != 'mean_skipped':
                    encoding_report.append({
                        'column': col,
                        'transformation': 'encoding',
                        'method': transformation_applied,
                        'original_categories': n_categories
                    })
                    print(f"   ✓ {col}: {transformation_applied} ({n_categories} categories)")
                
            except Exception as e:
                print(f"   ⚠️ Encoding failed for {col}: {e}")
        
        return df, encoding_report
    
    def _engineer_features(self, df: pd.DataFrame, column_mapping: Dict[str, Any] = None) -> Tuple[pd.DataFrame, List[Dict]]:
        """Engineer new features based on domain knowledge."""
        feature_engineering_report = []
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            # Create interaction features for numeric columns
            if len(numeric_cols) >= 2:
                # Create ratio features (for business metrics)
                if column_mapping:
                    mapped_cols = column_mapping.get('mapped_columns', [])
                    
                    # Find revenue/sales and quantity columns
                    revenue_cols = [m['original_column'] for m in mapped_cols 
                                  if m.get('mapped_column') in ['sales', 'revenue', 'amount'] 
                                  and m['original_column'] in df.columns]
                    quantity_cols = [m['original_column'] for m in mapped_cols 
                                   if m.get('mapped_column') in ['quantity', 'qty'] 
                                   and m['original_column'] in df.columns]
                    
                    # Create unit price features (revenue / quantity)
                    for rev_col in revenue_cols:
                        for qty_col in quantity_cols:
                            if rev_col in df.columns and qty_col in df.columns:
                                feature_name = f'{rev_col}_per_{qty_col}'
                                df[feature_name] = df[rev_col] / (df[qty_col] + 1e-10)  # Avoid division by zero
                                feature_engineering_report.append({
                                    'feature': feature_name,
                                    'type': 'ratio',
                                    'formula': f'{rev_col} / {qty_col}'
                                })
                                print(f"   ✓ Created feature: {feature_name}")
            
            # Create polynomial features (squares, cubes) for key metrics
            # (Only for a few selected columns to avoid explosion)
            if len(numeric_cols) > 0 and len(numeric_cols) <= 5:
                for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                    # Square
                    df[f'{col}_squared'] = df[col] ** 2
                    feature_engineering_report.append({
                        'feature': f'{col}_squared',
                        'type': 'polynomial',
                        'formula': f'{col}^2'
                    })
                    print(f"   ✓ Created feature: {col}_squared")
            
            # Create time-based features if date columns exist
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            for col in date_cols:
                # Extract date components
                df[f'{col}_year'] = df[col].dt.year
                df[f'{col}_month'] = df[col].dt.month
                df[f'{col}_day'] = df[col].dt.day
                df[f'{col}_dayofweek'] = df[col].dt.dayofweek
                df[f'{col}_quarter'] = df[col].dt.quarter
                
                feature_engineering_report.append({
                    'feature': f'{col}_datetime_components',
                    'type': 'temporal',
                    'components': ['year', 'month', 'day', 'dayofweek', 'quarter']
                })
                print(f"   ✓ Extracted date components from {col}")
            
        except Exception as e:
            print(f"   ⚠️ Feature engineering error: {e}")
        
        return df, feature_engineering_report
    
    def _reduce_dimensions(self, df: pd.DataFrame, n_components: int = 10) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Reduce dimensions using PCA."""
        reduction_report = {}
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) > n_components:
                # Apply PCA
                pca = PCA(n_components=min(n_components, len(numeric_cols)))
                pca_features = pca.fit_transform(df[numeric_cols])
                
                # Create PCA feature columns
                pca_df = pd.DataFrame(
                    pca_features,
                    columns=[f'PC{i+1}' for i in range(pca_features.shape[1])],
                    index=df.index
                )
                
                # Replace numeric columns with PCA components
                df = df.drop(columns=numeric_cols)
                df = pd.concat([df, pca_df], axis=1)
                
                self.transformers['pca'] = pca
                
                reduction_report = {
                    'method': 'PCA',
                    'original_features': len(numeric_cols),
                    'reduced_features': pca_features.shape[1],
                    'explained_variance': pca.explained_variance_ratio_.tolist(),
                    'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist()
                }
                
                print(f"   ✓ PCA: {len(numeric_cols)} → {pca_features.shape[1]} features")
                print(f"   ✓ Explained variance: {pca.explained_variance_ratio_.sum():.2%}")
        
        except Exception as e:
            reduction_report['error'] = str(e)
            print(f"   ⚠️ Dimensionality reduction failed: {e}")
        
        return df, reduction_report
    
    def _select_features(self, df: pd.DataFrame, original_df: pd.DataFrame, 
                        k: int = 10) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Select top k features using statistical tests."""
        selection_report = {}
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) > k:
                # For now, select features based on variance
                # (In supervised learning, we'd use target-based selection)
                variances = df[numeric_cols].var()
                top_k_features = variances.nlargest(k).index.tolist()
                
                df = df[top_k_features]
                
                selection_report = {
                    'method': 'variance_threshold',
                    'original_features': len(numeric_cols),
                    'selected_features': len(top_k_features),
                    'features': top_k_features
                }
                
                print(f"   ✓ Feature selection: {len(numeric_cols)} → {len(top_k_features)} features")
        
        except Exception as e:
            selection_report['error'] = str(e)
            print(f"   ⚠️ Feature selection failed: {e}")
        
        return df, selection_report
    
    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Inverse transform the data (if possible)."""
        try:
            if 'scaler' in self.transformers:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                df[numeric_cols] = self.transformers['scaler'].inverse_transform(df[numeric_cols])
            
            if 'pca' in self.transformers:
                pca_cols = [col for col in df.columns if col.startswith('PC')]
                original_data = self.transformers['pca'].inverse_transform(df[pca_cols])
                # Note: We'd need to track original column names for full reconstruction
            
            return df
            
        except Exception as e:
            print(f"⚠️ Inverse transform failed: {e}")
            return df
    
    def get_transformation_summary(self) -> Dict[str, Any]:
        """Get summary of all applied transformations."""
        return {
            'transformers_fitted': list(self.transformers.keys()),
            'total_transformations': len(self.transformation_history),
            'feature_engine_used': self.feature_engine_available,
            'is_fitted': self.fitted
        }

