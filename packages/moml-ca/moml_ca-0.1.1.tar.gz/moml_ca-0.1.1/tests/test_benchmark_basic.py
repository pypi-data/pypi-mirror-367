#!/usr/bin/env python3
"""
Basic test for Parameter Comparison Benchmark

This is a minimal test that doesn't rely on heavy dependencies like scipy/sklearn.
It tests the core functionality of the benchmark pipeline.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from huggingface_djmgnn_validation.parameter_comparison import ParameterComparison


def test_parameter_comparison_basic():
    """Test basic ParameterComparison functionality."""
    param = ParameterComparison(
        mol_id="test_mol",
        param_type="charge",
        param_name="C1",
        ref_value=-0.123,
        pred_value=-0.145,
        unit="elementary_charge",
        ff_source="test"
    )
    
    assert param.mol_id == "test_mol"
    assert param.param_type == "charge"
    assert param.ref_value == -0.123
    assert param.pred_value == -0.145


def test_benchmark_config_import():
    """Test that BenchmarkConfig can be imported and instantiated."""
    try:
        from huggingface_djmgnn_validation.parameter_comparison_benchmark import BenchmarkConfig
        
        config = BenchmarkConfig()
        assert config.model_repo_id == "your-username/djmgnn-model"
        assert config.device == "auto"
        assert config.include_pfas is True
        
        print("✓ BenchmarkConfig import and instantiation successful")
        
    except ImportError as e:
        pytest.skip(f"Cannot import BenchmarkConfig due to missing dependencies: {e}")


def test_benchmark_import_with_mocked_dependencies():
    """Test that benchmark can be imported when dependencies are mocked."""
    
    # Mock all the heavy dependencies
    with patch.dict('sys.modules', {
        'torch': Mock(),
        'torch.nn': Mock(),
        'torch.nn.functional': Mock(),
        'torch_geometric': Mock(),
        'torch_geometric.data': Mock(),
        'matplotlib': Mock(),
        'matplotlib.pyplot': Mock(),
        'seaborn': Mock(),
        'scipy': Mock(),
        'scipy.stats': Mock(),
        'sklearn': Mock(),
        'sklearn.metrics': Mock(),
        'huggingface_hub': Mock(),
        'rdkit': Mock(),
        'rdkit.Chem': Mock(),
        'rdkit.Chem.AllChem': Mock(),
    }):
        
        # Mock the global dependency flags
        import huggingface_djmgnn_validation.parameter_comparison_benchmark as benchmark_module
        benchmark_module.HAS_TORCH = True
        benchmark_module.HAS_RDKIT = True
        benchmark_module.HAS_HF_HUB = True
        benchmark_module.HAS_DJMGNN = True
        benchmark_module.HAS_PLOTTING = False  # Disable plotting for test
        benchmark_module.HAS_SCIPY = False
        benchmark_module.HAS_SKLEARN = False
        
        from huggingface_djmgnn_validation.parameter_comparison_benchmark import (
            ParameterComparisonBenchmark, 
            BenchmarkConfig
        )
        
        # Create config
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BenchmarkConfig(
                output_dir=temp_dir,
                generate_plots=False,
                statistical_tests=False
            )
            
            # Mock torch.device and torch.cuda.is_available
            with patch('torch.cuda.is_available', return_value=False), \
                 patch('torch.device') as mock_device:
                mock_device.return_value = Mock()
                
                # This should work without heavy dependencies
                benchmark = ParameterComparisonBenchmark(config)
                
                assert benchmark.config == config
                assert benchmark.output_dir == Path(temp_dir)
                
                print("✓ Benchmark initialization successful with mocked dependencies")


def test_parameter_comparison_methods():
    """Test parameter comparison methods work with basic data."""
    
    # Mock all the heavy dependencies but keep core functionality
    with patch.dict('sys.modules', {
        'torch': Mock(),
        'matplotlib': Mock(),
        'matplotlib.pyplot': Mock(),
        'seaborn': Mock(),
        'scipy': Mock(),
        'sklearn': Mock(),
        'huggingface_hub': Mock(),
        'rdkit': Mock(),
    }):
        
        import huggingface_djmgnn_validation.parameter_comparison_benchmark as benchmark_module
        benchmark_module.HAS_TORCH = True
        benchmark_module.HAS_RDKIT = True  
        benchmark_module.HAS_HF_HUB = True
        benchmark_module.HAS_DJMGNN = True
        benchmark_module.HAS_PLOTTING = False
        benchmark_module.HAS_SCIPY = False
        benchmark_module.HAS_SKLEARN = False
        
        from huggingface_djmgnn_validation.parameter_comparison_benchmark import (
            ParameterComparisonBenchmark,
            BenchmarkConfig
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = BenchmarkConfig(
                output_dir=temp_dir,
                generate_plots=False,
                statistical_tests=False
            )
            
            with patch('torch.cuda.is_available', return_value=False), \
                 patch('torch.device') as mock_device:
                mock_device.return_value = Mock()
                
                benchmark = ParameterComparisonBenchmark(config)
                
                # Test compare_parameters method
                djmgnn_params = [
                    ParameterComparison(
                        mol_id="test_mol",
                        param_type="charge",
                        param_name="C1",
                        ref_value=0.0,
                        pred_value=-0.123,
                        unit="elementary_charge",
                        ff_source="DJMGNN"
                    )
                ]
                
                mmff94_params = [
                    ParameterComparison(
                        mol_id="test_mol",
                        param_type="charge",
                        param_name="C1",
                        ref_value=-0.145,
                        pred_value=0.0,
                        unit="elementary_charge",
                        ff_source="MMFF94"
                    )
                ]
                
                comparison_df = benchmark.compare_parameters(djmgnn_params, mmff94_params)
                
                assert isinstance(comparison_df, pd.DataFrame)
                assert len(comparison_df) > 0
                
                # Test analyze_results method
                analysis_results = benchmark.analyze_results(comparison_df)
                
                assert isinstance(analysis_results, dict)
                assert 'overall_stats' in analysis_results
                
                print("✓ Parameter comparison and analysis methods work correctly")


def test_json_safe_conversion():
    """Test JSON-safe conversion works without benchmark import."""
    # Create a mock benchmark with just the method we need
    class MockBenchmark:
        def _make_json_safe(self, obj):
            """Convert numpy types to JSON-safe types."""
            if isinstance(obj, dict):
                return {k: self._make_json_safe(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [self._make_json_safe(v) for v in obj]
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            elif pd.isna(obj):
                return None
            else:
                return obj
    
    benchmark = MockBenchmark()
    
    test_data = {
        'float64': np.float64(1.5),
        'int32': np.int32(42),
        'array': np.array([1, 2, 3]),
        'nested': {
            'inner_float': np.float32(2.5),
        },
        'nan_value': np.nan
    }
    
    safe_data = benchmark._make_json_safe(test_data)
    
    assert isinstance(safe_data['float64'], float)
    assert isinstance(safe_data['int32'], int)
    assert isinstance(safe_data['array'], list)
    assert isinstance(safe_data['nested']['inner_float'], float)
    assert safe_data['nan_value'] is None
    
    print("✓ JSON-safe conversion works correctly")


if __name__ == "__main__":
    print("Running basic benchmark tests...")
    
    try:
        test_parameter_comparison_basic()
        print("✓ Basic parameter comparison test passed")
    except Exception as e:
        print(f"✗ Basic parameter comparison test failed: {e}")
    
    try:
        test_benchmark_config_import()
        print("✓ Benchmark config import test passed")
    except Exception as e:
        print(f"✗ Benchmark config import test failed: {e}")
    
    try:
        test_benchmark_import_with_mocked_dependencies()
        print("✓ Benchmark import with mocked dependencies test passed")
    except Exception as e:
        print(f"✗ Benchmark import with mocked dependencies test failed: {e}")
    
    try:
        test_parameter_comparison_methods()
        print("✓ Parameter comparison methods test passed")
    except Exception as e:
        print(f"✗ Parameter comparison methods test failed: {e}")
    
    try:
        test_json_safe_conversion()
        print("✓ JSON-safe conversion test passed")
    except Exception as e:
        print(f"✗ JSON-safe conversion test failed: {e}")
    
    print("\nAll basic tests completed!")