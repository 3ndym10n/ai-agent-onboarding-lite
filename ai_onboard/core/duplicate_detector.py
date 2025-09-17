"""
Duplicate Code Detection System

This module provides comprehensive duplicate code detection including:
- Token-based similarity analysis
- AST-based structural comparison
- Text-based diff analysis
- Duplicate code reporting and recommendations

Author: AI Assistant
"""

import ast
import difflib
import hashlib
import os
import re
import tokenize
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.utils import read_json, write_json


@dataclass
class CodeBlock:
    """Represents a block of code for duplicate analysis."""

    file_path: str
    start_line: int
    end_line: int
    content: str
    tokens: List[str] = field(default_factory=list)
    ast_hash: Optional[str] = None
    content_hash: str = ""


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate code blocks."""

    blocks: List[CodeBlock] = field(default_factory=list)
    similarity_score: float = 0.0
    duplicate_type: str = "unknown"  # 'exact', 'near', 'structural'


@dataclass
class DuplicateAnalysisResult:
    """Complete duplicate code analysis result."""

    files_analyzed: int = 0
    total_blocks: int = 0
    duplicate_groups: List[DuplicateGroup] = field(default_factory=list)
    exact_duplicates: int = 0
    near_duplicates: int = 0
    structural_duplicates: int = 0
    total_duplicate_lines: int = 0


class DuplicateDetector:
    """
    Comprehensive duplicate code detection engine.

    Provides multiple techniques for identifying duplicate code:
    - Exact duplicate detection via hashing
    - Near-duplicate detection via similarity algorithms
    - Structural duplicate detection via AST comparison
    """

    def __init__(
        self,
        root_path: Path,
        exclude_patterns: Optional[List[str]] = None,
        min_block_size: int = 6,
    ):
        """
        Initialize the duplicate detector.

        Args:
            root_path: Root directory to analyze
            exclude_patterns: List of glob patterns to exclude
            min_block_size: Minimum lines for a code block to be considered
        """
        self.root_path = root_path
        self.exclude_patterns = exclude_patterns or [
            "__pycache__",
            "*.pyc",
            ".git",
            ".ai_onboard",
            "build",
            "dist",
            "*.egg-info",
            "node_modules",
            "venv",
            ".venv",
            "env",
            ".env",
        ]
        self.min_block_size = min_block_size

        # Analysis state
        self.code_blocks: List[CodeBlock] = []
        self.hash_to_blocks: Dict[str, List[CodeBlock]] = defaultdict(list)
        self.ast_hash_to_blocks: Dict[str, List[CodeBlock]] = defaultdict(list)

    def analyze_duplicates(self) -> DuplicateAnalysisResult:
        """
        Perform comprehensive duplicate code analysis.

        Returns:
            DuplicateAnalysisResult with complete analysis
        """
        print("🔍 Starting comprehensive duplicate code analysis...")

        # Phase 1: Extract code blocks
        print("📦 Phase 1: Extracting code blocks...")
        python_files = self._find_python_files()
        print(f"   Found {len(python_files)} Python files")

        for file_path in python_files:
            try:
                blocks = self._extract_code_blocks(file_path)
                self.code_blocks.extend(blocks)
                print(
                    f"   Extracted {len(blocks)} blocks from {os.path.basename(file_path)}"
                )
            except Exception as e:
                print(f"   ⚠️  Error extracting blocks from {file_path}: {e}")

        print(f"   Total code blocks extracted: {len(self.code_blocks)}")

        # Phase 2: Index blocks by content hash
        print("🏷️  Phase 2: Indexing blocks by content...")
        for block in self.code_blocks:
            content_hash = self._hash_content(block.content)
            block.content_hash = content_hash
            self.hash_to_blocks[content_hash].append(block)

        # Phase 3: Detect exact duplicates
        print("🎯 Phase 3: Detecting exact duplicates...")
        result = DuplicateAnalysisResult()
        result.files_analyzed = len(python_files)
        result.total_blocks = len(self.code_blocks)

        exact_groups = self._find_exact_duplicates()
        result.duplicate_groups.extend(exact_groups)
        result.exact_duplicates = len(exact_groups)

        # Phase 4: Detect near duplicates
        print("🔄 Phase 4: Detecting near duplicates...")
        near_groups = self._find_near_duplicates()
        result.duplicate_groups.extend(near_groups)
        result.near_duplicates = len(near_groups)

        # Phase 5: Detect structural duplicates
        print("🏗️  Phase 5: Detecting structural duplicates...")
        structural_groups = self._find_structural_duplicates()
        result.duplicate_groups.extend(structural_groups)
        result.structural_duplicates = len(structural_groups)

        # Phase 6: Calculate metrics
        print("📊 Phase 6: Calculating duplicate metrics...")
        result.total_duplicate_lines = self._calculate_total_duplicate_lines(
            result.duplicate_groups
        )

        print("✅ Duplicate code analysis complete!")
        return result

    def _find_python_files(self) -> List[str]:
        """Find all Python files in the codebase."""
        python_files = []

        for root, dirs, files in os.walk(self.root_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]

            for file in files:
                if file.endswith(".py") and not self._is_excluded(
                    os.path.join(root, file)
                ):
                    python_files.append(os.path.join(root, file))

        return python_files

    def _is_excluded(self, path: str) -> bool:
        """Check if a path should be excluded."""
        path_str = str(path)

        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True

            # Handle glob-like patterns
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(
                    os.path.basename(path_str), pattern
                ):
                    return True

        return False

    def _extract_code_blocks(self, file_path: str) -> List[CodeBlock]:
        """Extract meaningful code blocks from a Python file."""
        blocks = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")
            tree = ast.parse(content, filename=file_path)

            # Extract function definitions
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    start_line = node.lineno - 1  # Convert to 0-based indexing
                    end_line = self._find_function_end(node, lines)
                    if end_line - start_line >= self.min_block_size:
                        block_content = "\n".join(lines[start_line:end_line])
                        block = CodeBlock(
                            file_path=file_path,
                            start_line=start_line + 1,  # Convert back to 1-based
                            end_line=end_line,
                            content=block_content,
                        )
                        block.tokens = self._tokenize_code(block_content)
                        blocks.append(block)

            # Extract class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    start_line = node.lineno - 1
                    end_line = self._find_class_end(node, lines)
                    if end_line - start_line >= self.min_block_size:
                        block_content = "\n".join(lines[start_line:end_line])
                        block = CodeBlock(
                            file_path=file_path,
                            start_line=start_line + 1,
                            end_line=end_line,
                            content=block_content,
                        )
                        block.tokens = self._tokenize_code(block_content)
                        blocks.append(block)

            # Extract large code blocks (methods within classes)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            start_line = item.lineno - 1
                            end_line = self._find_function_end(item, lines)
                            if end_line - start_line >= self.min_block_size:
                                block_content = "\n".join(lines[start_line:end_line])
                                block = CodeBlock(
                                    file_path=file_path,
                                    start_line=start_line + 1,
                                    end_line=end_line,
                                    content=block_content,
                                )
                                block.tokens = self._tokenize_code(block_content)
                                blocks.append(block)

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"   ⚠️  Error parsing {file_path}: {e}")

        return blocks

    def _find_function_end(self, func_node: ast.FunctionDef, lines: List[str]) -> int:
        """Find the end line of a function."""
        # Simple heuristic: find the next function/class at the same indentation level
        start_indent = self._get_line_indent(lines[func_node.lineno - 1])

        for i in range(func_node.lineno, len(lines)):
            line = lines[i]
            if line.strip().startswith(("def ", "class ", "@")):
                indent = self._get_line_indent(line)
                if indent <= start_indent and line.strip():
                    return i
            elif line.strip() and self._get_line_indent(line) < start_indent:
                return i

        return len(lines)

    def _find_class_end(self, class_node: ast.ClassDef, lines: List[str]) -> int:
        """Find the end line of a class."""
        return self._find_function_end(class_node, lines)

    def _get_line_indent(self, line: str) -> int:
        """Get the indentation level of a line."""
        return len(line) - len(line.lstrip())

    def _tokenize_code(self, code: str) -> List[str]:
        """Tokenize code into meaningful tokens for comparison."""
        tokens = []
        try:
            # Use Python's tokenize module
            import io

            token_stream = tokenize.generate_tokens(io.StringIO(code).readline)

            for tok in token_stream:
                if tok.type in (
                    tokenize.NAME,
                    tokenize.STRING,
                    tokenize.NUMBER,
                    tokenize.OP,
                ):
                    if tok.string not in ("\n", "\t", " "):
                        tokens.append(tok.string)
                elif tok.type == tokenize.NEWLINE:
                    continue
                elif tok.type == tokenize.INDENT:
                    tokens.append("INDENT")
                elif tok.type == tokenize.DEDENT:
                    tokens.append("DEDENT")
        except:
            # Fallback: simple split by whitespace and punctuation
            tokens = re.findall(r"\w+|[^\w\s]", code)

        return tokens

    def _hash_content(self, content: str) -> str:
        """Generate a hash of the content."""
        # Normalize whitespace for better duplicate detection
        normalized = re.sub(r"\s+", " ", content.strip())
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()

    def _find_exact_duplicates(self) -> List[DuplicateGroup]:
        """Find exact duplicate code blocks."""
        groups = []

        for hash_value, blocks in self.hash_to_blocks.items():
            if len(blocks) > 1:
                # All blocks with the same hash are exact duplicates
                group = DuplicateGroup(
                    blocks=blocks, similarity_score=1.0, duplicate_type="exact"
                )
                groups.append(group)

        return groups

    def _find_near_duplicates(self) -> List[DuplicateGroup]:
        """Find near-duplicate code blocks using similarity algorithms."""
        groups = []
        processed = set()

        # Compare blocks that are similar in size and token count
        size_groups = defaultdict(list)
        for block in self.code_blocks:
            size_groups[len(block.tokens)].append(block)

        for size, blocks in size_groups.items():
            if len(blocks) < 2:
                continue

            # Compare each pair of blocks
            for i, block1 in enumerate(blocks):
                for j, block2 in enumerate(blocks[i + 1 :], i + 1):
                    pair_key = (block1.content_hash, block2.content_hash)
                    if pair_key in processed:
                        continue
                    processed.add(pair_key)

                    # Skip if they're already exact duplicates
                    if block1.content_hash == block2.content_hash:
                        continue

                    similarity = self._calculate_similarity(block1, block2)
                    if similarity >= 0.8:  # 80% similarity threshold
                        # Check if either block is already in a group
                        existing_group = None
                        for group in groups:
                            if any(
                                b.content_hash
                                in (block1.content_hash, block2.content_hash)
                                for b in group.blocks
                            ):
                                existing_group = group
                                break

                        if existing_group:
                            # Add to existing group if not already there
                            if not any(
                                b.content_hash == block1.content_hash
                                for b in existing_group.blocks
                            ):
                                existing_group.blocks.append(block1)
                            if not any(
                                b.content_hash == block2.content_hash
                                for b in existing_group.blocks
                            ):
                                existing_group.blocks.append(block2)
                            existing_group.similarity_score = min(
                                existing_group.similarity_score, similarity
                            )
                        else:
                            # Create new group
                            group = DuplicateGroup(
                                blocks=[block1, block2],
                                similarity_score=similarity,
                                duplicate_type="near",
                            )
                            groups.append(group)

        return groups

    def _find_structural_duplicates(self) -> List[DuplicateGroup]:
        """Find structurally similar code blocks using AST comparison."""
        groups = []
        processed = set()

        # Index blocks by AST structure
        for block in self.code_blocks:
            try:
                tree = ast.parse(block.content)
                ast_hash = self._hash_ast(tree)
                block.ast_hash = ast_hash
                self.ast_hash_to_blocks[ast_hash].append(block)
            except:
                continue

        # Find blocks with similar AST structures
        for ast_hash, blocks in self.ast_hash_to_blocks.items():
            if len(blocks) > 1:
                group = DuplicateGroup(
                    blocks=blocks,
                    similarity_score=0.9,  # AST similarity is high
                    duplicate_type="structural",
                )
                groups.append(group)

        return groups

    def _calculate_similarity(self, block1: CodeBlock, block2: CodeBlock) -> float:
        """Calculate similarity between two code blocks."""
        # Use multiple similarity metrics

        # 1. Token-based similarity
        if block1.tokens and block2.tokens:
            token_similarity = difflib.SequenceMatcher(
                None, block1.tokens, block2.tokens
            ).ratio()
        else:
            token_similarity = 0.0

        # 2. Text-based similarity
        text_similarity = difflib.SequenceMatcher(
            None, block1.content, block2.content
        ).ratio()

        # 3. Length similarity (penalty for very different sizes)
        len1, len2 = len(block1.content), len(block2.content)
        length_similarity = 1.0 - abs(len1 - len2) / max(len1, len2)

        # Weighted combination
        similarity = (
            token_similarity * 0.5 + text_similarity * 0.3 + length_similarity * 0.2
        )

        return similarity

    def _hash_ast(self, tree: ast.AST) -> str:
        """Generate a hash representing the AST structure."""
        # Create a simplified representation of the AST
        structure = []

        def traverse(node, depth=0):
            if depth > 10:  # Limit depth to avoid infinite recursion
                return

            node_type = type(node).__name__
            structure.append(node_type)

            if isinstance(node, ast.FunctionDef):
                structure.append(f"func:{node.name}")
            elif isinstance(node, ast.ClassDef):
                structure.append(f"class:{node.name}")
            elif isinstance(node, ast.Name):
                structure.append(f"name:{node.id}")
            elif isinstance(node, ast.Str):
                structure.append("string")
            elif isinstance(node, ast.Num):
                structure.append("number")

            for child in ast.iter_child_nodes(node):
                traverse(child, depth + 1)

        traverse(tree)
        structure_str = "|".join(structure)
        return hashlib.md5(structure_str.encode("utf-8")).hexdigest()

    def _calculate_total_duplicate_lines(
        self, duplicate_groups: List[DuplicateGroup]
    ) -> int:
        """Calculate total lines of duplicate code."""
        total_lines = 0
        processed_blocks = set()

        for group in duplicate_groups:
            # Count unique duplicate lines (avoid double-counting)
            for block in group.blocks:
                block_key = (block.file_path, block.start_line, block.end_line)
                if block_key not in processed_blocks:
                    lines_in_block = block.end_line - block.start_line + 1
                    total_lines += lines_in_block
                    processed_blocks.add(block_key)

        return total_lines

    def generate_duplicate_report(
        self, result: DuplicateAnalysisResult, output_path: Optional[str] = None
    ) -> str:
        """Generate a comprehensive duplicate code analysis report."""
        report_lines = []

        report_lines.append("=" * 80)
        report_lines.append("🔍 DUPLICATE CODE ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")

        report_lines.append("📊 OVERVIEW:")
        report_lines.append(f"   Files Analyzed: {result.files_analyzed}")
        report_lines.append(f"   Code Blocks Analyzed: {result.total_blocks}")
        report_lines.append(
            f"   Duplicate Groups Found: {len(result.duplicate_groups)}"
        )
        report_lines.append(f"   Exact Duplicates: {result.exact_duplicates}")
        report_lines.append(f"   Near Duplicates: {result.near_duplicates}")
        report_lines.append(f"   Structural Duplicates: {result.structural_duplicates}")
        report_lines.append(f"   Total Duplicate Lines: {result.total_duplicate_lines}")
        report_lines.append("")

        # Summary by type
        if result.duplicate_groups:
            type_counts = defaultdict(int)
            for group in result.duplicate_groups:
                type_counts[group.duplicate_type] += 1

            report_lines.append("📈 DUPLICATES BY TYPE:")
            for dup_type, count in type_counts.items():
                report_lines.append(f"   {dup_type}: {count} groups")
            report_lines.append("")

        # Top duplicate groups
        if result.duplicate_groups:
            # Sort by number of duplicates (largest groups first)
            sorted_groups = sorted(
                result.duplicate_groups, key=lambda g: len(g.blocks), reverse=True
            )[:10]

            report_lines.append("🎯 LARGEST DUPLICATE GROUPS:")
            for i, group in enumerate(sorted_groups, 1):
                dup_type_emoji = {"exact": "🎯", "near": "🔄", "structural": "🏗️"}.get(
                    group.duplicate_type, "❓"
                )
                report_lines.append(
                    f"   {i}. {dup_type_emoji} {group.duplicate_type.upper()} - {len(group.blocks)} copies"
                )
                report_lines.append(".2f")
                report_lines.append("      Locations:")

                for block in group.blocks[:3]:  # Show first 3 locations
                    report_lines.append(
                        f"        {block.file_path}:{block.start_line}-{block.end_line}"
                    )

                if len(group.blocks) > 3:
                    report_lines.append(f"        ... and {len(group.blocks) - 3} more")
                report_lines.append("")

        # Recommendations
        if result.duplicate_groups:
            report_lines.append("💡 RECOMMENDATIONS:")
            report_lines.append(
                "   1. Extract duplicate code into shared functions or classes"
            )
            report_lines.append("   2. Create base classes for similar functionality")
            report_lines.append(
                "   3. Use configuration or strategy patterns to reduce duplication"
            )
            report_lines.append(
                "   4. Consider using code generation for repetitive patterns"
            )
            report_lines.append("")

        # Impact assessment
        if result.total_duplicate_lines > 0:
            report_lines.append("📊 IMPACT ASSESSMENT:")
            if result.total_duplicate_lines < 100:
                report_lines.append(
                    "   🔍 LOW: Minimal duplication, codebase is well-structured"
                )
            elif result.total_duplicate_lines < 500:
                report_lines.append(
                    "   ⚠️  MEDIUM: Moderate duplication, consider refactoring"
                )
            else:
                report_lines.append(
                    "   🚨 HIGH: Significant duplication, refactoring recommended"
                )
            report_lines.append("")

        report_lines.append("=" * 80)

        report = "\n".join(report_lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Duplicate code report saved to: {output_path}")

        return report


def main():
    """CLI entry point for duplicate code analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Duplicate Code Detection System")
    parser.add_argument("--path", default=".", help="Path to analyze")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--exclude", nargs="*", help="Additional patterns to exclude")
    parser.add_argument(
        "--min-size", type=int, default=6, help="Minimum block size in lines"
    )

    args = parser.parse_args()

    root_path = Path(args.path)
    detector = DuplicateDetector(root_path, args.exclude, args.min_size)

    try:
        result = detector.analyze_duplicates()
        report = detector.generate_duplicate_report(result, args.output)

        print(report)

    except Exception as e:
        print(f"❌ Error during duplicate analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
