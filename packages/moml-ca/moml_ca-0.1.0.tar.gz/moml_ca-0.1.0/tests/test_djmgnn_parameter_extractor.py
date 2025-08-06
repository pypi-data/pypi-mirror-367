"""
Tests for DJMGNN Parameter Extractor

This module tests the systematic extraction of DJMGNN's 19 force field parameters
and their mapping to the ParameterComparison schema.
"""

import pytest
import numpy as np
import torch
from rdkit import Chem
from rdkit.Chem import AllChem

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from huggingface_djmgnn_validation.djmgnn_parameter_extractor import (
    DJMGNNParameterExtractor,
    ParameterMapping,
    create_djmgnn_extractor
)
from huggingface_djmgnn_validation.parameter_comparison import ParameterComparison


@pytest.fixture
def sample_molecule():
    """Create a sample PFAS molecule for testing."""
    # PFOA-like molecule: C(C(C(C(F)(F)F)(F)F)(F)F)C(=O)O
    smiles = "C(C(C(C(F)(F)F)(F)F)(F)F)C(=O)O"
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    return mol


@pytest.fixture
def sample_djmgnn_outputs():
    """Create sample DJMGNN outputs for testing."""
    # Simulate DJMGNN outputs
    n_atoms = 20  # Approximate for PFOA with hydrogens
    
    # Node predictions (partial charges) - shape: [n_atoms, 3]
    node_pred = torch.randn(n_atoms, 3) * 0.5  # Realistic charge range
    
    # Graph predictions (19 force field parameters)
    graph_pred = torch.randn(1, 19) * 2.0  # 19 parameters
    
    # Energy prediction
    energy_pred = torch.randn(1, 1) * 100.0
    
    return {
        'node_pred': node_pred,
        'graph_pred': graph_pred,
        'energy_pred': energy_pred
    }


@pytest.fixture
def extractor():
    """Create a DJMGNN parameter extractor."""
    return create_djmgnn_extractor()


class TestParameterMapping:
    """Test the ParameterMapping configuration."""
    
    def test_default_mapping(self):
        """Test default parameter mapping configuration."""
        mapping = ParameterMapping()
        
        assert len(mapping.vdw_epsilon_indices) == 4
        assert len(mapping.vdw_sigma_indices) == 4
        assert len(mapping.vdw_atom_types) == 4
        assert mapping.vdw_atom_types == ['C', 'O', 'F', 'H']
        
        assert len(mapping.bond_k_indices) == 4
        assert len(mapping.bond_r0_indices) == 4
        assert len(mapping.bond_types) == 4
        
        assert mapping.angle_k_index == 16
        assert mapping.angle_theta0_index == 17
        assert mapping.dihedral_barrier_index == 18


class TestDJMGNNParameterExtractor:
    """Test the main parameter extractor functionality."""
    
    def test_initialization(self, extractor):
        """Test extractor initialization."""
        assert extractor is not None
        assert extractor.parameter_mapping is not None
        assert 'hartree_to_kcal_mol' in extractor.unit_conversions
    
    def test_extract_charges(self, extractor, sample_djmgnn_outputs, sample_molecule):
        """Test charge parameter extraction."""
        charges = extractor.extract_charges(sample_djmgnn_outputs, sample_molecule)
        
        assert len(charges) > 0
        assert all(isinstance(param, ParameterComparison) for param in charges)
        assert all(param.param_type == "charge" for param in charges)
        assert all(param.unit == "elementary_charge" for param in charges)
        assert all(param.ff_source == "DJMGNN" for param in charges)
    
    def test_extract_vdw(self, extractor, sample_djmgnn_outputs, sample_molecule):
        """Test van der Waals parameter extraction."""
        vdw_params = extractor.extract_vdw(sample_djmgnn_outputs, sample_molecule)
        
        assert len(vdw_params) == 8  # 4 atom types × 2 params (epsilon, sigma)
        assert all(isinstance(param, ParameterComparison) for param in vdw_params)
        assert all(param.param_type == "vdw" for param in vdw_params)
        assert all(param.ff_source == "DJMGNN" for param in vdw_params)
        
        # Check that we have epsilon and sigma for each atom type
        param_names = [param.param_name for param in vdw_params]
        for atom_type in ['C', 'O', 'F', 'H']:
            assert f"{atom_type}_epsilon" in param_names
            assert f"{atom_type}_sigma" in param_names
    
    def test_extract_bonds(self, extractor, sample_djmgnn_outputs, sample_molecule):
        """Test bond parameter extraction."""
        bond_params = extractor.extract_bonds(sample_djmgnn_outputs, sample_molecule)
        
        assert len(bond_params) == 8  # 4 bond types × 2 params (k, r0)
        assert all(isinstance(param, ParameterComparison) for param in bond_params)
        assert all(param.param_type == "bond" for param in bond_params)
        assert all(param.ff_source == "DJMGNN" for param in bond_params)
        
        # Check units
        k_params = [p for p in bond_params if p.param_name.endswith('_k')]
        r0_params = [p for p in bond_params if p.param_name.endswith('_r0')]
        
        assert all(p.unit == "kcal/mol/A^2" for p in k_params)
        assert all(p.unit == "A" for p in r0_params)
    
    def test_extract_angles(self, extractor, sample_djmgnn_outputs, sample_molecule):
        """Test angle parameter extraction."""
        angle_params = extractor.extract_angles(sample_djmgnn_outputs, sample_molecule)
        
        assert len(angle_params) == 2  # k and theta0
        assert all(isinstance(param, ParameterComparison) for param in angle_params)
        assert all(param.param_type == "angle" for param in angle_params)
        assert all(param.ff_source == "DJMGNN" for param in angle_params)
        
        # Check parameter names and units
        param_names = [param.param_name for param in angle_params]
        assert "generic_angle_k" in param_names
        assert "generic_angle_theta0" in param_names
        
        k_param = next(p for p in angle_params if p.param_name == "generic_angle_k")
        theta_param = next(p for p in angle_params if p.param_name == "generic_angle_theta0")
        
        assert k_param.unit == "kcal/mol/rad^2"
        assert theta_param.unit == "degrees"
    
    def test_extract_dihedrals(self, extractor, sample_djmgnn_outputs, sample_molecule):
        """Test dihedral parameter extraction."""
        dihedral_params = extractor.extract_dihedrals(sample_djmgnn_outputs, sample_molecule)
        
        assert len(dihedral_params) == 1  # barrier height only
        assert all(isinstance(param, ParameterComparison) for param in dihedral_params)
        assert all(param.param_type == "dihedral" for param in dihedral_params)
        assert all(param.ff_source == "DJMGNN" for param in dihedral_params)
        
        param = dihedral_params[0]
        assert param.param_name == "generic_dihedral_barrier"
        assert param.unit == "kcal/mol"
    
    def test_extract_all_parameters(self, extractor, sample_djmgnn_outputs, sample_molecule):
        """Test extraction of all parameters together."""
        all_params = extractor.extract_all_parameters(sample_djmgnn_outputs, sample_molecule)
        
        assert len(all_params) > 0
        assert all(isinstance(param, ParameterComparison) for param in all_params)
        
        # Count by parameter type
        param_counts = {}
        for param in all_params:
            param_counts[param.param_type] = param_counts.get(param.param_type, 0) + 1
        
        # Should have all parameter types
        expected_types = {'charge', 'vdw', 'bond', 'angle', 'dihedral'}
        assert set(param_counts.keys()) == expected_types
        
        # Check expected counts for graph-level parameters
        assert param_counts['vdw'] == 8      # 4 atom types × 2 params
        assert param_counts['bond'] == 8     # 4 bond types × 2 params
        assert param_counts['angle'] == 2    # k + theta0
        assert param_counts['dihedral'] == 1 # barrier only
    
    def test_parameter_count(self, extractor):
        """Test parameter count reporting."""
        counts = extractor.get_parameter_count()
        
        assert 'total_graph_params' in counts
        assert counts['total_graph_params'] == 19
        assert counts['vdw_params'] == 8
        assert counts['bond_params'] == 8
        assert counts['angle_params'] == 2
        assert counts['dihedral_params'] == 1
    
    def test_validate_extraction(self, extractor, sample_djmgnn_outputs, sample_molecule):
        """Test extraction validation."""
        all_params = extractor.extract_all_parameters(sample_djmgnn_outputs, sample_molecule)
        validation = extractor.validate_extraction(all_params)
        
        assert 'total_parameters' in validation
        assert 'by_type' in validation
        assert 'warnings' in validation
        assert 'errors' in validation
        assert 'is_valid' in validation
        
        assert validation['total_parameters'] == len(all_params)
    
    def test_missing_outputs(self, extractor, sample_molecule):
        """Test handling of missing outputs."""
        # Test with missing node_pred
        outputs_no_node = {'graph_pred': torch.randn(1, 19)}
        charges = extractor.extract_charges(outputs_no_node, sample_molecule)
        assert len(charges) == 0
        
        # Test with missing graph_pred  
        outputs_no_graph = {'node_pred': torch.randn(10, 3)}
        vdw_params = extractor.extract_vdw(outputs_no_graph, sample_molecule)
        assert len(vdw_params) == 0
    
    def test_wrong_parameter_count(self, extractor, sample_molecule):
        """Test handling of wrong parameter count in graph_pred."""
        # Wrong number of parameters (should be 19)
        outputs_wrong_count = {'graph_pred': torch.randn(1, 15)}
        vdw_params = extractor.extract_vdw(outputs_wrong_count, sample_molecule)
        assert len(vdw_params) == 0
    
    def test_documentation(self, extractor):
        """Test parameter documentation generation."""
        doc = extractor.get_parameter_documentation()
        
        assert isinstance(doc, str)
        assert len(doc) > 0
        assert "19-Parameter" in doc
        assert "Parameter Index Mapping" in doc
        assert "Unit Conversions" in doc


class TestFactoryFunction:
    """Test the factory function."""
    
    def test_create_djmgnn_extractor(self):
        """Test factory function."""
        extractor = create_djmgnn_extractor()
        
        assert isinstance(extractor, DJMGNNParameterExtractor)
        assert extractor.parameter_mapping is not None
    
    def test_create_with_custom_mapping(self):
        """Test factory function with custom mapping."""
        custom_mapping = ParameterMapping()
        custom_mapping.vdw_atom_types = ['C', 'N', 'O', 'F']  # Different atom types
        
        extractor = create_djmgnn_extractor(custom_mapping)
        
        assert isinstance(extractor, DJMGNNParameterExtractor)
        assert extractor.parameter_mapping.vdw_atom_types == ['C', 'N', 'O', 'F']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])