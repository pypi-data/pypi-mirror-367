#!/usr/bin/env python3
"""
Tests for Parameter Comparison Benchmark

This module tests the ParameterComparisonBenchmark class functionality
including molecule preparation, parameter extraction, and analysis methods.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False

from huggingface_djmgnn_validation.parameter_comparison_benchmark import (
    ParameterComparisonBenchmark,
    BenchmarkConfig
)
from huggingface_djmgnn_validation.parameter_comparison import ParameterComparison


class TestBenchmarkConfig:
    """Test the BenchmarkConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = BenchmarkConfig()
        
        assert config.model_repo_id == "your-username/djmgnn-model"
        assert config.model_filename == "model.pt"
        assert config.device == "auto"
        assert config.include_pfas is True
        assert config.include_organics is True
        assert config.parameter_types == ["charge", "vdw", "bond", "angle", "dihedral"]
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = BenchmarkConfig(
            model_repo_id="test/model",
            device="cpu",
            include_pfas=False,
            parameter_types=["charge", "bond"]
        )
        
        assert config.model_repo_id == "test/model"
        assert config.device == "cpu"
        assert config.include_pfas is False
        assert config.parameter_types == ["charge", "bond"]


class TestParameterComparisonBenchmark:
    """Test the ParameterComparisonBenchmark class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def benchmark_config(self, temp_dir):
        """Create a test benchmark configuration."""
        return BenchmarkConfig(
            model_repo_id="test/model",
            device="cpu",
            output_dir=str(temp_dir),
            generate_plots=False,  # Skip plots for testing
            include_pfas=True,
            include_organics=True,
            include_heteroatoms=False  # Keep test simple
        )
    
    @pytest.fixture
    def benchmark(self, benchmark_config):
        """Create a benchmark instance with mocked dependencies."""
        with patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_TORCH', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_RDKIT', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_HF_HUB', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_DJMGNN', True):
            
            # Mock torch device setup
            with patch('torch.cuda.is_available', return_value=False), \
                 patch('torch.device') as mock_device:
                mock_device.return_value = Mock()
                
                benchmark = ParameterComparisonBenchmark(benchmark_config)
                return benchmark
    
    def test_initialization(self, benchmark_config, temp_dir):
        """Test benchmark initialization."""
        with patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_TORCH', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_RDKIT', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_HF_HUB', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_DJMGNN', True):
            
            with patch('torch.cuda.is_available', return_value=False), \
                 patch('torch.device') as mock_device:
                mock_device.return_value = Mock()
                
                benchmark = ParameterComparisonBenchmark(benchmark_config)
                
                assert benchmark.config == benchmark_config
                assert benchmark.output_dir == temp_dir
                assert temp_dir.exists()
    
    def test_dependency_validation(self):
        """Test dependency validation."""
        # Test missing dependencies
        with patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_TORCH', False):
            with pytest.raises(ImportError, match="Missing required dependencies"):
                ParameterComparisonBenchmark()
    
    @pytest.mark.skipif(not HAS_RDKIT, reason="RDKit not available")
    def test_prepare_test_molecules(self, benchmark):
        """Test test molecule preparation."""
        # Mock RDKit functions
        with patch('rdkit.Chem.MolFromSmiles') as mock_mol_from_smiles, \
             patch('rdkit.Chem.AddHs') as mock_add_hs, \
             patch('rdkit.Chem.AllChem.EmbedMolecule') as mock_embed, \
             patch('rdkit.Chem.AllChem.MMFFOptimizeMolecule') as mock_optimize:
            
            # Create mock molecule
            mock_mol = Mock()
            mock_mol.GetNumAtoms.return_value = 10
            
            mock_mol_from_smiles.return_value = mock_mol
            mock_add_hs.return_value = mock_mol
            mock_embed.return_value = 0  # Success
            mock_optimize.return_value = None
            
            molecules = benchmark.prepare_test_molecules()
            
            assert len(molecules) > 0
            assert all(isinstance(mol_tuple, tuple) and len(mol_tuple) == 2 for mol_tuple in molecules)
            assert all(isinstance(mol_tuple[0], str) for mol_tuple in molecules)  # Names
    
    def test_compare_parameters(self, benchmark):
        """Test parameter comparison functionality."""
        # Create mock parameter lists
        djmgnn_params = [
            ParameterComparison(
                mol_id="test_mol",
                param_type="charge",
                param_name="C1",
                ref_value=0.0,
                pred_value=-0.123,
                unit="elementary_charge",
                ff_source="DJMGNN"
            ),
            ParameterComparison(
                mol_id="test_mol",
                param_type="bond",
                param_name="C1-C2_k",
                ref_value=0.0,
                pred_value=350.0,
                unit="kcal/mol/A^2",
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
            ),
            ParameterComparison(
                mol_id="test_mol",
                param_type="bond",
                param_name="C1-C2_k",
                ref_value=340.0,
                pred_value=0.0,
                unit="kcal/mol/A^2",
                ff_source="MMFF94"
            )
        ]
        
        comparison_df = benchmark.compare_parameters(djmgnn_params, mmff94_params)
        
        assert isinstance(comparison_df, pd.DataFrame)
        assert len(comparison_df) > 0
        assert "mol_id" in comparison_df.columns
        assert "param_type" in comparison_df.columns
        assert "ref_value" in comparison_df.columns
        assert "pred_value" in comparison_df.columns
    
    def test_analyze_results(self, benchmark):
        """Test results analysis functionality."""
        # Create test comparison DataFrame
        test_data = {
            'mol_id': ['mol1', 'mol1', 'mol2', 'mol2'],
            'param_type': ['charge', 'bond', 'charge', 'bond'],
            'param_name': ['C1', 'C1-C2', 'C1', 'C1-C2'],
            'ref_value': [0.1, 350.0, -0.2, 400.0],
            'pred_value': [0.12, 340.0, -0.18, 390.0],
            'unit': ['e', 'kcal/mol/A^2', 'e', 'kcal/mol/A^2'],
            'ff_source': ['test', 'test', 'test', 'test']
        }
        
        comparison_df = pd.DataFrame(test_data)
        
        analysis_results = benchmark.analyze_results(comparison_df)
        
        assert isinstance(analysis_results, dict)
        assert 'overall_stats' in analysis_results
        assert 'by_parameter_type' in analysis_results
        assert 'by_molecule' in analysis_results
        
        # Check overall statistics
        overall_stats = analysis_results['overall_stats']
        assert 'mae' in overall_stats
        assert 'rmse' in overall_stats
        assert 'r_squared' in overall_stats
        assert 'count' in overall_stats
        
        # Check parameter type statistics
        param_stats = analysis_results['by_parameter_type']
        assert 'charge' in param_stats
        assert 'bond' in param_stats
    
    def test_generate_report(self, benchmark, temp_dir):
        """Test report generation."""
        # Create minimal test data
        test_data = {
            'mol_id': ['mol1', 'mol1'],
            'param_type': ['charge', 'bond'],
            'param_name': ['C1', 'C1-C2'],
            'ref_value': [0.1, 350.0],
            'pred_value': [0.12, 340.0],
            'unit': ['e', 'kcal/mol/A^2'],
            'ff_source': ['test', 'test']
        }
        
        comparison_df = pd.DataFrame(test_data)
        analysis_results = benchmark.analyze_results(comparison_df)
        
        # Generate report
        report_file = "test_report.html"
        benchmark.generate_report(comparison_df, analysis_results, report_file)
        
        report_path = temp_dir / report_file
        assert report_path.exists()
        
        # Check report content
        with open(report_path, 'r') as f:
            content = f.read()
            assert "DJMGNN vs MMFF94 Parameter Comparison Report" in content
            assert "Executive Summary" in content
            assert "Statistical Analysis" in content
    
    def test_json_safe_conversion(self, benchmark):
        """Test JSON-safe conversion of numpy types."""
        test_data = {
            'float64': np.float64(1.5),
            'int32': np.int32(42),
            'array': np.array([1, 2, 3]),
            'nested': {
                'inner_float': np.float32(2.5),
                'inner_list': [np.int64(1), np.float64(2.0)]
            },
            'list': [np.int32(1), np.float64(2.0), np.nan],
            'nan_value': np.nan
        }
        
        safe_data = benchmark._make_json_safe(test_data)
        
        assert isinstance(safe_data['float64'], float)
        assert isinstance(safe_data['int32'], int)
        assert isinstance(safe_data['array'], list)
        assert isinstance(safe_data['nested']['inner_float'], float)
        assert isinstance(safe_data['nested']['inner_list'][0], int)
        assert isinstance(safe_data['nested']['inner_list'][1], float)
        assert safe_data['nan_value'] is None
    
    @patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.hf_hub_download')
    @patch('torch.load')
    def test_load_model_success(self, mock_torch_load, mock_hf_download, benchmark):
        """Test successful model loading."""
        # Mock the download and loading process
        mock_hf_download.return_value = "/fake/path/model.pt"
        mock_torch_load.return_value = {
            'model_state_dict': {},
            'input_dim': 128,
            'hidden_dim': 256,
            'output_dim': 19,
            'num_layers': 4,
            'dropout': 0.1
        }
        
        # Mock DJMGNN and related classes
        with patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.DJMGNN') as mock_djmgnn, \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.MolecularGraphProcessor') as mock_processor, \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.create_djmgnn_extractor') as mock_djmgnn_ext, \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.create_mmff94_extractor') as mock_mmff94_ext:
            
            mock_model = Mock()
            mock_djmgnn.return_value = mock_model
            
            result = benchmark.load_model()
            
            assert result is True
            assert benchmark.djmgnn_model == mock_model
            mock_model.to.assert_called_once()
            mock_model.eval.assert_called_once()
    
    @patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.hf_hub_download')
    def test_load_model_failure(self, mock_hf_download, benchmark):
        """Test model loading failure."""
        # Mock download failure
        mock_hf_download.side_effect = Exception("Download failed")
        
        result = benchmark.load_model()
        
        assert result is False
        assert benchmark.djmgnn_model is None


class TestIntegration:
    """Integration tests for the benchmark pipeline."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_minimal_benchmark_pipeline(self, temp_dir):
        """Test a minimal benchmark pipeline with mocked components."""
        config = BenchmarkConfig(
            model_repo_id="test/model",
            device="cpu",
            output_dir=str(temp_dir),
            generate_plots=False,
            include_pfas=False,
            include_organics=True,
            include_heteroatoms=False
        )
        
        # Mock all external dependencies
        with patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_TORCH', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_RDKIT', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_HF_HUB', True), \
             patch('huggingface_djmgnn_validation.parameter_comparison_benchmark.HAS_DJMGNN', True), \
             patch('torch.cuda.is_available', return_value=False), \
             patch('torch.device') as mock_device:
            
            mock_device.return_value = Mock()
            
            benchmark = ParameterComparisonBenchmark(config)
            
            # Mock the load_model method
            benchmark.load_model = Mock(return_value=True)
            
            # Mock prepare_test_molecules to return simple test data
            mock_mol = Mock()
            benchmark.prepare_test_molecules = Mock(return_value=[("test_mol", mock_mol)])
            
            # Mock parameter extraction
            mock_djmgnn_params = [
                ParameterComparison(
                    mol_id="test_mol",
                    param_type="charge",
                    param_name="C1",
                    ref_value=0.0,
                    pred_value=0.1,
                    unit="elementary_charge",
                    ff_source="DJMGNN"
                )
            ]
            
            mock_mmff94_params = [
                ParameterComparison(
                    mol_id="test_mol",
                    param_type="charge",
                    param_name="C1",
                    ref_value=0.12,
                    pred_value=0.0,
                    unit="elementary_charge",
                    ff_source="MMFF94"
                )
            ]
            
            benchmark.extract_parameters = Mock(return_value=(mock_djmgnn_params, mock_mmff94_params))
            
            # Run the benchmark
            results = benchmark.run_benchmark()
            
            # Verify results
            assert isinstance(results, dict)
            assert 'comparison_df' in results
            assert 'analysis_results' in results
            assert 'config' in results
            
            # Check that files were created
            assert (temp_dir / "parameter_comparisons.csv").exists()
            assert (temp_dir / "analysis_results.json").exists()
            assert (temp_dir / "benchmark_report.html").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])