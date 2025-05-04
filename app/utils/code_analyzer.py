import re
import logging
from typing import Dict, List, Any, Optional, Tuple

class CodeAnalyzer:
    """Analyze code snippets for structure, issues, and patterns"""
    
    def __init__(self):
        # Language patterns for detection
        self.language_patterns = {
            "python": {
                "extensions": [".py", ".pyx", ".pyw"],
                "keywords": ["def ", "class ", "import ", "from ", "if ", "for ", "while ", "try:", "except:", "with "],
                "comment": "#"
            },
            "javascript": {
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "keywords": ["function", "const ", "let ", "var ", "import ", "export ", "class ", "=>", "if(", "for("],
                "comment": "//"
            },
            "java": {
                "extensions": [".java"],
                "keywords": ["public ", "private ", "class ", "void ", "static ", "import ", "extends ", "implements "],
                "comment": "//"
            },
            "c": {
                "extensions": [".c", ".h"],
                "keywords": ["int ", "void ", "struct ", "char ", "return ", "include ", "define ", "typedef "],
                "comment": "//"
            },
            "cpp": {
                "extensions": [".cpp", ".hpp", ".cc", ".hh"],
                "keywords": ["class ", "namespace ", "template ", "std::", "cout ", "cin ", "vector<"],
                "comment": "//"
            },
            "csharp": {
                "extensions": [".cs"],
                "keywords": ["using ", "namespace ", "class ", "public ", "private ", "void ", "static "],
                "comment": "//"
            },
            "ruby": {
                "extensions": [".rb"],
                "keywords": ["def ", "class ", "module ", "require ", "include ", "attr_", "end"],
                "comment": "#"
            },
            "go": {
                "extensions": [".go"],
                "keywords": ["func ", "package ", "import ", "type ", "struct ", "interface ", "go "],
                "comment": "//"
            },
            "php": {
                "extensions": [".php"],
                "keywords": ["<?php", "function ", "class ", "public ", "private ", "echo ", "$"],
                "comment": "//"
            },
            "swift": {
                "extensions": [".swift"],
                "keywords": ["func ", "class ", "struct ", "var ", "let ", "guard ", "import "],
                "comment": "//"
            },
            "rust": {
                "extensions": [".rs"],
                "keywords": ["fn ", "struct ", "impl ", "pub ", "let ", "mut ", "use ", "mod "],
                "comment": "//"
            },
            "kotlin": {
                "extensions": [".kt"],
                "keywords": ["fun ", "class ", "val ", "var ", "import ", "package ", "override "],
                "comment": "//"
            },
            "html": {
                "extensions": [".html", ".htm"],
                "keywords": ["<!DOCTYPE", "<html", "<head", "<body", "<div", "<span", "<a ", "<img "],
                "comment": "<!--"
            },
            "css": {
                "extensions": [".css"],
                "keywords": ["{", "}", "margin:", "padding:", "color:", "@media", "display:"],
                "comment": "/*"
            },
            "sql": {
                "extensions": [".sql"],
                "keywords": ["SELECT ", "FROM ", "WHERE ", "INSERT ", "UPDATE ", "DELETE ", "CREATE TABLE"],
                "comment": "--"
            },
            "bash": {
                "extensions": [".sh", ".bash"],
                "keywords": ["#!/bin/", "function ", "if [", "for ", "while ", "echo ", "export "],
                "comment": "#"
            },
            "powershell": {
                "extensions": [".ps1"],
                "keywords": ["function ", "param(", "$", "if(", "foreach(", "Write-Host"],
                "comment": "#"
            },
            "yaml": {
                "extensions": [".yml", ".yaml"],
                "keywords": ["---", "name:", "version:", "services:", "environment:"],
                "comment": "#"
            },
            "json": {
                "extensions": [".json"],
                "keywords": ["{", "}", "\":", "[", "]"],
                "comment": null
            },
            "dockerfile": {
                "extensions": ["Dockerfile"],
                "keywords": ["FROM ", "RUN ", "CMD ", "ENTRYPOINT ", "COPY ", "ADD ", "ENV "],
                "comment": "#"
            }
        }
    
    def detect_language(self, code_content: str) -> str:
        """
        Detect the programming language of the code snippet
        
        Args:
            code_content: The code to analyze
            
        Returns:
            Detected language name
        """
        # Check for language indicators in the first line (e.g., shebang)
        first_line = code_content.split('\n')[0] if code_content else ""
        
        if first_line.startswith("#!/bin/bash") or first_line.startswith("#!/bin/sh"):
            return "bash"
        elif first_line.startswith("#!/usr/bin/env python"):
            return "python"
        elif first_line.startswith("#!/usr/bin/env node"):
            return "javascript"
        elif first_line.startswith("<?php"):
            return "php"
        
        # Count keyword occurrences for each language
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            for keyword in patterns["keywords"]:
                score += code_content.count(keyword) * 2  # Weight keywords more heavily
            
            # Check for language-specific patterns
            if lang == "python" and "def " in code_content and ":" in code_content:
                score += 5
            elif lang == "javascript" and ("function" in code_content or "=>" in code_content) and ";" in code_content:
                score += 5
            elif lang == "html" and code_content.strip().startswith("<") and ">" in code_content:
                score += 5
            elif lang == "java" and "public class" in code_content and ";" in code_content:
                score += 5
            
            language_scores[lang] = score
        
        # Get the language with the highest score
        if language_scores:
            max_lang = max(language_scores.items(), key=lambda x: x[1])
            if max_lang[1] > 0:
                return max_lang[0]
        
        # Default if no clear match
        return "unknown"
    
    def parse_code(self, code_content: str, language: str) -> Dict[str, Any]:
        """
        Parse code to extract structure and key elements
        
        Args:
            code_content: The code to analyze
            language: Detected programming language
            
        Returns:
            Dictionary with parsed code information
        """
        result = {
            "language": language,
            "line_count": code_content.count('\n') + 1,
            "functions": [],
            "classes": [],
            "imports": [],
            "variables": [],
            "comments": [],
            "potential_issues": []
        }
        
        # Skip detailed parsing for unknown language
        if language == "unknown":
            return result
        
        # Get language-specific patterns
        patterns = self.language_patterns.get(language, {})
        comment_marker = patterns.get("comment")
        
        # Process line by line
        lines = code_content.split('\n')
        for i, line in enumerate(lines):
            line_num = i + 1
            stripped_line = line.strip()
            
            # Skip empty lines
            if not stripped_line:
                continue
            
            # Check for comments
            if comment_marker and stripped_line.startswith(comment_marker):
                result["comments"].append({
                    "line": line_num,
                    "text": stripped_line
                })
                continue
            
            # Parse based on language
            if language == "python":
                self._parse_python(stripped_line, line_num, result)
            elif language in ["javascript", "typescript"]:
                self._parse_javascript(stripped_line, line_num, result)
            elif language == "java":
                self._parse_java(stripped_line, line_num, result)
            elif language in ["c", "cpp"]:
                self._parse_c_cpp(stripped_line, line_num, result)
            elif language == "go":
                self._parse_go(stripped_line, line_num, result)
            # Add more language parsers as needed
        
        # Check for potential issues
        self._check_for_issues(code_content, language, result)
        
        return result
    
    def _parse_python(self, line: str, line_num: int, result: Dict[str, Any]):
        """Parse Python code line"""
        # Check for function definitions
        if line.startswith("def "):
            func_match = re.match(r"def\s+([a-zA-Z0-9_]+)\s*\((.*)\):", line)
            if func_match:
                result["functions"].append({
                    "name": func_match.group(1),
                    "params": func_match.group(2),
                    "line": line_num
                })
        
        # Check for class definitions
        elif line.startswith("class "):
            class_match = re.match(r"class\s+([a-zA-Z0-9_]+)(?:\((.*)\))?:", line)
            if class_match:
                result["classes"].append({
                    "name": class_match.group(1),
                    "inherits": class_match.group(2) if class_match.group(2) else "",
                    "line": line_num
                })
        
        # Check for imports
        elif line.startswith("import ") or line.startswith("from "):
            result["imports"].append({
                "statement": line,
                "line": line_num
            })
        
        # Check for variable assignments
        elif "=" in line and not line.startswith(("if ", "elif ", "while ")):
            var_match = re.match(r"([a-zA-Z0-9_]+)\s*=", line)
            if var_match:
                result["variables"].append({
                    "name": var_match.group(1),
                    "line": line_num,
                    "value": line.split("=", 1)[1].strip()
                })
    
    def _parse_javascript(self, line: str, line_num: int, result: Dict[str, Any]):
        """Parse JavaScript/TypeScript code line"""
        # Check for function definitions
        if "function " in line:
            func_match = re.search(r"function\s+([a-zA-Z0-9_$]+)\s*\((.*)\)", line)
            if func_match:
                result["functions"].append({
                    "name": func_match.group(1),
                    "params": func_match.group(2),
                    "line": line_num
                })
        
        # Check for arrow functions with names
        elif "=>" in line and "=" in line:
            func_match = re.search(r"(const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:\((.*)\)|([a-zA-Z0-9_$]+))\s*=>", line)
            if func_match:
                result["functions"].append({
                    "name": func_match.group(2),
                    "params": func_match.group(3) if func_match.group(3) else func_match.group(4) or "",
                    "line": line_num,
                    "type": "arrow"
                })
        
        # Check for class definitions
        elif line.startswith("class "):
            class_match = re.match(r"class\s+([a-zA-Z0-9_$]+)(?:\s+extends\s+([a-zA-Z0-9_$.]+))?", line)
            if class_match:
                result["classes"].append({
                    "name": class_match.group(1),
                    "inherits": class_match.group(2) if class_match.group(2) else "",
                    "line": line_num
                })
        
        # Check for imports
        elif line.startswith("import "):
            result["imports"].append({
                "statement": line,
                "line": line_num
            })
        
        # Check for variable declarations
        elif any(x in line for x in ["const ", "let ", "var "]):
            var_match = re.match(r"(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=", line)
            if var_match:
                result["variables"].append({
                    "name": var_match.group(1),
                    "line": line_num,
                    "value": line.split("=", 1)[1].strip().rstrip(";")
                })
    
    def _parse_java(self, line: str, line_num: int, result: Dict[str, Any]):
        """Parse Java code line"""
        # Check for method definitions
        method_match = re.search(r"(?:public|private|protected)?\s+(?:static\s+)?(?:[a-zA-Z0-9_<>]+)\s+([a-zA-Z0-9_]+)\s*\((.*)\)", line)
        if method_match and not line.endsWith(";"):
            result["functions"].append({
                "name": method_match.group(1),
                "params": method_match.group(2),
                "line": line_num
            })
        
        # Check for class definitions
        elif "class " in line:
            class_match = re.search(r"(?:public|private|protected)?\s+class\s+([a-zA-Z0-9_]+)(?:\s+extends\s+([a-zA-Z0-9_]+))?(?:\s+implements\s+([a-zA-Z0-9_, ]+))?", line)
            if class_match:
                result["classes"].append({
                    "name": class_match.group(1),
                    "inherits": class_match.group(2) if class_match.group(2) else "",
                    "implements": class_match.group(3) if class_match.group(3) else "",
                    "line": line_num
                })
        
        # Check for imports
        elif line.startswith("import "):
            result["imports"].append({
                "statement": line,
                "line": line_num
            })
        
        # Check for variable declarations
        var_match = re.search(r"(?:private|public|protected)?\s+(?:final\s+)?([a-zA-Z0-9_<>]+)\s+([a-zA-Z0-9_]+)\s*=", line)
        if var_match:
            result["variables"].append({
                "name": var_match.group(2),
                "type": var_match.group(1),
                "line": line_num
            })
    
    def _parse_c_cpp(self, line: str, line_num: int, result: Dict[str, Any]):
        """Parse C/C++ code line"""
        # Check for function definitions
        func_match = re.search(r"(?:[a-zA-Z0-9_*]+\s+)+([a-zA-Z0-9_]+)\s*\((.*)\)\s*(?:const)?\s*(?:{|$)", line)
        if func_match and not line.endswith(";"):
            result["functions"].append({
                "name": func_match.group(1),
                "params": func_match.group(2),
                "line": line_num
            })
        
        # Check for class/struct definitions
        elif "class " in line or "struct " in line:
            class_match = re.search(r"(?:class|struct)\s+([a-zA-Z0-9_]+)(?:\s*:\s*(?:public|private|protected)?\s*([a-zA-Z0-9_]+))?", line)
            if class_match:
                result["classes"].append({
                    "name": class_match.group(1),
                    "inherits": class_match.group(2) if class_match.group(2) else "",
                    "line": line_num,
                    "type": "class" if "class " in line else "struct"
                })
        
        # Check for includes
        elif line.startswith("#include"):
            result["imports"].append({
                "statement": line,
                "line": line_num
            })
        
        # Check for variable declarations
        var_match = re.search(r"(?:static\s+)?(?:const\s+)?([a-zA-Z0-9_*]+)\s+([a-zA-Z0-9_]+)(?:\s*=|;|\[)", line)
        if var_match and not func_match:
            result["variables"].append({
                "name": var_match.group(2),
                "type": var_match.group(1),
                "line": line_num
            })
    
    def _parse_go(self, line: str, line_num: int, result: Dict[str, Any]):
        """Parse Go code line"""
        # Check for function definitions
        if line.startswith("func "):
            func_match = re.search(r"func\s+(?:\([^)]+\)\s+)?([a-zA-Z0-9_]+)\s*\((.*)\)", line)
            if func_match:
                result["functions"].append({
                    "name": func_match.group(1),
                    "params": func_match.group(2),
                    "line": line_num
                })
        
        # Check for struct definitions
        elif "type " in line and "struct" in line:
            struct_match = re.search(r"type\s+([a-zA-Z0-9_]+)\s+struct", line)
            if struct_match:
                result["classes"].append({
                    "name": struct_match.group(1),
                    "line": line_num,
                    "type": "struct"
                })
        
        # Check for imports
        elif line.startswith("import "):
            result["imports"].append({
                "statement": line,
                "line": line_num
            })
        
        # Check for variable declarations
        elif ":=" in line:
            var_match = re.search(r"([a-zA-Z0-9_]+)\s*:=", line)
            if var_match:
                result["variables"].append({
                    "name": var_match.group(1),
                    "line": line_num,
                    "value": line.split(":=", 1)[1].strip()
                })
        elif "var " in line:
            var_match = re.search(r"var\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_]+)(?:\s*=)?", line)
            if var_match:
                result["variables"].append({
                    "name": var_match.group(1),
                    "type": var_match.group(2),
                    "line": line_num
                })
    
    def _check_for_issues(self, code_content: str, language: str, result: Dict[str, Any]):
        """Check for potential issues in the code"""
        issues = []
        
        # Check for common issues across languages
        
        # 1. Check for TODO comments
        todo_pattern = r"(?:TODO|FIXME|XXX|BUG|HACK)"
        todos = re.finditer(todo_pattern, code_content, re.IGNORECASE)
        for match in todos:
            # Find the line number
            line_num = code_content[:match.start()].count('\n') + 1
            line = code_content.split('\n')[line_num - 1].strip()
            issues.append({
                "type": "todo",
                "line": line_num,
                "description": f"TODO comment: {line}"
            })
        
        # 2. Check for hardcoded credentials
        credential_patterns = [
            r"password\s*=\s*['\"]([^'\"]+)['\"]",
            r"api[_-]?key\s*=\s*['\"]([^'\"]+)['\"]",
            r"secret\s*=\s*['\"]([^'\"]+)['\"]",
            r"token\s*=\s*['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in credential_patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                # Find the line number
                line_num = code_content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "security",
                    "line": line_num,
                    "description": f"Potential hardcoded credential at line {line_num}"
                })
        
        # 3. Language-specific checks
        if language == "python":
            # Check for bare except clauses
            bare_excepts = re.finditer(r"except\s*:", code_content)
            for match in bare_excepts:
                line_num = code_content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "style",
                    "line": line_num,
                    "description": "Bare except clause should specify exceptions"
                })
            
            # Check for mutable default arguments
            mutable_defaults = re.finditer(r"def\s+\w+\s*\(.*?=\s*(?:\[\]|{}|\{\}|\(\)).*?\):", code_content)
            for match in mutable_defaults:
                line_num = code_content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "bug",
                    "line": line_num,
                    "description": "Mutable default argument (list, dict, etc.) can cause unexpected behavior"
                })
        
        elif language in ["javascript", "typescript"]:
            # Check for console.log statements
            console_logs = re.finditer(r"console\.log\(", code_content)
            for match in console_logs:
                line_num = code_content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "debug",
                    "line": line_num,
                    "description": "console.log statement should be removed in production code"
                })
            
            # Check for == instead of ===
            loose_equals = re.finditer(r"[^=]=[^=]", code_content)
            for match in loose_equals:
                line_num = code_content[:match.start()].count('\n') + 1
                line = code_content.split('\n')[line_num - 1].strip()
                if "=" in line and not re.search(r"[<>!=]=", line) and not line.strip().startswith("//"):
                    issues.append({
                        "type": "style",
                        "line": line_num,
                        "description": "Consider using === instead of == for comparison"
                    })
        
        # Add the issues to the result
        result["potential_issues"].extend(issues)
    
    def analyze_complexity(self, code_content: str, language: str) -> Dict[str, Any]:
        """
        Analyze code complexity
        
        Args:
            code_content: The code to analyze
            language: Detected programming language
            
        Returns:
            Dictionary with complexity metrics
        """
        result = {
            "cyclomatic_complexity": 0,
            "nesting_depth": 0,
            "function_count": 0,
            "class_count": 0,
            "line_count": code_content.count('\n') + 1,
            "comment_ratio": 0
        }
        
        # Skip analysis for unknown language
        if language == "unknown":
            return result
        
        # Get language-specific patterns
        patterns = self.language_patterns.get(language, {})
        comment_marker = patterns.get("comment")
        
        # Count functions and classes
        parsed = self.parse_code(code_content, language)
        result["function_count"] = len(parsed["functions"])
        result["class_count"] = len(parsed["classes"])
        
        # Calculate comment ratio
        comment_count = len(parsed["comments"])
        result["comment_ratio"] = comment_count / result["line_count"] if result["line_count"] > 0 else 0
        
        # Calculate cyclomatic complexity (simplified)
        # Count decision points like if, for, while, case, etc.
        decision_patterns = {
            "python": [r"\bif\b", r"\belif\b", r"\bfor\b", r"\bwhile\b", r"\bexcept\b", r"\band\b", r"\bor\b"],
            "javascript": [r"\bif\b", r"\belse if\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\b&&\b", r"\b\|\|\b"],
            "java": [r"\bif\b", r"\belse if\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\b&&\b", r"\b\|\|\b"],
            "c": [r"\bif\b", r"\belse if\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\b&&\b", r"\b\|\|\b"],
            "cpp": [r"\bif\b", r"\belse if\b", r"\bfor\b", r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\b&&\b", r"\b\|\|\b"],
            "go": [r"\bif\b", r"\belse if\b", r"\bfor\b", r"\bswitch\b", r"\bcase\b", r"\b&&\b", r"\b\|\|\b"]
        }
        
        patterns = decision_patterns.get(language, decision_patterns.get("javascript", []))
        complexity = 1  # Base complexity
        
        for pattern in patterns:
            complexity += len(re.findall(pattern, code_content))
        
        result["cyclomatic_complexity"] = complexity
        
        # Calculate maximum nesting depth
        lines = code_content.split('\n')
        max_depth = 0
        current_depth = 0
        
        indent_patterns = {
            "python": r"^(\s*)[^\s]",
            "default": r"^(\s*)[^\s]"
        }
        
        indent_pattern = indent_patterns.get(language, indent_patterns["default"])
        
        prev_indent = 0
        for line in lines:
            if not line.strip() or (comment_marker and line.strip().startswith(comment_marker)):
                continue
                
            match = re.match(indent_pattern, line)
            if match:
                indent = len(match.group(1))
                
                if indent > prev_indent:
                    current_depth += 1
                elif indent < prev_indent:
                    current_depth -= max(0, (prev_indent - indent) // 2)  # Approximate for non-Python
                
                prev_indent = indent
                max_depth = max(max_depth, current_depth)
        
        result["nesting_depth"] = max_depth
        
        return result
