import pytest
import shutil
from unittest.mock import patch, Mock
from pathlib import Path
import tempfile

from leanup.repo.manager import LeanRepo, RepoManager


class TestRepoManager:
    """Test cases for RepoManager class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_manager = RepoManager(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test RepoManager initialization"""
        assert self.repo_manager.cwd == Path(self.temp_dir).resolve()
        assert not self.repo_manager.is_gitrepo
    
    def test_read_write_file(self):
        """Test file read/write operations"""
        content = "test content"
        file_path = "test.txt"
        
        # Test write
        result = self.repo_manager.write_file(file_path, content)
        assert result is True
        
        # Test read
        read_content = self.repo_manager.read_file(file_path)
        assert read_content == content
    
    def test_edit_file(self):
        """Test file editing"""
        original_content = "Hello world"
        file_path = "test.txt"
        
        # Create file
        self.repo_manager.write_file(file_path, original_content)
        
        # Edit file
        result = self.repo_manager.edit_file(file_path, "world", "universe")
        assert result is True
        
        # Verify edit
        new_content = self.repo_manager.read_file(file_path)
        assert new_content == "Hello universe"
    
    def test_list_files_and_dirs(self):
        """Test listing files and directories"""
        # Create test files and directories
        (Path(self.temp_dir) / "file1.txt").write_text("content")
        (Path(self.temp_dir) / "file2.py").write_text("content")
        (Path(self.temp_dir) / "subdir").mkdir()
        
        # Test list files
        files = self.repo_manager.list_files()
        assert len(files) == 2
        
        # Test list files with pattern
        py_files = self.repo_manager.list_files("*.py")
        assert len(py_files) == 1
        assert py_files[0].name == "file2.py"
        
        # Test list directories
        dirs = self.repo_manager.list_dirs()
        assert len(dirs) == 1
        assert dirs[0].name == "subdir"


class TestLeanRepo:
    """Test cases for LeanRepo class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.lean_repo = LeanRepo(self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_lean_toolchain_exists(self):
        """Test reading lean-toolchain file when it exists"""
        toolchain_content = "leanprover/lean4:v4.3.0"
        toolchain_file = Path(self.temp_dir) / "lean-toolchain"
        toolchain_file.write_text(toolchain_content)
        
        result = self.lean_repo.get_lean_toolchain()
        assert result == toolchain_content
    
    def test_get_lean_toolchain_not_exists(self):
        """Test reading lean-toolchain file when it doesn't exist"""
        result = self.lean_repo.get_lean_toolchain()
        assert result is None
    
    def test_get_project_info(self):
        """Test getting project information"""
        # Create some files
        (Path(self.temp_dir) / "lean-toolchain").write_text("leanprover/lean4:v4.3.0")
        (Path(self.temp_dir) / "lakefile.toml").write_text("[package]\nname = 'test'")
        (Path(self.temp_dir) / ".lake").mkdir()
        
        info = self.lean_repo.get_project_info()
        
        assert info['lean_version'] == "leanprover/lean4:v4.3.0"
        assert info['has_lakefile_toml'] is True
        assert info['has_lakefile_lean'] is False
        assert info['build_dir_exists'] is True
        assert info['has_lake_manifest'] is False