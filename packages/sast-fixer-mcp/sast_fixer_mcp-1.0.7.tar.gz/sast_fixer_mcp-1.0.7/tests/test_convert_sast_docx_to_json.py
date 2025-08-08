import os
import json
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

# Import the function to test
from sast_fixer_mcp.server import convert_sast_docx_to_json

def test_convert_sast_docx_to_json_with_real_file():
    """
    Test convert_sast_docx_to_json function with the actual test file
    """
    # Path to the actual test file - using absolute path
    test_file_path = os.path.join(os.path.dirname(__file__), "sast_report_test.docx")
    
    # Verify the test file exists
    assert os.path.exists(test_file_path), f"Test file not found: {test_file_path}"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(temp_dir)
        # Copy the test file to the temporary directory
        temp_test_file = os.path.join(temp_dir, "sast_report_test.docx")
        shutil.copy(test_file_path, temp_test_file)
        
        # Run the conversion
        result = convert_sast_docx_to_json(temp_test_file, temp_dir)
        
        # Check that the function returns the expected success message
        assert "所有漏洞已保存到" in result
        assert ".scanissuefix" in result
        
        # Check that the output directory was created
        output_dir = os.path.join(temp_dir, ".scanissuefix")
        assert os.path.exists(output_dir)
        
        # Check that JSON files were created
        json_files = [f for f in os.listdir(output_dir) if f.endswith('_new.json')]
        # There should be at least one JSON file created
        assert len(json_files) >= 1
        
        # Check the content of one of the JSON files
        if json_files:
            with open(os.path.join(output_dir, json_files[0]), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check that the data has the expected structure
                assert "issue_title" in data
                assert "issue_level" in data
                assert "code_list" in data

# def test_parse_docx_to_json_with_real_file():
#     """
#     Test parse_docx_to_json function with the actual test file
#     """
#     # Path to the actual test file - using absolute path
#     test_file_path = os.path.join(os.path.dirname(__file__), "sast_report_test.docx")
    
#     # Verify the test file exists
#     assert os.path.exists(test_file_path), f"Test file not found: {test_file_path}"
    
#     with tempfile.TemporaryDirectory() as temp_dir:
#         # Copy the test file to the temporary directory
#         temp_test_file = os.path.join(temp_dir, "sast_report_test.docx")
#         shutil.copy(test_file_path, temp_test_file)
        
#         # Run the parsing
#         result = parse_docx_to_json(temp_test_file)
        
#         # Basic assertions
#         assert isinstance(result, list)
#         # Should have at least some content
#         assert len(result) >= 1
        
#         # Check that the result contains expected section titles
#         titles = [item["title"] for item in result]
#         # Most SAST reports should have these sections
#         assert any("漏洞" in title for title in titles)

# def test_transform_json_with_real_data():
#     """
#     Test transform_json function with data parsed from the real file
#     """
#     # Path to the actual test file - using absolute path
#     test_file_path = os.path.join(os.path.dirname(__file__), "sast_report_test.docx")
    
#     # Verify the test file exists
#     assert os.path.exists(test_file_path), f"Test file not found: {test_file_path}"
    
#     with tempfile.TemporaryDirectory() as temp_dir:
#         # Copy the test file to the temporary directory
#         temp_test_file = os.path.join(temp_dir, "sast_report_test.docx")
#         shutil.copy(test_file_path, temp_test_file)
        
#         # First parse the document
#         parsed_data = parse_docx_to_json(temp_test_file)
        
#         # Transform the data
#         transformed_data = transform_json(parsed_data)
        
#         # Should have at least the main sections
#         assert isinstance(transformed_data, dict)
        
#         # If there are vulnerability sections, check their structure
#         for section_name in transformed_data:
#             if "漏洞" in section_name and transformed_data[section_name]:
#                 # Check the first vulnerability entry
#                 first_issue = transformed_data[section_name][0]
#                 required_fields = ["issue_title", "issue_level", "issue_count", 
#                                  "issue_desc", "fix_advice", "code_list"]
#                 for field in required_fields:
#                     assert field in first_issue

# def test_convert_sast_docx_to_json_file_not_exists():
#     """
#     Test convert_sast_docx_to_json function when file does not exist
#     """
#     with tempfile.TemporaryDirectory() as temp_dir:
#         file_path = "non_existent_file.docx"
#         result = convert_sast_docx_to_json(file_path, temp_dir)
#         assert f"文件不存在: {os.path.join(temp_dir, file_path)}" in result
