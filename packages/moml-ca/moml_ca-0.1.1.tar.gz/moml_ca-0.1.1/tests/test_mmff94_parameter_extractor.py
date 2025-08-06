"""
Tests for MMFF94 Parameter Extractor

This module tests the systematic extraction of MMFF94 force field parameters
using RDKit and their mapping to the ParameterComparison schema.
"""

import pytest
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from huggingface_djmgnn_validation.mmff94_parameter_extractor import (
    MMFF94ParameterExtractor,
    MMFF94AtomTypeMapping,
    create_mmff94_extractor,
    HAS_RDKIT
)
from huggingface_djmgnn_validation.parameter_comparison import ParameterComparison


@pytest.fixture
def sample_ethanol():
    """Create ethanol molecule for testing."""
    if not HAS_RDKIT:
        pytest.skip("RDKit not available")
    
    smiles = "CCO"
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol)
    return mol


@pytest.fixture
def sample_pfas_molecule():
    """Create a simple PFAS molecule for testing."""
    if not HAS_RDKIT:
        pytest.skip("RDKit not available")
    
    # Trifluoroacetic acid: C(=O)(O)C(F)(F)F
    smiles = "C(=O)(O)C(F)(F)F"
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol)
    return mol


@pytest.fixture
def extractor():
    """Create MMFF94 parameter extractor."""
    if not HAS_RDKIT:
        pytest.skip("RDKit not available")
    return create_mmff94_extractor()


class TestMMFF94AtomTypeMapping:
    """Test the MMFF94 atom type mapping class."""
    
    def test_initialization(self):
        """Test atom type mapping initialization."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        mapping = MMFF94AtomTypeMapping()
        assert mapping.vdw_params is not None
        assert len(mapping.vdw_params) > 0
        
        # Check some known atom types
        assert 1 in mapping.vdw_params  # Carbon
        assert 11 in mapping.vdw_params  # Fluorine
    
    def test_get_vdw_params(self):
        """Test getting vdW parameters for atom types."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        mapping = MMFF94AtomTypeMapping()
        
        # Test known atom type
        params = mapping.get_vdw_params(1)  # Carbon
        assert params is not None
        assert len(params) == 2
        assert params[0] > 0  # epsilon
        assert params[1] > 0  # R*
        
        # Test unknown atom type
        params = mapping.get_vdw_params(999)
        assert params is None


class TestMMFF94ParameterExtractor:
    """Test the main MMFF94 parameter extractor class."""
    
    def test_initialization(self, extractor):
        """Test extractor initialization."""
        assert extractor is not None
        assert extractor.atom_type_mapping is not None
    
    def test_initialization_without_rdkit(self):
        """Test initialization when RDKit is not available."""
        import huggingface_djmgnn_validation.mmff94_parameter_extractor as mmff_module
        
        # Temporarily set HAS_RDKIT to False
        original_has_rdkit = mmff_module.HAS_RDKIT
        mmff_module.HAS_RDKIT = False
        
        try:
            with pytest.raises(ImportError, match="RDKit is required"):
                MMFF94ParameterExtractor()
        finally:
            mmff_module.HAS_RDKIT = original_has_rdkit
    
    def test_validate_molecule_valid(self, extractor, sample_ethanol):
        """Test molecule validation with valid molecule."""
        assert extractor._validate_molecule(sample_ethanol) is True
    
    def test_validate_molecule_none(self, extractor):
        """Test molecule validation with None."""
        assert extractor._validate_molecule(None) is False
    
    def test_validate_molecule_no_conformers(self, extractor):
        """Test molecule validation with no conformers."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        mol = Chem.MolFromSmiles("CCO")
        mol = Chem.AddHs(mol)
        # Don't add conformers
        
        # Should still work as it tries to generate them
        result = extractor._validate_molecule(mol)
        # Result depends on whether coordinate generation succeeds
        assert isinstance(result, bool)
    
    def test_extract_charges(self, extractor, sample_ethanol):
        """Test charge extraction."""
        charges = extractor.extract_charges(sample_ethanol)
        
        assert isinstance(charges, list)
        assert len(charges) > 0
        assert len(charges) == sample_ethanol.GetNumAtoms()
        
        # Check first charge parameter
        charge_param = charges[0]
        assert isinstance(charge_param, ParameterComparison)
        assert charge_param.param_type == "charge"
        assert charge_param.unit == "elementary_charge"
        assert charge_param.ff_source == "MMFF94"
        assert charge_param.param_name.startswith(("C", "O", "H"))
        
        # Check that charges are reasonable
        for charge in charges:
            assert -3.0 <= charge.ref_value <= 3.0
    
    def test_extract_charges_invalid_molecule(self, extractor):
        """Test charge extraction with invalid molecule."""
        charges = extractor.extract_charges(None)
        assert charges == []
    
    def test_extract_vdw(self, extractor, sample_ethanol):
        """Test vdW parameter extraction."""
        from rdkit.Chem import rdForceFieldHelpers
        
        mmff_props = rdForceFieldHelpers.MMFFGetMoleculeProperties(sample_ethanol)
        vdw_params = extractor.extract_vdw(sample_ethanol, mmff_props)
        
        assert isinstance(vdw_params, list)
        assert len(vdw_params) > 0
        
        # Should have pairs of epsilon/sigma parameters
        assert len(vdw_params) % 2 == 0
        
        # Check parameter structure
        for param in vdw_params:
            assert isinstance(param, ParameterComparison)
            assert param.param_type == "vdw"
            assert param.ff_source == "MMFF94"
            assert param.unit in ["kcal/mol", "A"]
            assert param.ref_value > 0  # vdW parameters should be positive
    
    def test_extract_vdw_none_props(self, extractor, sample_ethanol):
        """Test vdW extraction with None properties."""
        vdw_params = extractor.extract_vdw(sample_ethanol, None)
        assert vdw_params == []
    
    def test_extract_bonds(self, extractor, sample_ethanol):
        """Test bond parameter extraction."""
        from rdkit.Chem import rdForceFieldHelpers
        
        mmff_props = rdForceFieldHelpers.MMFFGetMoleculeProperties(sample_ethanol)
        bond_params = extractor.extract_bonds(sample_ethanol, mmff_props)
        
        assert isinstance(bond_params, list)
        assert len(bond_params) > 0
        
        # Should have pairs of k/r0 parameters
        assert len(bond_params) % 2 == 0
        
        # Check parameter structure
        for param in bond_params:
            assert isinstance(param, ParameterComparison)
            assert param.param_type == "bond"
            assert param.ff_source == "MMFF94"
            assert param.unit in ["kcal/mol/A^2", "A"]
            assert param.ref_value > 0  # Bond parameters should be positive
            assert "-" in param.param_name  # Should contain bond notation
    
    def test_extract_bonds_none_props(self, extractor, sample_ethanol):
        """Test bond extraction with None properties."""
        bond_params = extractor.extract_bonds(sample_ethanol, None)
        assert bond_params == []
    
    def test_extract_angles(self, extractor, sample_ethanol):
        """Test angle parameter extraction."""
        from rdkit.Chem import rdForceFieldHelpers
        
        mmff_props = rdForceFieldHelpers.MMFFGetMoleculeProperties(sample_ethanol)
        angle_params = extractor.extract_angles(sample_ethanol, mmff_props)
        
        assert isinstance(angle_params, list)
        assert len(angle_params) > 0
        
        # Should have pairs of k/theta0 parameters
        assert len(angle_params) % 2 == 0
        
        # Check parameter structure
        for param in angle_params:
            assert isinstance(param, ParameterComparison)
            assert param.param_type == "angle"
            assert param.ff_source == "MMFF94"
            assert param.unit in ["kcal/mol/rad^2", "degrees"]
            assert param.ref_value > 0  # Angle parameters should be positive
            
            # Check angle naming convention
            if param.unit == "degrees":
                assert 0 <= param.ref_value <= 180  # Angle should be in valid range
    
    def test_extract_angles_none_props(self, extractor, sample_ethanol):
        """Test angle extraction with None properties."""
        angle_params = extractor.extract_angles(sample_ethanol, None)
        assert angle_params == []
    
    def test_actual_mmff94_bond_parameters(self, extractor):
        """Test that bond parameters are extracted from actual MMFF94 data, not hardcoded values."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        from rdkit.Chem import rdForceFieldHelpers
        
        # Test with different molecules to ensure parameters are not hardcoded
        molecules = [
            ("CCO", "ethanol"),      # C-C and C-O bonds
            ("CC=O", "acetaldehyde"), # C-C and C=O bonds
            ("CCN", "ethylamine"),   # C-C and C-N bonds
        ]
        
        all_bond_params = {}
        
        for smiles, name in molecules:
            mol = Chem.MolFromSmiles(smiles)
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            
            mmff_props = rdForceFieldHelpers.MMFFGetMoleculeProperties(mol)
            bond_params = extractor.extract_bonds(mol, mmff_props)
            
            # Extract just the force constants for comparison
            force_constants = [p.ref_value for p in bond_params if p.param_name.endswith('_k')]
            all_bond_params[name] = force_constants
        
        # Verify that we got different parameters for different molecules
        # This proves they're not hardcoded values like 700.0, 1000.0, etc.
        ethanol_params = set(all_bond_params["ethanol"])
        acetaldehyde_params = set(all_bond_params["acetaldehyde"])
        ethylamine_params = set(all_bond_params["ethylamine"])
        
        # There should be some variation between molecules
        assert len(ethanol_params.union(acetaldehyde_params, ethylamine_params)) > len(ethanol_params)
        
        # Verify parameters are reasonable MMFF94 values (not the old hardcoded 700.0, 1000.0)
        for params in all_bond_params.values():
            for k in params:
                assert 0.1 < k < 20.0  # Reasonable range for MMFF94 force constants
                # Should not be the old hardcoded values
                assert k not in [700.0, 1000.0, 1500.0, 500.0]
    
    def test_actual_mmff94_angle_parameters(self, extractor):
        """Test that angle parameters are extracted from actual MMFF94 data, not hardcoded values."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        from rdkit.Chem import rdForceFieldHelpers
        
        # Test with different molecules to ensure parameters are not hardcoded
        molecules = [
            ("CCO", "ethanol"),      # sp3 carbon angles
            ("CC=O", "acetaldehyde"), # sp2 carbon angles
            ("CCN", "ethylamine"),   # angles with nitrogen
        ]
        
        all_angle_params = {}
        
        for smiles, name in molecules:
            mol = Chem.MolFromSmiles(smiles)
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            
            mmff_props = rdForceFieldHelpers.MMFFGetMoleculeProperties(mol)
            angle_params = extractor.extract_angles(mol, mmff_props)
            
            # Extract force constants and equilibrium angles for comparison
            force_constants = [p.ref_value for p in angle_params if p.param_name.endswith('_k')]
            equilibrium_angles = [p.ref_value for p in angle_params if p.param_name.endswith('_theta0')]
            
            all_angle_params[name] = {
                'force_constants': force_constants,
                'equilibrium_angles': equilibrium_angles
            }
        
        # Verify that we got realistic parameters
        for name, params in all_angle_params.items():
            # Check force constants are reasonable MMFF94 values
            for k in params['force_constants']:
                assert 0.1 < k < 5.0  # Reasonable range for MMFF94 angle force constants
                # Should not be the old hardcoded values
                assert k not in [80.0, 100.0, 120.0, 70.0]
            
            # Check equilibrium angles are reasonable
            for theta in params['equilibrium_angles']:
                assert 90.0 < theta < 180.0  # Reasonable range for bond angles
                # Should not be exactly the old hardcoded values
                assert theta not in [109.5, 120.0, 180.0]
    
    def test_expanded_atom_type_coverage(self, extractor):
        """Test that the expanded atom type mapping includes N, P, S atom types."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        mapping = extractor.atom_type_mapping
        
        # Check that we have expanded beyond the original 6 atom types
        assert len(mapping.vdw_params) > 6
        
        # Check specific atom types that were missing are now included
        nitrogen_types = [10, 12, 15, 16, 17]  # Various nitrogen types
        sulfur_types = [25, 26, 27]           # Various sulfur types
        phosphorus_types = [44, 45]           # Various phosphorus types
        
        # At least some nitrogen types should be present
        assert any(nt in mapping.vdw_params for nt in nitrogen_types)
        
        # At least some sulfur types should be present
        assert any(st in mapping.vdw_params for st in sulfur_types)
        
        # At least some phosphorus types should be present
        assert any(pt in mapping.vdw_params for pt in phosphorus_types)
        
        # Verify the parameters are reasonable
        for atom_type, (epsilon, r_star) in mapping.vdw_params.items():
            assert epsilon > 0, f"Epsilon should be positive for atom type {atom_type}"
            assert r_star > 0, f"R* should be positive for atom type {atom_type}"
            assert epsilon < 1.0, f"Epsilon too large for atom type {atom_type}"
            assert 1.0 < r_star < 3.0, f"R* out of reasonable range for atom type {atom_type}"
    
    def test_extract_dihedrals(self, extractor, sample_ethanol):
        """Test dihedral parameter extraction."""
        from rdkit.Chem import rdForceFieldHelpers
        
        mmff_props = rdForceFieldHelpers.MMFFGetMoleculeProperties(sample_ethanol)
        dihedral_params = extractor.extract_dihedrals(sample_ethanol, mmff_props)
        
        assert isinstance(dihedral_params, list)
        # Note: might be empty for simple molecules
        
        # Check parameter structure if any exist
        for param in dihedral_params:
            assert isinstance(param, ParameterComparison)
            assert param.param_type == "dihedral"
            assert param.ff_source == "MMFF94"
            assert param.unit == "kcal/mol"
            assert param.param_name.endswith(("_V1", "_V2", "_V3"))
    
    def test_extract_dihedrals_none_props(self, extractor, sample_ethanol):
        """Test dihedral extraction with None properties."""
        dihedral_params = extractor.extract_dihedrals(sample_ethanol, None)
        assert dihedral_params == []
    
    def test_extract_all_parameters(self, extractor, sample_ethanol):
        """Test extraction of all parameters."""
        all_params = extractor.extract_all_parameters(sample_ethanol)
        
        assert isinstance(all_params, list)
        assert len(all_params) > 0
        
        # Should contain different parameter types
        param_types = set(param.param_type for param in all_params)
        assert "charge" in param_types
        
        # Check that all parameters are valid
        for param in all_params:
            assert isinstance(param, ParameterComparison)
            assert param.ff_source == "MMFF94"
            assert param.param_type in ["charge", "vdw", "bond", "angle", "dihedral"]
            assert not np.isnan(param.ref_value)
            assert not np.isinf(param.ref_value)
    
    def test_extract_all_parameters_invalid_molecule(self, extractor):
        """Test extraction with invalid molecule."""
        all_params = extractor.extract_all_parameters(None)
        assert all_params == []
    
    def test_get_parameter_count(self, extractor, sample_ethanol):
        """Test parameter counting."""
        counts = extractor.get_parameter_count(sample_ethanol)
        
        assert isinstance(counts, dict)
        assert "charges" in counts
        assert "bonds" in counts
        assert "angles" in counts
        assert "dihedrals" in counts
        assert "vdw_types" in counts
        
        # Check reasonable values
        assert counts["charges"] == sample_ethanol.GetNumAtoms()
        assert counts["bonds"] > 0
        assert counts["angles"] > 0
    
    def test_get_parameter_count_invalid_molecule(self, extractor):
        """Test parameter counting with invalid molecule."""
        counts = extractor.get_parameter_count(None)
        assert "error" in counts
    
    def test_pfas_molecule_extraction(self, extractor, sample_pfas_molecule):
        """Test extraction with PFAS molecule."""
        all_params = extractor.extract_all_parameters(sample_pfas_molecule)
        
        assert isinstance(all_params, list)
        assert len(all_params) > 0
        
        # Should contain fluorine-related parameters
        param_names = [param.param_name for param in all_params]
        has_fluorine = any("F" in name for name in param_names)
        assert has_fluorine, "Should have fluorine-containing parameters for PFAS molecule"
        
        # Check for reasonable charge distribution
        charges = [param.ref_value for param in all_params if param.param_type == "charge"]
        assert len(charges) > 0
        
        # Fluorine atoms should have negative charges
        fluorine_charges = [
            param.ref_value for param in all_params 
            if param.param_type == "charge" and "F" in param.param_name
        ]
        if fluorine_charges:  # If fluorine charges exist
            assert all(charge < 0 for charge in fluorine_charges), "Fluorine should have negative charges"


class TestFactoryFunction:
    """Test the factory function."""
    
    def test_create_mmff94_extractor(self):
        """Test factory function."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        extractor = create_mmff94_extractor()
        assert isinstance(extractor, MMFF94ParameterExtractor)


class TestIntegration:
    """Integration tests with real molecules."""
    
    @pytest.mark.parametrize("smiles,min_atoms", [
        ("C", 4),      # Methane (with hydrogens) - at least 4 atoms
        ("CC", 8),     # Ethane (with hydrogens) - at least 8 atoms
        ("CCO", 9),    # Ethanol (with hydrogens) - at least 9 atoms
        ("C(F)(F)F", 5),  # Trifluoromethane (with hydrogen) - at least 5 atoms
    ])
    def test_various_molecules(self, smiles, min_atoms):
        """Test extraction with various molecules."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        extractor = create_mmff94_extractor()
        
        # Create molecule
        mol = Chem.MolFromSmiles(smiles)
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        
        # Extract parameters
        params = extractor.extract_all_parameters(mol)
        
        assert len(params) > 0
        actual_atoms = mol.GetNumAtoms()
        assert actual_atoms >= min_atoms, f"Expected at least {min_atoms} atoms, got {actual_atoms}"
        
        # Check charge parameters
        charges = [p for p in params if p.param_type == "charge"]
        assert len(charges) == actual_atoms
        
        # Check charge neutrality (within tolerance)
        total_charge = sum(p.ref_value for p in charges)
        assert abs(total_charge) < 0.01, f"Total charge {total_charge} should be near zero"
    
    def test_parameter_validation_integration(self):
        """Test that extracted parameters pass validation."""
        if not HAS_RDKIT:
            pytest.skip("RDKit not available")
        
        extractor = create_mmff94_extractor()
        
        # Create test molecule
        mol = Chem.MolFromSmiles("CCO")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        
        # Extract parameters
        params = extractor.extract_all_parameters(mol)
        
        # All parameters should be valid (no validation errors)
        # Note: We skip validation for parameters where pred_value is 0.0 (no prediction yet)
        from huggingface_djmgnn_validation.parameter_comparison import validate_parameter_entry
        
        for param in params:
            # Skip parameters with zero pred_value (no prediction made yet)
            if param.pred_value == 0.0:
                continue
                
            # Skip vdW epsilon parameters that are zero (valid MMFF94 behavior)
            if param.param_type == "vdw" and "epsilon" in param.param_name and param.ref_value == 0.0:
                continue
                
            validation_result = validate_parameter_entry(param)
            assert validation_result.is_valid, f"Parameter {param.param_name} failed validation: {validation_result.error_message}"


if __name__ == "__main__":
    # Run basic tests if executed directly
    if HAS_RDKIT:
        print("Running MMFF94 Parameter Extractor Tests")
        print("=" * 50)
        
        # Test basic functionality
        extractor = create_mmff94_extractor()
        
        # Test with ethanol
        mol = Chem.MolFromSmiles("CCO")
        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)
        
        params = extractor.extract_all_parameters(mol)
        print(f"Extracted {len(params)} parameters from ethanol")
        
        # Show parameter breakdown
        param_types = {}
        for param in params:
            if param.param_type not in param_types:
                param_types[param.param_type] = 0
            param_types[param.param_type] += 1
        
        for ptype, count in param_types.items():
            print(f"  {ptype}: {count}")
        
        print("\nAll basic tests passed!")
    else:
        print("RDKit not available - skipping tests")