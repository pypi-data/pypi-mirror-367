#!/usr/bin/env python3
"""
Test suite for DJMGNN vs DFT Timing Benchmark

This module tests the timing benchmark functionality to ensure accurate
speedup measurements and validation of the 1000× claim.
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from huggingface_djmgnn_validation.timing_benchmark import (
    TimingBenchmark, 
    MoleculeInfo, 
    TimingResult, 
    DFTTimingEstimate, 
    SpeedupAnalysis,
    create_timing_benchmark
)
from huggingface_djmgnn_validation.parameter_comparison_benchmark import BenchmarkConfig


class TestTimingBenchmark(unittest.TestCase):
    """Test cases for timing benchmark functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = BenchmarkConfig(
            generate_plots=False,  # Skip plotting in tests
            statistical_tests=False,
            save_raw_data=True
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_timing_benchmark_initialization(self):
        """Test timing benchmark initialization."""
        benchmark = create_timing_benchmark(self.config)
        
        # Check basic initialization
        self.assertIsNotNone(benchmark)
        self.assertIsInstance(benchmark, TimingBenchmark)
        self.assertEqual(benchmark.config, self.config)
        
        # Check test molecules are loaded
        self.assertGreater(len(benchmark.test_molecules), 0)
        
        # Check DFT timing database is created
        self.assertGreater(len(benchmark.dft_timing_db), 0)
        
        # Check system info is collected
        self.assertIn('platform', benchmark.system_info)
        self.assertIn('cpu_count', benchmark.system_info)
        self.assertIn('memory_gb', benchmark.system_info)
    
    def test_molecule_definitions(self):
        """Test test molecule definitions."""
        benchmark = create_timing_benchmark(self.config)
        
        # Check molecule categories
        categories = set(mol.category for mol in benchmark.test_molecules)
        expected_categories = {'small', 'medium', 'large'}
        self.assertEqual(categories, expected_categories)
        
        # Check PFAS molecules
        pfas_molecules = [mol for mol in benchmark.test_molecules if mol.is_pfas]
        self.assertEqual(len(pfas_molecules), len(benchmark.test_molecules))  # All should be PFAS
        
        # Check atom counts increase with category
        small_atoms = [mol.num_atoms for mol in benchmark.test_molecules if mol.category == 'small']
        medium_atoms = [mol.num_atoms for mol in benchmark.test_molecules if mol.category == 'medium']
        large_atoms = [mol.num_atoms for mol in benchmark.test_molecules if mol.category == 'large']
        
        # Small molecules should have fewer atoms than large ones
        if small_atoms and large_atoms:
            self.assertLess(max(small_atoms), max(large_atoms))
    
    def test_dft_timing_estimates(self):
        """Test DFT timing estimate calculations."""
        benchmark = create_timing_benchmark(self.config)
        
        # Check all molecules have DFT estimates
        for mol in benchmark.test_molecules:
            self.assertIn(mol.name, benchmark.dft_timing_db)
            
            estimate = benchmark.dft_timing_db[mol.name]
            self.assertIsInstance(estimate, DFTTimingEstimate)
            
            # Check timing components are positive
            self.assertGreater(estimate.geometry_optimization_hours, 0)
            self.assertGreater(estimate.frequency_calculation_hours, 0)
            self.assertGreater(estimate.single_point_energy_hours, 0)
            self.assertGreater(estimate.total_dft_hours, 0)
            
            # Check total is sum of components
            expected_total = (estimate.geometry_optimization_hours + 
                            estimate.frequency_calculation_hours + 
                            estimate.single_point_energy_hours)
            self.assertAlmostEqual(estimate.total_dft_hours, expected_total, places=6)
    
    def test_timing_result_creation(self):
        """Test timing result data structure."""
        result = TimingResult(
            molecule_name="test_mol",
            operation="inference",
            time_seconds=0.05,
            memory_mb=200.0,
            cpu_percent=75.0,
            success=True
        )
        
        self.assertEqual(result.molecule_name, "test_mol")
        self.assertEqual(result.operation, "inference")
        self.assertEqual(result.time_seconds, 0.05)
        self.assertEqual(result.memory_mb, 200.0)
        self.assertEqual(result.cpu_percent, 75.0)
        self.assertTrue(result.success)
        self.assertIsNone(result.error_message)
    
    def test_speedup_calculation(self):
        """Test speedup calculation logic."""
        benchmark = create_timing_benchmark(self.config)
        
        # Create mock timing results
        timing_results = [
            TimingResult(
                molecule_name="CF4",
                operation="total_pipeline",
                time_seconds=0.05,  # 50ms
                memory_mb=200.0,
                cpu_percent=60.0,
                success=True
            ),
            TimingResult(
                molecule_name="CF4",
                operation="total_pipeline", 
                time_seconds=0.06,  # 60ms
                memory_mb=210.0,
                cpu_percent=65.0,
                success=True
            )
        ]
        
        # Calculate speedup
        speedup_analyses = benchmark.calculate_speedup_analysis(timing_results)
        
        self.assertEqual(len(speedup_analyses), 1)
        analysis = speedup_analyses[0]
        
        self.assertEqual(analysis.molecule_name, "CF4")
        self.assertAlmostEqual(analysis.djmgnn_time_seconds, 0.055, places=3)  # Average of 0.05 and 0.06
        self.assertGreater(analysis.dft_time_seconds, 0)
        self.assertGreater(analysis.speedup_factor, 1)
    
    def test_timing_statistics_calculation(self):
        """Test timing statistics calculation."""
        benchmark = create_timing_benchmark(self.config)
        
        # Create mock timing results
        timing_results = [
            TimingResult("mol1", "inference", 0.05, 200, 60, True),
            TimingResult("mol1", "parameter_extraction", 0.01, 50, 40, True),
            TimingResult("mol1", "total_pipeline", 0.06, 250, 50, True),
            TimingResult("mol2", "inference", 0.08, 220, 65, True),
            TimingResult("mol2", "parameter_extraction", 0.02, 60, 45, True),
            TimingResult("mol2", "total_pipeline", 0.10, 280, 55, True),
        ]
        
        stats = benchmark._calculate_timing_statistics(timing_results)
        
        # Check overall structure
        self.assertIn('by_operation', stats)
        self.assertIn('by_molecule_category', stats)
        self.assertIn('overall', stats)
        
        # Check operation statistics
        self.assertIn('inference', stats['by_operation'])
        self.assertIn('parameter_extraction', stats['by_operation'])
        self.assertIn('total_pipeline', stats['by_operation'])
        
        # Check inference statistics
        inference_stats = stats['by_operation']['inference']
        self.assertEqual(inference_stats['count'], 2)
        self.assertAlmostEqual(inference_stats['mean_seconds'], 0.065, places=3)
    
    def test_speedup_statistics_calculation(self):
        """Test speedup statistics calculation."""
        benchmark = create_timing_benchmark(self.config)
        
        # Create mock speedup analyses
        speedup_analyses = [
            SpeedupAnalysis("mol1", 0.05, 3600, 72000, "small", 8),  # 72,000x speedup
            SpeedupAnalysis("mol2", 0.10, 7200, 72000, "medium", 12),  # 72,000x speedup
            SpeedupAnalysis("mol3", 0.20, 14400, 72000, "large", 20),  # 72,000x speedup
        ]
        
        stats = benchmark._calculate_speedup_statistics(speedup_analyses)
        
        # Check overall statistics
        self.assertIn('overall', stats)
        overall = stats['overall']
        self.assertEqual(overall['num_molecules'], 3)
        self.assertAlmostEqual(overall['mean_speedup'], 72000, places=0)
        self.assertAlmostEqual(overall['median_speedup'], 72000, places=0)
        
        # Check validation
        self.assertIn('validation', stats)
        validation = stats['validation']
        self.assertTrue(validation['claim_1000x_validated'])
        self.assertEqual(validation['molecules_above_1000x'], 3)
        self.assertEqual(validation['percentage_above_1000x'], 100.0)
    
    @patch('huggingface_djmgnn_validation.timing_benchmark.ParameterComparisonBenchmark')
    def test_mock_djmgnn_timing(self, mock_benchmark_class):
        """Test DJMGNN timing measurement with mocked components."""
        # Set up mock benchmark
        mock_benchmark_instance = Mock()
        mock_benchmark_instance.load_model.return_value = None
        mock_benchmark_instance.run_djmgnn_inference.return_value = {
            'node_pred': np.array([0.1, -0.2, 0.3]),
            'graph_pred': np.random.random(19)
        }
        mock_benchmark_class.return_value = mock_benchmark_instance
        
        # Create timing benchmark
        benchmark = create_timing_benchmark(self.config)
        benchmark.benchmark = mock_benchmark_instance
        
        # Test molecule
        test_mol = benchmark.test_molecules[0]
        
        # Mock the extractor
        with patch.object(benchmark.djmgnn_extractor, 'extract_all_parameters') as mock_extract:
            mock_extract.return_value = [Mock()]  # Mock parameter list
            
            # Measure timing (single run for speed)
            timing_results = benchmark.measure_djmgnn_timing(test_mol, num_runs=1)
            
            # Check results
            self.assertGreater(len(timing_results), 0)
            
            # Check for expected operations
            operations = [r.operation for r in timing_results]
            self.assertIn('inference', operations)
            self.assertIn('parameter_extraction', operations)
            self.assertIn('total_pipeline', operations)
            
            # Check successful results
            successful_results = [r for r in timing_results if r.success]
            self.assertGreater(len(successful_results), 0)
    
    def test_report_generation(self):
        """Test timing report generation."""
        benchmark = create_timing_benchmark(self.config)
        
        # Create mock results
        mock_results = {
            'benchmark_info': {
                'start_time': '2024-01-01T00:00:00',
                'end_time': '2024-01-01T00:05:00',
                'duration_minutes': 5.0,
                'system_info': benchmark.system_info,
                'num_molecules_tested': 2,
                'num_successful': 2,
                'num_failed': 0,
                'num_runs_per_molecule': 3
            },
            'test_molecules': [mol.__dict__ for mol in benchmark.test_molecules[:2]],
            'timing_results': [
                TimingResult("mol1", "total_pipeline", 0.05, 200, 60, True).__dict__,
                TimingResult("mol2", "total_pipeline", 0.10, 220, 65, True).__dict__,
            ],
            'dft_estimates': {
                name: estimate.__dict__ 
                for name, estimate in list(benchmark.dft_timing_db.items())[:2]
            },
            'speedup_analyses': [
                SpeedupAnalysis("mol1", 0.05, 3600, 72000, "small", 8).__dict__,
                SpeedupAnalysis("mol2", 0.10, 7200, 72000, "medium", 12).__dict__,
            ],
            'timing_statistics': {'overall': {'mean_pipeline_seconds': 0.075}},
            'speedup_statistics': {
                'overall': {'mean_speedup': 72000, 'median_speedup': 72000},
                'validation': {'claim_1000x_validated': True, 'percentage_above_1000x': 100.0}
            },
            'successful_molecules': ['mol1', 'mol2'],
            'failed_molecules': []
        }
        
        # Generate report
        report_path = benchmark.generate_timing_report(mock_results, self.test_dir)
        
        # Check report file was created
        self.assertTrue(report_path.exists())
        self.assertEqual(report_path.suffix, '.html')
        
        # Check raw data files
        json_path = self.test_dir / "timing_results.json"
        self.assertTrue(json_path.exists())
        
        csv_path = self.test_dir / "speedup_analysis.csv"
        self.assertTrue(csv_path.exists())
        
        # Check HTML content
        html_content = report_path.read_text()
        self.assertIn('DJMGNN vs DFT Timing Benchmark Report', html_content)
        self.assertIn('72000', html_content)  # Check speedup value appears
        self.assertIn('VALIDATED', html_content)  # Check validation status
    
    def test_molecule_info_dataclass(self):
        """Test MoleculeInfo dataclass."""
        mol_info = MoleculeInfo(
            name="CF4",
            smiles="C(F)(F)(F)F",
            category="small",
            num_atoms=5,
            num_heavy_atoms=5,
            molecular_weight=88.0,
            is_pfas=True,
            description="Tetrafluoromethane"
        )
        
        self.assertEqual(mol_info.name, "CF4")
        self.assertEqual(mol_info.smiles, "C(F)(F)(F)F")
        self.assertEqual(mol_info.category, "small")
        self.assertEqual(mol_info.num_atoms, 5)
        self.assertTrue(mol_info.is_pfas)
    
    def test_dft_estimate_dataclass(self):
        """Test DFTTimingEstimate dataclass."""
        estimate = DFTTimingEstimate(
            molecule_name="CF4",
            num_atoms=5,
            num_heavy_atoms=5,
            geometry_optimization_hours=0.5,
            frequency_calculation_hours=1.5,
            single_point_energy_hours=0.1,
            total_dft_hours=2.1
        )
        
        self.assertEqual(estimate.molecule_name, "CF4")
        self.assertEqual(estimate.num_atoms, 5)
        self.assertEqual(estimate.total_dft_hours, 2.1)
        self.assertEqual(estimate.method, "B3LYP")  # Default value
        self.assertEqual(estimate.basis_set, "6-31G(d)")  # Default value


class TestTimingBenchmarkIntegration(unittest.TestCase):
    """Integration tests for timing benchmark."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up integration test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_full_demo_benchmark(self):
        """Test complete demo benchmark workflow."""
        config = BenchmarkConfig(
            generate_plots=False,  # Skip plotting for faster test
            statistical_tests=False,
            save_raw_data=True
        )
        
        benchmark = create_timing_benchmark(config)
        
        # Run demo timing (minimal runs for speed)
        with patch('huggingface_djmgnn_validation.timing_benchmark.ParameterComparisonBenchmark'):
            # Mock the benchmark components for speed
            mock_results = {
                'benchmark_info': {
                    'start_time': '2024-01-01T00:00:00',
                    'end_time': '2024-01-01T00:01:00',
                    'duration_minutes': 1.0,
                    'system_info': benchmark.system_info,
                    'num_molecules_tested': len(benchmark.test_molecules),
                    'num_successful': len(benchmark.test_molecules),
                    'num_failed': 0,
                    'num_runs_per_molecule': 2
                },
                'test_molecules': [mol.__dict__ for mol in benchmark.test_molecules],
                'timing_results': [],
                'dft_estimates': {name: est.__dict__ for name, est in benchmark.dft_timing_db.items()},
                'speedup_analyses': [],
                'timing_statistics': {'overall': {'mean_pipeline_seconds': 0.08}},
                'speedup_statistics': {
                    'overall': {'mean_speedup': 50000, 'median_speedup': 45000},
                    'validation': {'claim_1000x_validated': True, 'percentage_above_1000x': 85.0}
                },
                'successful_molecules': [mol.name for mol in benchmark.test_molecules],
                'failed_molecules': []
            }
            
            # Generate report
            report_path = benchmark.generate_timing_report(mock_results, self.test_dir)
            
            # Verify report generation
            self.assertTrue(report_path.exists())
            
            # Check expected files
            expected_files = [
                'timing_report.html',
                'timing_results.json'
            ]
            
            for filename in expected_files:
                file_path = self.test_dir / filename
                self.assertTrue(file_path.exists(), f"Expected file {filename} not found")
    
    def test_error_handling(self):
        """Test error handling in timing benchmark."""
        benchmark = create_timing_benchmark()
        
        # Test with invalid molecule (should handle gracefully)
        invalid_mol = MoleculeInfo(
            name="invalid",
            smiles="INVALID_SMILES",
            category="test",
            num_atoms=0,
            num_heavy_atoms=0,
            molecular_weight=0.0,
            is_pfas=False,
            description="Invalid test molecule"
        )
        
        # This should not crash, but return empty results
        timing_results = benchmark.measure_djmgnn_timing(invalid_mol, num_runs=1)
        
        # Should handle the error gracefully
        self.assertIsInstance(timing_results, list)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)