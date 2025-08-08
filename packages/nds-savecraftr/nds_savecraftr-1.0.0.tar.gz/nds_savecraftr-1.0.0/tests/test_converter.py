#!/usr/bin/env python3

import pytest
import tempfile
import os
from pathlib import Path
from nds_savecraftr import convert_save, find_actual_data_end, smart_trim_size

class TestNDSSaveCraftr:
    """Test suite for NDS SaveCraftr"""
    
    def create_test_save(self, size_kb, data_end_kb=None):
        """Create a test save file with specified size and data end point"""
        if data_end_kb is None:
            data_end_kb = size_kb
            
        size = size_kb * 1024
        data_end = data_end_kb * 1024
        
        # Create test data
        data = bytearray(size)
        
        # Fill with non-zero data up to data_end
        for i in range(data_end):
            data[i] = (i % 255) + 1  # Non-zero pattern
            
        # Rest remains zeros (padding)
        
        # Create temporary file
        fd, path = tempfile.mkstemp(suffix='.sav')
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            
        return path
    
    def test_find_actual_data_end_full_data(self):
        """Test finding data end when file is full of data"""
        test_file = self.create_test_save(128, 128)
        try:
            result = find_actual_data_end(test_file)
            assert result == 128 * 1024
        finally:
            os.unlink(test_file)
    
    def test_find_actual_data_end_with_padding(self):
        """Test finding data end when file has trailing zeros"""
        test_file = self.create_test_save(512, 128)  # 128KB data, 512KB total
        try:
            result = find_actual_data_end(test_file)
            assert result == 128 * 1024
        finally:
            os.unlink(test_file)
    
    def test_expansion_mode(self):
        """Test auto-expansion for files < 512KB"""
        input_file = self.create_test_save(128)
        try:
            output_file = convert_save(input_file, verbose=False)
            try:
                # Check output size is 512KB
                assert Path(output_file).stat().st_size == 512 * 1024
                
                # Check data integrity
                with open(input_file, 'rb') as f1, open(output_file, 'rb') as f2:
                    original_data = f1.read()
                    converted_data = f2.read()
                    
                    # First 128KB should be identical
                    assert converted_data[:128*1024] == original_data
                    # Rest should be zeros
                    assert all(b == 0 for b in converted_data[128*1024:])
                    
            finally:
                os.unlink(output_file)
        finally:
            os.unlink(input_file)
    
    def test_trimming_mode(self):
        """Test auto-trimming for files = 512KB with padding"""
        input_file = self.create_test_save(512, 128)  # 128KB data + padding
        try:
            output_file = convert_save(input_file, verbose=False)
            try:
                # Check output size is trimmed to actual data
                assert Path(output_file).stat().st_size == 128 * 1024
                
                # Check data integrity
                with open(input_file, 'rb') as f1, open(output_file, 'rb') as f2:
                    original_data = f1.read()
                    converted_data = f2.read()
                    
                    # Converted should match first 128KB of original
                    assert converted_data == original_data[:128*1024]
                    
            finally:
                os.unlink(output_file)
        finally:
            os.unlink(input_file)
    
    def test_manual_mode(self):
        """Test manual size specification"""
        input_file = self.create_test_save(128)
        try:
            output_file = convert_save(input_file, target_size_kb=256, verbose=False)
            try:
                # Check output size is exactly 256KB
                assert Path(output_file).stat().st_size == 256 * 1024
            finally:
                os.unlink(output_file)
        finally:
            os.unlink(input_file)
    
    def test_smart_trim_rounding(self):
        """Test smart trimming rounds up when close to standard sizes"""
        # Test cases: (actual_end, expected_rounded)
        test_cases = [
            (127 * 1024, 128 * 1024),  # Close to 128KB -> round up
            (120 * 1024, 120 * 1024),  # Far from 128KB -> keep natural
            (255 * 1024, 256 * 1024),  # Close to 256KB -> round up  
            (200 * 1024, 200 * 1024),  # Far from any standard -> keep natural
            (63 * 1024, 64 * 1024),    # Close to 64KB -> round up
        ]
        
        for actual_end, expected in test_cases:
            result = smart_trim_size(actual_end)
            assert result == expected, f"Expected {expected}, got {result} for {actual_end}"
    
    def test_smart_trimming_integration(self):
        """Test smart trimming in full conversion pipeline"""
        # Create file with data that ends close to 128KB (should round up)
        input_file = self.create_test_save(512, 127)  # 127KB data + padding
        try:
            output_file = convert_save(input_file, verbose=False)
            try:
                # Should round up to exactly 128KB
                assert Path(output_file).stat().st_size == 128 * 1024
            finally:
                os.unlink(output_file)
        finally:
            os.unlink(input_file)
        """Test custom output file path"""
        input_file = self.create_test_save(64)
        custom_output = tempfile.mktemp(suffix='_custom.sav')
        
    def test_custom_output_path(self):
        """Test custom output file path"""
        input_file = self.create_test_save(64)
        custom_output = tempfile.mktemp(suffix='_custom.sav')
        
        try:
            output_file = convert_save(input_file, custom_output, verbose=False)
            assert output_file == custom_output
            assert Path(custom_output).exists()
        finally:
            os.unlink(input_file)
            if Path(custom_output).exists():
                os.unlink(custom_output)
    
    def test_nonexistent_file(self):
        """Test error handling for nonexistent input file"""
        with pytest.raises(FileNotFoundError):
            convert_save("nonexistent_file.sav")
    
    def test_mario_kart_ds_real_save(self):
        """Test with real Mario Kart DS save file"""
        # Path to the example Mario Kart DS save
        mario_kart_save = Path(__file__).parent.parent / "examples" / "mario_kart_ds_256kb.sav"
        
        if not mario_kart_save.exists():
            pytest.skip("Mario Kart DS example save not found")
        
        # Test expansion mode (256KB -> 512KB)
        output_file = convert_save(str(mario_kart_save), verbose=False)
        try:
            # Check that it was expanded to 512KB
            output_path = Path(output_file)
            assert output_path.stat().st_size == 512 * 1024
            
            # Check that original data is preserved at the beginning
            with open(mario_kart_save, 'rb') as f1, open(output_file, 'rb') as f2:
                original_data = f1.read()
                converted_data = f2.read()
                
                # First 256KB should be identical
                assert converted_data[:256*1024] == original_data
                # Rest should be zeros
                assert all(b == 0 for b in converted_data[256*1024:])
                
        finally:
            if Path(output_file).exists():
                os.unlink(output_file)
    
    def test_mario_kart_ds_data_integrity(self):
        """Test that Mario Kart DS save data integrity is preserved"""
        mario_kart_save = Path(__file__).parent.parent / "examples" / "mario_kart_ds_256kb.sav"
        
        if not mario_kart_save.exists():
            pytest.skip("Mario Kart DS example save not found")
        
        # Check actual data end detection
        actual_end = find_actual_data_end(str(mario_kart_save))
        
        # Mario Kart DS saves typically use most of their allocated space
        # Should be close to 256KB (within reasonable range)
        assert actual_end > 200 * 1024  # At least 200KB of actual data
        assert actual_end <= 256 * 1024  # But not more than 256KB

if __name__ == '__main__':
    pytest.main([__file__])