"""
Unit tests for parameter comparison schema and validation utilities.
"""

import pytest
import pandas as pd
import numpy as np
import warnings
from unittest.mock import patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from huggingface_djmgnn_validation.parameter_comparison import (
    ParameterComparison,
    ValidationResult,
    ChargeValidator,
    BondValidator,
    AngleValidator,
    DihedralValidator,
    VdWValidator,
    validate_parameter_entry,
    create_comparison_dataframe,
    add_parameter_comparison,
    get_parameter_statistics,
    validate_molecular_charges,
    VALIDATORS
)


class TestParameterComparison:
    """Test the ParameterComparison dataclass."""
    
    def test_parameter_creation_valid(self):
        """Test creating a valid parameter comparison."""
        param = ParameterComparison(
            mol_id="mol_001",
            param_type="charge",
            param_name="C1",
            ref_value=-0.123,
            pred_value=-0.145,
            unit="elementary_charge",
            ff_source="GAFF2"
        )
        
        assert param.mol_id == "mol_001"
        assert param.param_type == "charge"
        assert param.param_name == "C1"
        assert param.ref_value == -0.123
        assert param.pred_value == -0.145
        assert param.unit == "elementary_charge"
        assert param.ff_source == "GAFF2"
    
    def test_parameter_creation_with_validation_warning(self):
        """Test creating a parameter that generates a validation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            param = ParameterComparison(
                mol_id="mol_001",
                param_type="charge",
                param_name="C1",
                ref_value=5.0,  # Unreasonably high charge
                pred_value=-0.145,
                unit="elementary_charge",
                ff_source="GAFF2"
            )
            
            assert len(w) == 1
            assert "outside typical range" in str(w[0].message)


class TestValidationResult:
    """Test the ValidationResult dataclass."""
    
    def test_validation_result_valid(self):
        """Test creating a valid ValidationResult."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.error_message is None
        assert result.warnings == []
    
    def test_validation_result_invalid(self):
        """Test creating an invalid ValidationResult."""
        result = ValidationResult(
            is_valid=False,
            error_message="Test error",
            warnings=["Test warning"]
        )
        assert result.is_valid is False
        assert result.error_message == "Test error"
        assert result.warnings == ["Test warning"]


class TestChargeValidator:
    """Test the ChargeValidator class."""
    
    def setUp(self):
        self.validator = ChargeValidator()
    
    def test_valid_charge(self):
        """Test validation of a valid charge parameter."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="charge", param_name="C1",
            ref_value=-0.123, pred_value=-0.145, 
            unit="elementary_charge", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_invalid_charge_unit(self):
        """Test validation with invalid charge unit."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="charge", param_name="C1",
            ref_value=-0.123, pred_value=-0.145, 
            unit="invalid_unit", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is False
        assert "Invalid charge unit" in result.error_message
    
    def test_charge_out_of_range_warning(self):
        """Test validation with charges outside typical range."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="charge", param_name="C1",
            ref_value=5.0, pred_value=-4.0,  # Outside typical range
            unit="elementary_charge", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert len(result.warnings) == 2
        assert "outside typical range" in result.warnings[0]
        assert "outside typical range" in result.warnings[1]


class TestBondValidator:
    """Test the BondValidator class."""
    
    def setUp(self):
        self.validator = BondValidator()
    
    def test_valid_bond_length(self):
        """Test validation of a valid bond length parameter."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="bond", param_name="C1-C2",
            ref_value=1.54, pred_value=1.52, 
            unit="A", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_bond_force_constant(self):
        """Test validation of a valid bond force constant."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="bond", param_name="C1-C2",
            ref_value=300.0, pred_value=320.0, 
            unit="kcal/mol/A^2", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_invalid_bond_unit(self):
        """Test validation with invalid bond unit."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="bond", param_name="C1-C2",
            ref_value=1.54, pred_value=1.52, 
            unit="invalid_unit", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is False
        assert "Invalid bond unit" in result.error_message
    
    def test_negative_force_constant(self):
        """Test validation with negative force constant."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="bond", param_name="C1-C2",
            ref_value=-300.0, pred_value=320.0, 
            unit="kcal/mol/A^2", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is False
        assert "must be positive" in result.error_message
    
    def test_bond_length_out_of_range_warning(self):
        """Test validation with bond length outside typical range."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="bond", param_name="C1-C2",
            ref_value=10.0, pred_value=0.1,  # Outside typical range
            unit="A", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert len(result.warnings) == 2
        assert "outside typical range" in result.warnings[0]
        assert "outside typical range" in result.warnings[1]


class TestAngleValidator:
    """Test the AngleValidator class."""
    
    def setUp(self):
        self.validator = AngleValidator()
    
    def test_valid_angle_degrees(self):
        """Test validation of a valid angle in degrees."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="angle", param_name="C1-C2-C3",
            ref_value=109.5, pred_value=111.2, 
            unit="degrees", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_angle_force_constant(self):
        """Test validation of a valid angle force constant."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="angle", param_name="C1-C2-C3",
            ref_value=50.0, pred_value=55.0, 
            unit="kcal/mol/rad^2", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_invalid_angle_unit(self):
        """Test validation with invalid angle unit."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="angle", param_name="C1-C2-C3",
            ref_value=109.5, pred_value=111.2, 
            unit="invalid_unit", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is False
        assert "Invalid angle unit" in result.error_message
    
    def test_angle_out_of_range_warning(self):
        """Test validation with angle outside valid range."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="angle", param_name="C1-C2-C3",
            ref_value=200.0, pred_value=-10.0,  # Outside valid range
            unit="degrees", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert len(result.warnings) == 2
        assert "outside valid range" in result.warnings[0]
        assert "outside valid range" in result.warnings[1]


class TestDihedralValidator:
    """Test the DihedralValidator class."""
    
    def setUp(self):
        self.validator = DihedralValidator()
    
    def test_valid_dihedral_force_constant(self):
        """Test validation of a valid dihedral force constant."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="dihedral", param_name="C1-C2-C3-C4",
            ref_value=1.5, pred_value=1.8, 
            unit="kcal/mol", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_dihedral_phase(self):
        """Test validation of a valid dihedral phase."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="dihedral", param_name="C1-C2-C3-C4_phase",
            ref_value=180.0, pred_value=170.0, 
            unit="degrees", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_invalid_dihedral_unit(self):
        """Test validation with invalid dihedral unit."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="dihedral", param_name="C1-C2-C3-C4",
            ref_value=1.5, pred_value=1.8, 
            unit="invalid_unit", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is False
        assert "Invalid dihedral unit" in result.error_message
    
    def test_periodicity_out_of_range_warning(self):
        """Test validation with periodicity outside typical range."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="dihedral", param_name="C1-C2-C3-C4_n",
            ref_value=8.0, pred_value=0.0,  # Outside typical range
            unit="dimensionless", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert len(result.warnings) == 2
        assert "outside typical range" in result.warnings[0]
        assert "outside typical range" in result.warnings[1]


class TestVdWValidator:
    """Test the VdWValidator class."""
    
    def setUp(self):
        self.validator = VdWValidator()
    
    def test_valid_vdw_epsilon(self):
        """Test validation of a valid vdW epsilon parameter."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="vdw", param_name="C1_epsilon",
            ref_value=0.1, pred_value=0.12, 
            unit="kcal/mol", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_valid_vdw_sigma(self):
        """Test validation of a valid vdW sigma parameter."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="vdw", param_name="C1_sigma",
            ref_value=3.4, pred_value=3.5, 
            unit="A", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_invalid_vdw_unit(self):
        """Test validation with invalid vdW unit."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="vdw", param_name="C1_epsilon",
            ref_value=0.1, pred_value=0.12, 
            unit="invalid_unit", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is False
        assert "Invalid vdW unit" in result.error_message
    
    def test_negative_vdw_parameter(self):
        """Test validation with negative vdW parameter."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="vdw", param_name="C1_epsilon",
            ref_value=-0.1, pred_value=0.12, 
            unit="kcal/mol", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is False
        assert "must be positive" in result.error_message
    
    def test_vdw_out_of_range_warning(self):
        """Test validation with vdW parameters outside typical range."""
        self.setUp()
        param = ParameterComparison(
            mol_id="mol_001", param_type="vdw", param_name="C1_sigma",
            ref_value=20.0, pred_value=0.1,  # Outside typical range
            unit="A", ff_source="GAFF2"
        )
        
        result = self.validator.validate(param)
        assert result.is_valid is True
        assert len(result.warnings) == 2
        assert "outside typical range" in result.warnings[0]
        assert "outside typical range" in result.warnings[1]


class TestValidateParameterEntry:
    """Test the validate_parameter_entry function."""
    
    def test_valid_parameter_entry(self):
        """Test validation of a valid parameter entry."""
        param = ParameterComparison(
            mol_id="mol_001", param_type="charge", param_name="C1",
            ref_value=-0.123, pred_value=-0.145, 
            unit="elementary_charge", ff_source="GAFF2"
        )
        
        result = validate_parameter_entry(param)
        assert result.is_valid is True
        assert result.error_message is None
    
    def test_unknown_parameter_type(self):
        """Test validation with unknown parameter type."""
        param = ParameterComparison(
            mol_id="mol_001", param_type="unknown_type", param_name="C1",
            ref_value=-0.123, pred_value=-0.145, 
            unit="elementary_charge", ff_source="GAFF2"
        )
        
        result = validate_parameter_entry(param)
        assert result.is_valid is False
        assert "Unknown parameter type" in result.error_message
    
    def test_validators_registry(self):
        """Test that all expected validators are in the registry."""
        expected_types = ["charge", "bond", "angle", "dihedral", "vdw"]
        for param_type in expected_types:
            assert param_type in VALIDATORS


class TestDataFrameOperations:
    """Test DataFrame operations."""
    
    def test_create_comparison_dataframe(self):
        """Test creating an empty comparison DataFrame."""
        df = create_comparison_dataframe()
        
        expected_columns = [
            "mol_id", "param_type", "param_name", "ref_value", 
            "pred_value", "unit", "ff_source"
        ]
        
        assert list(df.columns) == expected_columns
        assert len(df) == 0
        assert df["mol_id"].dtype == "string"
        assert df["param_type"].dtype == "string"
        assert df["param_name"].dtype == "string"
        assert df["ref_value"].dtype == "float64"
        assert df["pred_value"].dtype == "float64"
        assert df["unit"].dtype == "string"
        assert df["ff_source"].dtype == "string"
    
    def test_add_parameter_comparison_with_object(self):
        """Test adding a parameter comparison using ParameterComparison object."""
        df = create_comparison_dataframe()
        
        param = ParameterComparison(
            mol_id="mol_001", param_type="charge", param_name="C1",
            ref_value=-0.123, pred_value=-0.145, 
            unit="elementary_charge", ff_source="GAFF2"
        )
        
        df = add_parameter_comparison(df, param)
        
        assert len(df) == 1
        assert df.iloc[0]["mol_id"] == "mol_001"
        assert df.iloc[0]["param_type"] == "charge"
        assert df.iloc[0]["param_name"] == "C1"
        assert df.iloc[0]["ref_value"] == -0.123
        assert df.iloc[0]["pred_value"] == -0.145
        assert df.iloc[0]["unit"] == "elementary_charge"
        assert df.iloc[0]["ff_source"] == "GAFF2"
    
    def test_add_parameter_comparison_with_dict(self):
        """Test adding a parameter comparison using dictionary."""
        df = create_comparison_dataframe()
        
        param_dict = {
            "mol_id": "mol_001",
            "param_type": "charge", 
            "param_name": "C1",
            "ref_value": -0.123,
            "pred_value": -0.145,
            "unit": "elementary_charge",
            "ff_source": "GAFF2"
        }
        
        df = add_parameter_comparison(df, param_dict)
        
        assert len(df) == 1
        assert df.iloc[0]["mol_id"] == "mol_001"
    
    def test_add_parameter_comparison_invalid(self):
        """Test adding an invalid parameter comparison."""
        df = create_comparison_dataframe()
        
        param = ParameterComparison(
            mol_id="mol_001", param_type="unknown_type", param_name="C1",
            ref_value=-0.123, pred_value=-0.145, 
            unit="elementary_charge", ff_source="GAFF2"
        )
        
        with pytest.raises(ValueError, match="Parameter validation failed"):
            add_parameter_comparison(df, param)


class TestStatistics:
    """Test statistical calculations."""
    
    def setUp(self):
        """Set up test DataFrame with sample data."""
        self.df = create_comparison_dataframe()
        
        # Add sample data
        samples = [
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "C1", 
             "ref_value": -0.1, "pred_value": -0.12, "unit": "elementary_charge", "ff_source": "GAFF2"},
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "C2", 
             "ref_value": 0.1, "pred_value": 0.08, "unit": "elementary_charge", "ff_source": "GAFF2"},
            {"mol_id": "mol_002", "param_type": "bond", "param_name": "C1-C2", 
             "ref_value": 1.54, "pred_value": 1.52, "unit": "A", "ff_source": "GAFF2"},
            {"mol_id": "mol_002", "param_type": "bond", "param_name": "C2-C3", 
             "ref_value": 1.50, "pred_value": 1.48, "unit": "A", "ff_source": "MMFF94"},
        ]
        
        for sample in samples:
            self.df = add_parameter_comparison(self.df, sample)
    
    def test_get_parameter_statistics_overall(self):
        """Test calculating overall statistics."""
        self.setUp()
        stats = get_parameter_statistics(self.df)
        
        assert stats["count"] == 4
        assert stats["mae"] == pytest.approx(0.02, abs=1e-6)
        assert stats["rmse"] == pytest.approx(0.02, abs=1e-6)
        assert "r_squared" in stats
        assert "mean_ref" in stats
        assert "mean_pred" in stats
        assert "std_ref" in stats
        assert "std_pred" in stats
    
    def test_get_parameter_statistics_by_type(self):
        """Test calculating statistics filtered by parameter type."""
        self.setUp()
        charge_stats = get_parameter_statistics(self.df, param_type="charge")
        
        assert charge_stats["count"] == 2
        assert charge_stats["mae"] == pytest.approx(0.02, abs=1e-6)
        
        bond_stats = get_parameter_statistics(self.df, param_type="bond")
        assert bond_stats["count"] == 2
        assert bond_stats["mae"] == pytest.approx(0.02, abs=1e-6)
    
    def test_get_parameter_statistics_by_ff_source(self):
        """Test calculating statistics filtered by force field source."""
        self.setUp()
        gaff2_stats = get_parameter_statistics(self.df, ff_source="GAFF2")
        
        assert gaff2_stats["count"] == 3
        
        mmff94_stats = get_parameter_statistics(self.df, ff_source="MMFF94")
        assert mmff94_stats["count"] == 1
    
    def test_get_parameter_statistics_empty(self):
        """Test calculating statistics for empty dataset."""
        stats = get_parameter_statistics(create_comparison_dataframe())
        
        assert stats["count"] == 0
        assert np.isnan(stats["mae"])
        assert np.isnan(stats["rmse"])
        assert np.isnan(stats["r_squared"])
    
    def test_get_parameter_statistics_no_matches(self):
        """Test calculating statistics when no data matches filters."""
        self.setUp()
        stats = get_parameter_statistics(self.df, param_type="nonexistent_type")
        
        assert stats["count"] == 0
        assert np.isnan(stats["mae"])


class TestMolecularChargeValidation:
    """Test molecular charge validation."""
    
    def setUp(self):
        """Set up test DataFrame with charge data."""
        self.df = create_comparison_dataframe()
        
        # Add charges for molecule with net charge 0
        charges_mol1 = [
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "C1", 
             "ref_value": -0.1, "pred_value": -0.12, "unit": "elementary_charge", "ff_source": "GAFF2"},
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "H1", 
             "ref_value": 0.1, "pred_value": 0.12, "unit": "elementary_charge", "ff_source": "GAFF2"},
        ]
        
        # Add charges for molecule with net charge +1
        charges_mol2 = [
            {"mol_id": "mol_002", "param_type": "charge", "param_name": "N1", 
             "ref_value": 0.5, "pred_value": 0.48, "unit": "elementary_charge", "ff_source": "GAFF2"},
            {"mol_id": "mol_002", "param_type": "charge", "param_name": "H1", 
             "ref_value": 0.5, "pred_value": 0.52, "unit": "elementary_charge", "ff_source": "GAFF2"},
        ]
        
        for charge in charges_mol1 + charges_mol2:
            self.df = add_parameter_comparison(self.df, charge)
    
    def test_validate_molecular_charges_valid(self):
        """Test validation of valid molecular charges."""
        self.setUp()
        results = validate_molecular_charges(self.df)
        
        assert "mol_001" in results
        assert "mol_002" in results
        assert len(results["mol_001"]) == 0  # No issues for neutral molecule
        assert len(results["mol_002"]) == 0  # No issues for +1 charged molecule
    
    def test_validate_molecular_charges_mismatch(self):
        """Test validation with charge sum mismatch."""
        df = create_comparison_dataframe()
        
        # Add charges that don't sum consistently
        charges = [
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "C1", 
             "ref_value": -0.1, "pred_value": -0.5, "unit": "elementary_charge", "ff_source": "GAFF2"},
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "H1", 
             "ref_value": 0.1, "pred_value": 0.3, "unit": "elementary_charge", "ff_source": "GAFF2"},
        ]
        
        for charge in charges:
            df = add_parameter_comparison(df, charge)
        
        results = validate_molecular_charges(df)
        
        assert "mol_001" in results
        assert len(results["mol_001"]) > 0
        assert any("mismatch" in issue for issue in results["mol_001"])
    
    def test_validate_molecular_charges_non_integer_sum(self):
        """Test validation with non-integer charge sum."""
        df = create_comparison_dataframe()
        
        # Add charges that sum to non-integer
        charges = [
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "C1", 
             "ref_value": -0.15, "pred_value": -0.15, "unit": "elementary_charge", "ff_source": "GAFF2"},
            {"mol_id": "mol_001", "param_type": "charge", "param_name": "H1", 
             "ref_value": 0.1, "pred_value": 0.1, "unit": "elementary_charge", "ff_source": "GAFF2"},
        ]
        
        for charge in charges:
            df = add_parameter_comparison(df, charge)
        
        results = validate_molecular_charges(df, tolerance=1e-3)
        
        assert "mol_001" in results
        assert len(results["mol_001"]) > 0
        assert any("not close to integer" in issue for issue in results["mol_001"])
    
    def test_validate_molecular_charges_empty(self):
        """Test validation with no charge data."""
        df = create_comparison_dataframe()
        results = validate_molecular_charges(df)
        assert results == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])