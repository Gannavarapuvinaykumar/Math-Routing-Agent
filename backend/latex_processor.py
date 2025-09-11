"""
LaTeX Mathematical Notation Support for Math Routing Agent
Converts mathematical expressions to proper LaTeX format
"""

import re
from typing import Dict, List, Tuple

class LaTeXProcessor:
    """Advanced LaTeX mathematical notation processor"""
    
    def __init__(self):
        # Common mathematical symbols and their LaTeX equivalents
        self.symbol_map = {
            '²': '^2',
            '³': '^3',
            '√': '\\sqrt{',
            '∫': '\\int',
            '∂': '\\partial',
            '∞': '\\infty',
            'π': '\\pi',
            'α': '\\alpha',
            'β': '\\beta',
            'γ': '\\gamma',
            'δ': '\\delta',
            'θ': '\\theta',
            'λ': '\\lambda',
            'μ': '\\mu',
            'σ': '\\sigma',
            'Σ': '\\Sigma',
            '±': '\\pm',
            '≠': '\\neq',
            '≤': '\\leq',
            '≥': '\\geq',
            '≈': '\\approx',
            '∈': '\\in',
            '∉': '\\notin',
            '⊂': '\\subset',
            '⊆': '\\subseteq',
            '∪': '\\cup',
            '∩': '\\cap',
            '→': '\\rightarrow',
            '←': '\\leftarrow',
            '↔': '\\leftrightarrow',
            '⇒': '\\Rightarrow',
            '⇐': '\\Leftarrow',
            '⇔': '\\Leftrightarrow'
        }
        
        # Function patterns for LaTeX conversion
        self.function_patterns = [
            (r'sin\(([^)]+)\)', r'\\sin(\\1)'),
            (r'cos\(([^)]+)\)', r'\\cos(\\1)'),
            (r'tan\(([^)]+)\)', r'\\tan(\\1)'),
            (r'log\(([^)]+)\)', r'\\log(\\1)'),
            (r'ln\(([^)]+)\)', r'\\ln(\\1)'),
            (r'exp\(([^)]+)\)', r'\\exp(\\1)'),
            (r'lim\s*([^{]+)', r'\\lim_{\\1}'),
            (r'sum\s*([^{]+)', r'\\sum_{\\1}'),
        ]
        
        # Fraction patterns
        self.fraction_patterns = [
            (r'(\d+)/(\d+)', r'\\frac{\\1}{\\2}'),
            (r'\(([^)]+)\)/\(([^)]+)\)', r'\\frac{\\1}{\\2}'),
        ]
        
        # Matrix patterns
        self.matrix_patterns = [
            (r'\[\[([^\]]+)\]\]', self._convert_matrix),
        ]
    
    def process_text(self, text: str) -> str:
        """Convert mathematical text to LaTeX format"""
        if not text:
            return text
        
        # Process inline math expressions
        processed = self._process_inline_math(text)
        
        # Process display math expressions
        processed = self._process_display_math(processed)
        
        return processed
    
    def _process_inline_math(self, text: str) -> str:
        """Process inline mathematical expressions"""
        # Find potential math expressions
        math_patterns = [
            r'\$([^$]+)\$',  # Already in LaTeX format
            r'([a-zA-Z]+)\^(\d+)',  # Powers
            r'([a-zA-Z]+)_(\d+)',   # Subscripts
            r'(\d+)\*([a-zA-Z]+)',  # Multiplication
        ]
        
        processed = text
        
        # Convert symbols
        for symbol, latex in self.symbol_map.items():
            processed = processed.replace(symbol, latex)
        
        # Convert functions
        for pattern, replacement in self.function_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        # Convert fractions
        for pattern, replacement in self.fraction_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        # Handle powers and subscripts
        processed = re.sub(r'([a-zA-Z]+)\^(\d+)', r'\\1^{\\2}', processed)
        processed = re.sub(r'([a-zA-Z]+)_(\d+)', r'\\1_{\\2}', processed)
        
        return processed
    
    def _process_display_math(self, text: str) -> str:
        """Process display mathematical expressions"""
        # Convert equations to display math
        equation_patterns = [
            (r'([^$])([a-zA-Z]+\s*=\s*[^,\n.]+)([^$])', r'\\1$$\\2$$\\3'),
        ]
        
        processed = text
        for pattern, replacement in equation_patterns:
            processed = re.sub(pattern, replacement, processed)
        
        return processed
    
    def _convert_matrix(self, match) -> str:
        """Convert matrix notation to LaTeX"""
        content = match.group(1)
        rows = content.split(',')
        latex_rows = []
        
        for row in rows:
            elements = row.strip().split()
            latex_rows.append(' & '.join(elements) + ' \\\\')
        
        return f"\\begin{{pmatrix}} {' '.join(latex_rows)} \\end{{pmatrix}}"
    
    def format_step_by_step(self, steps: str) -> str:
        """Format step-by-step solutions with proper LaTeX"""
        if not steps:
            return steps
        
        lines = steps.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                # Process mathematical content in each step
                processed_line = self.process_text(line)
                
                # Add step numbering if not present
                if not re.match(r'^\d+\.', line.strip()):
                    step_num = len([l for l in formatted_lines if l.strip()]) + 1
                    processed_line = f"{step_num}. {processed_line}"
                
                formatted_lines.append(processed_line)
        
        return '\n'.join(formatted_lines)
    
    def validate_latex(self, latex_text: str) -> Tuple[bool, str]:
        """Validate LaTeX syntax and return feedback"""
        errors = []
        
        # Check for balanced braces
        brace_count = latex_text.count('{') - latex_text.count('}')
        if brace_count != 0:
            errors.append(f"Unbalanced braces: {abs(brace_count)} {'extra opening' if brace_count > 0 else 'extra closing'}")
        
        # Check for balanced dollars
        dollar_count = latex_text.count('$')
        if dollar_count % 2 != 0:
            errors.append("Unbalanced math delimiters ($)")
        
        # Check for common LaTeX errors
        common_errors = [
            (r'\\[a-zA-Z]+{[^}]*$', "Unclosed command"),
            (r'\$[^$]*\n[^$]*\$', "Math expression spans multiple lines without proper formatting"),
        ]
        
        for pattern, error_msg in common_errors:
            if re.search(pattern, latex_text):
                errors.append(error_msg)
        
        if errors:
            return False, "; ".join(errors)
        return True, "Valid LaTeX"

# Global LaTeX processor instance
latex_processor = LaTeXProcessor()
