"""
Project scanner for file discovery and categorization.

This module handles scanning project directories, building directory trees,
and categorizing special files like configuration, documentation, and build files.
"""

import os
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from .models import FileInfo, ProjectScanResult, SpecialFiles
from .qualified_names import normalize_file_path
from code_index_mcp.constants import SUPPORTED_EXTENSIONS


class ProjectScanner:
    """Scans project directory and categorizes files."""
    
    # Use the centralized supported extensions list
    # Convert list to set for faster lookup
    _SUPPORTED_EXTENSIONS_SET = set(SUPPORTED_EXTENSIONS)
    
    # Special file patterns for categorization
    SPECIAL_FILE_PATTERNS = {
        'entry_points': [
            '__main__.py', 'main.py', 'app.py', 'server.py', 'run.py',
            'index.js', 'app.js', 'server.js', 'main.js',
            'Main.java', 'Application.java',
            'main.go', 'cmd/*.go',
            'main.c', 'main.cpp',
            'Program.cs', 'Main.cs'
        ],
        'config_files': [
            'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements*.txt',
            'package.json', 'package-lock.json', 'yarn.lock', 'tsconfig.json',
            'pom.xml', 'build.gradle', 'gradle.properties',
            'go.mod', 'go.sum',
            'Makefile', 'CMakeLists.txt',
            '*.csproj', '*.sln',
            'Gemfile', 'Gemfile.lock',
            'composer.json', 'composer.lock',
            'Cargo.toml', 'Cargo.lock',
            'build.sbt',
            'project.clj',
            'stack.yaml', 'cabal.project',
            'pubspec.yaml',
            'config.json', 'settings.json', '*.ini', '*.conf', '*.cfg'
        ],
        'documentation': [
            'README*', 'CHANGELOG*', 'HISTORY*', 'NEWS*',
            'LICENSE*', 'COPYING*', 'COPYRIGHT*',
            'CONTRIBUTING*', 'CODE_OF_CONDUCT*',
            'INSTALL*', 'USAGE*', 'EXAMPLES*',
            'docs/**/*', 'doc/**/*', 'documentation/**/*',
            '*.md', '*.rst', '*.txt', '*.adoc'
        ],
        'build_files': [
            'Dockerfile*', 'docker-compose*.yml', 'docker-compose*.yaml',
            '.dockerignore',
            'Jenkinsfile', '.github/**/*', '.gitlab-ci.yml',
            'azure-pipelines.yml', 'appveyor.yml',
            'tox.ini', 'noxfile.py',
            'webpack.config.js', 'rollup.config.js', 'vite.config.js',
            'gulpfile.js', 'Gruntfile.js',
            'build.xml', 'ant.xml'
        ],

    }
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.file_id_counter = 0
    
    def scan_project(self) -> ProjectScanResult:
        """
        Scan the project directory and return structured results.
        
        Returns:
            ProjectScanResult containing directory tree, file list, 
            special files, and project metadata.
        """
        # Discover all files
        all_files = self._discover_files()
        
        # Filter to supported files and assign IDs
        file_list = self._create_file_info_list(all_files)
        
        # Build directory tree
        directory_tree = self._build_directory_tree([f.path for f in file_list])
        
        # Categorize special files
        special_files = self._categorize_special_files(all_files)
        
        # Create project metadata
        project_metadata = self._create_project_metadata(file_list)
        
        return ProjectScanResult(
            directory_tree=directory_tree,
            file_list=file_list,
            special_files=special_files,
            project_metadata=project_metadata
        )
    
    def _discover_files(self) -> List[str]:
        """Discover all files in the project directory."""
        files = []
        
        for root, dirs, filenames in os.walk(self.base_path):
            # Skip common directories that shouldn't be indexed
            dirs[:] = [d for d in dirs if not self._should_skip_directory(d)]
            
            for filename in filenames:
                if not self._should_skip_file(filename):
                    file_path = os.path.join(root, filename)
                    # Convert to relative path from base_path
                    rel_path = os.path.relpath(file_path, self.base_path)
                    files.append(normalize_file_path(rel_path))  # Normalize path separators
        
        return files
    
    def _should_skip_directory(self, dirname: str) -> bool:
        """Check if directory should be skipped during scanning."""
        skip_dirs = {
            '__pycache__', '.pytest_cache', '.mypy_cache',
            'node_modules', '.npm', '.yarn',
            '.git', '.svn', '.hg',
            'build', 'dist', 'target', 'out',
            '.vscode', '.idea', '.vs',
            'venv', 'env', '.env', 'virtualenv',
            '.tox', '.nox',
            'coverage', '.coverage',
            'logs', 'log',
            'tmp', 'temp', '.tmp',
            '.DS_Store'
        }
        return dirname in skip_dirs or dirname.startswith('.')
    
    def _should_skip_file(self, filename: str) -> bool:
        """Check if file should be skipped during scanning."""
        # Skip hidden files and common non-code files
        if filename.startswith('.') and filename not in {'.gitignore', '.gitattributes'}:
            return True
        
        # Skip common binary and temporary files
        skip_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
            '.class', '.jar', '.war', '.ear',
            '.exe', '.bin', '.obj', '.o', '.a',
            '.log', '.tmp', '.temp', '.bak', '.swp',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.zip', '.tar', '.gz', '.rar', '.7z'
        }
        
        ext = Path(filename).suffix.lower()
        return ext in skip_extensions
    
    def _create_file_info_list(self, files: List[str]) -> List[FileInfo]:
        """Create FileInfo objects for supported files."""
        file_list = []
        
        for file_path in files:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                continue
            
            try:
                stat = full_path.stat()
                extension = full_path.suffix.lower()
                
                # Only include files with supported extensions
                if extension in self._SUPPORTED_EXTENSIONS_SET:
                    file_info = FileInfo(
                        id=self.file_id_counter,
                        path=file_path,
                        size=stat.st_size,
                        modified_time=datetime.fromtimestamp(stat.st_mtime),
                        extension=extension,
                        language=self._detect_language(extension)
                    )
                    file_list.append(file_info)
                    self.file_id_counter += 1
            
            except (OSError, PermissionError):
                # Skip files that can't be accessed
                continue
        
        return file_list
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python', '.pyw': 'python',
            '.js': 'javascript', '.jsx': 'javascript', 
            '.ts': 'typescript', '.tsx': 'typescript',
            '.mjs': 'javascript', '.cjs': 'javascript',
            '.java': 'java',
            '.go': 'go',
            '.c': 'c', '.h': 'c',
            '.cpp': 'cpp', '.cxx': 'cpp', '.cc': 'cpp', '.hpp': 'cpp',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin', '.kts': 'kotlin',
            '.rs': 'rust',
            '.scala': 'scala',
            '.clj': 'clojure', '.cljs': 'clojure',
            '.hs': 'haskell',
            '.ml': 'ocaml', '.mli': 'ocaml',
            '.fs': 'fsharp', '.fsx': 'fsharp',
            '.dart': 'dart',
            '.lua': 'lua',
            '.r': 'r', '.R': 'r',
            '.m': 'objective-c', '.mm': 'objective-c',
            '.pl': 'perl', '.pm': 'perl',
            '.sh': 'shell', '.bash': 'shell', '.zsh': 'shell',
            '.ps1': 'powershell',
            '.bat': 'batch', '.cmd': 'batch',
            '.sql': 'sql',
            '.json': 'json',
            '.yaml': 'yaml', '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'html', '.htm': 'html',
            '.css': 'css', '.scss': 'scss', '.sass': 'sass',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.txt': 'text'
        }
        return language_map.get(extension, 'unknown')
    
    def _build_directory_tree(self, files: List[str]) -> Dict[str, Any]:
        """Build nested directory structure."""
        tree = {}
        
        for file_path in files:
            parts = file_path.split('/')
            current = tree
            
            # Navigate/create directory structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file (leaf node)
            current[parts[-1]] = None
        
        return tree
    
    def _categorize_special_files(self, all_files: List[str]) -> Dict[str, List[str]]:
        """Categorize files into special types."""
        special_files = SpecialFiles()
        
        for file_path in all_files:
            filename = os.path.basename(file_path)
            
            # Check each category
            for category, patterns in self.SPECIAL_FILE_PATTERNS.items():
                if self._matches_patterns(file_path, patterns):
                    getattr(special_files, category).append(file_path)
        
        return {
            'entry_points': special_files.entry_points,
            'config_files': special_files.config_files,
            'documentation': special_files.documentation,
            'build_files': special_files.build_files
        }
    
    def _matches_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file matches any of the given patterns."""
        filename = os.path.basename(file_path)
        
        for pattern in patterns:
            # Handle glob patterns
            if '*' in pattern or '?' in pattern:
                if '/' in pattern:
                    # Path-based pattern
                    if glob.fnmatch.fnmatch(file_path, pattern):
                        return True
                else:
                    # Filename-based pattern
                    if glob.fnmatch.fnmatch(filename, pattern):
                        return True
            else:
                # Exact match
                if filename == pattern or file_path == pattern:
                    return True
        
        return False
    
    def _is_special_file(self, file_path: str) -> bool:
        """Check if file is a special file that should be included."""
        for patterns in self.SPECIAL_FILE_PATTERNS.values():
            if self._matches_patterns(file_path, patterns):
                return True
        return False
    
    def _create_project_metadata(self, file_list: List[FileInfo]) -> Dict[str, Any]:
        """Create project metadata from file list."""
        total_lines = 0
        
        # Calculate total lines for text files
        for file_info in file_list:
            if file_info.language in {'python', 'javascript', 'typescript', 'java', 'go', 'c', 'cpp'}:
                try:
                    full_path = self.base_path / file_info.path
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                except (OSError, UnicodeDecodeError):
                    pass
        
        return {
            'name': self.base_path.name,
            'root_path': str(self.base_path),
            'indexed_at': datetime.now(),
            'total_files': len(file_list),
            'total_lines': total_lines
        }