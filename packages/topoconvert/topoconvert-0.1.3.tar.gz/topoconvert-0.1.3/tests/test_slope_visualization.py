"""Tests for slope visualization functions (matplotlib rendering)."""
import pytest
import tempfile
from pathlib import Path
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import matplotlib.pyplot as plt
from PIL import Image

from topoconvert.core.slope_heatmap import render_slope_heatmap


class TestRenderSlopeHeatmap:
    """Test cases for render_slope_heatmap function."""
    
    def create_mock_slope_data(self, grid_size=50):
        """Create mock slope data for testing."""
        # Create synthetic slope grid with known pattern
        x = np.linspace(0, 100, grid_size)
        y = np.linspace(0, 100, grid_size)
        xi, yi = np.meshgrid(x, y)
        
        # Create a simple slope pattern (inclined plane)
        slope_grid = np.ones_like(xi) * 15.0  # 15 degree uniform slope
        
        # Add some variation
        slope_grid += np.sin(xi / 10) * 5.0
        
        # Create matching elevation grid
        elevation_grid = xi * 0.268 * 100  # ~15 degree slope in feet
        
        return {
            'slope_grid': slope_grid,
            'elevation_grid': elevation_grid,
            'x_coords': x,
            'y_coords': y,
            'xi': x,
            'yi': y,
            'extent': [0, 100, 0, 100],
            'slope_stats': {
                'min': float(np.min(slope_grid)),
                'max': float(np.max(slope_grid)),
                'mean': float(np.mean(slope_grid)),
                'median': float(np.median(slope_grid))
            },
            'mask': np.ones_like(slope_grid, dtype=bool),
            'utm_zone': 10,
            'epsg_code': 32610
        }
    
    def test_basic_rendering(self):
        """Test basic rendering functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_render.png"
            slope_data = self.create_mock_slope_data()
            
            render_slope_heatmap(
                slope_data=slope_data,
                output_file=output_file,
                input_title="Test Slope"
            )
            
            # Verify output file created
            assert output_file.exists()
            
            # Verify it's a valid PNG
            with Image.open(str(output_file)) as img:
                assert img.format == 'PNG'
                assert img.size[0] > 0
                assert img.size[1] > 0
    
    def test_rendering_with_target_slope(self):
        """Test rendering with target slope colormap."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_target_slope.png"
            slope_data = self.create_mock_slope_data()
            
            render_slope_heatmap(
                slope_data=slope_data,
                output_file=output_file,
                target_slope=15.0,
                slope_units='degrees'
            )
            
            assert output_file.exists()
    
    def test_rendering_with_contours(self):
        """Test rendering with elevation contours."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_contours.png"
            slope_data = self.create_mock_slope_data()
            
            render_slope_heatmap(
                slope_data=slope_data,
                output_file=output_file,
                show_contours=True,
                contour_interval=10.0
            )
            
            assert output_file.exists()
    
    def test_different_stats_positions(self):
        """Test different statistics display positions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            slope_data = self.create_mock_slope_data()
            
            # Test each position option
            for position in ['inside', 'outside', 'none']:
                output_file = Path(temp_dir) / f"test_stats_{position}.png"
                
                render_slope_heatmap(
                    slope_data=slope_data,
                    output_file=output_file,
                    stats_position=position
                )
                
                assert output_file.exists()
    
    def test_different_slope_units(self):
        """Test rendering with different slope unit displays."""
        with tempfile.TemporaryDirectory() as temp_dir:
            slope_data = self.create_mock_slope_data()
            
            for units in ['degrees', 'percent', 'rise-run']:
                output_file = Path(temp_dir) / f"test_{units}.png"
                
                render_slope_heatmap(
                    slope_data=slope_data,
                    output_file=output_file,
                    slope_units=units,
                    run_length=12.0 if units == 'rise-run' else 10.0
                )
                
                assert output_file.exists()
    
    def test_custom_colormap(self):
        """Test rendering with different colormaps."""
        with tempfile.TemporaryDirectory() as temp_dir:
            slope_data = self.create_mock_slope_data()
            
            for cmap in ['viridis', 'plasma', 'RdYlGn_r']:
                output_file = Path(temp_dir) / f"test_{cmap}.png"
                
                render_slope_heatmap(
                    slope_data=slope_data,
                    output_file=output_file,
                    colormap=cmap
                )
                
                assert output_file.exists()
    
    def test_custom_dpi_and_figsize(self):
        """Test rendering with custom DPI and figure size."""
        with tempfile.TemporaryDirectory() as temp_dir:
            slope_data = self.create_mock_slope_data()
            
            output_file = Path(temp_dir) / "test_custom_size.png"
            
            render_slope_heatmap(
                slope_data=slope_data,
                output_file=output_file,
                dpi=300,
                figsize=[12, 10]
            )
            
            assert output_file.exists()
            
            # Check image has higher resolution
            with Image.open(str(output_file)) as img:
                assert img.size[0] > 1000  # Should be larger due to higher DPI
    
    def test_nan_handling_in_visualization(self):
        """Test that NaN values are handled properly in visualization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "test_nan_handling.png"
            slope_data = self.create_mock_slope_data()
            
            # Add some NaN values
            slope_data['slope_grid'][10:20, 10:20] = np.nan
            
            render_slope_heatmap(
                slope_data=slope_data,
                output_file=output_file
            )
            
            assert output_file.exists()
    
    def test_max_slope_clipping(self):
        """Test that max_slope parameter properly clips color scale."""
        with tempfile.TemporaryDirectory() as temp_dir:
            slope_data = self.create_mock_slope_data()
            
            # Add some high slope values
            slope_data['slope_grid'][5:10, 5:10] = 45.0
            
            output_file = Path(temp_dir) / "test_max_slope.png"
            
            render_slope_heatmap(
                slope_data=slope_data,
                output_file=output_file,
                max_slope=30.0  # Clip at 30 degrees
            )
            
            assert output_file.exists()


class TestVisualizationRobustness:
    """Test cases for visualization robustness improvements."""
    
    def test_sparse_data_warning(self):
        """Test that sparse data triggers appropriate warnings."""
        from topoconvert.core.slope_heatmap import compute_slope_from_points
        import warnings
        
        # Create very sparse data
        points = [
            (-122.0, 37.0, 100.0),
            (-122.01, 37.0, 110.0),  # Far apart
            (-122.0, 37.01, 120.0),
        ]
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = compute_slope_from_points(
                points=points,
                grid_resolution=100  # High resolution for sparse data
            )
            
            # Should have warned about sparse data
            assert len(w) > 0
            assert any("Sparse data detected" in str(warning.message) for warning in w)