#!/usr/bin/env python3
"""
Test suite for PyFunc C++ backend.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyfunc import pipe, _
from pyfunc.backends import enable_cpp_backend, disable_cpp_backend, is_cpp_available

class TestCppBackend(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        # Always start with Python backend
        disable_cpp_backend()
    
    def tearDown(self):
        """Clean up after tests."""
        disable_cpp_backend()
    
    @unittest.skipUnless(is_cpp_available(), "C++ backend not available")
    def test_map_operations(self):
        """Test map operations with C++ backend."""
        data = list(range(1000))
        
        # Test with Python backend
        disable_cpp_backend()
        python_result = pipe(data).map(_ * 2).to_list()
        
        # Test with C++ backend
        enable_cpp_backend(threshold=100)
        cpp_result = pipe(data).map(_ * 2).to_list()
        
        self.assertEqual(python_result, cpp_result)
    
    @unittest.skipUnless(is_cpp_available(), "C++ backend not available")
    def test_filter_operations(self):
        """Test filter operations with C++ backend."""
        data = list(range(1000))
        
        # Test with Python backend
        disable_cpp_backend()
        python_result = pipe(data).filter(_ > 500).to_list()
        
        # Test with C++ backend
        enable_cpp_backend(threshold=100)
        cpp_result = pipe(data).filter(_ > 500).to_list()
        
        self.assertEqual(python_result, cpp_result)
    
    @unittest.skipUnless(is_cpp_available(), "C++ backend not available")
    def test_sum_operations(self):
        """Test sum operations with C++ backend."""
        data = list(range(1000))
        
        # Test with Python backend
        disable_cpp_backend()
        python_result = pipe(data).sum().get()
        
        # Test with C++ backend
        enable_cpp_backend(threshold=100)
        cpp_result = pipe(data).sum().get()
        
        self.assertEqual(python_result, cpp_result)
    
    @unittest.skipUnless(is_cpp_available(), "C++ backend not available")
    def test_combined_operations(self):
        """Test combined operations with C++ backend."""
        data = list(range(1000))
        
        # Test with Python backend
        disable_cpp_backend()
        python_result = pipe(data).map(_ * 2).filter(_ > 1000).sum().get()
        
        # Test with C++ backend
        enable_cpp_backend(threshold=100)
        cpp_result = pipe(data).map(_ * 2).filter(_ > 1000).sum().get()
        
        self.assertEqual(python_result, cpp_result)
    
    @unittest.skipUnless(is_cpp_available(), "C++ backend not available")
    def test_threshold_behavior(self):
        """Test that C++ backend respects size thresholds."""
        small_data = list(range(10))
        large_data = list(range(10000))
        
        enable_cpp_backend(threshold=1000)
        
        # Small data should use Python (we can't easily test this directly,
        # but we can verify it doesn't crash)
        small_result = pipe(small_data).map(_ * 2).to_list()
        self.assertEqual(len(small_result), 10)
        
        # Large data should use C++
        large_result = pipe(large_data).map(_ * 2).to_list()
        self.assertEqual(len(large_result), 10000)
    
    def test_fallback_behavior(self):
        """Test that operations fall back to Python when C++ is not available."""
        # This test should work regardless of C++ availability
        data = list(range(100))
        
        # Enable C++ backend (will fall back if not available)
        enable_cpp_backend(threshold=10)
        
        result = pipe(data).map(_ * 2).filter(_ > 100).sum().get()
        
        # Verify we get the expected result
        expected = sum(x * 2 for x in data if x * 2 > 100)
        self.assertEqual(result, expected)
    
    @unittest.skipUnless(is_cpp_available(), "C++ backend not available")
    def test_unsupported_operations(self):
        """Test that unsupported operations fall back to Python."""
        data = ["hello", "world", "test"]
        
        enable_cpp_backend(threshold=1)
        
        # String operations should fall back to Python
        result = pipe(data).map(_.upper()).to_list()
        expected = ["HELLO", "WORLD", "TEST"]
        self.assertEqual(result, expected)
    
    @unittest.skipUnless(is_cpp_available(), "C++ backend not available")
    def test_complex_placeholders(self):
        """Test that complex placeholders fall back to Python."""
        data = [{"value": i} for i in range(100)]
        
        enable_cpp_backend(threshold=10)
        
        # Dictionary access should fall back to Python
        result = pipe(data).map(_["value"]).filter(_ > 50).to_list()
        expected = list(range(51, 100))
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()