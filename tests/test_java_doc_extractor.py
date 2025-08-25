"""
Unit tests for JavaDocExtractor class.

This module contains comprehensive unit tests for the JavaDocExtractor class,
covering all public methods and various Javadoc extraction scenarios including
success cases, edge cases, and different Javadoc formatting styles.

Author: Rubens Gomes
License: Apache-2.0
"""

import unittest
import re
from typing import Dict

from java_mcp.parser.java_doc_extractor import JavaDocExtractor


class TestJavaDocExtractor(unittest.TestCase):
    """Test cases for JavaDocExtractor class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.extractor = JavaDocExtractor()

    def test_init(self):
        """Test JavaDocExtractor initialization."""
        extractor = JavaDocExtractor()

        # Verify that the javadoc_pattern is properly initialized
        self.assertIsInstance(extractor.javadoc_pattern, re.Pattern)

        # Verify the pattern has DOTALL flag
        self.assertTrue(extractor.javadoc_pattern.flags & re.DOTALL)

    def test_extract_javadocs_simple_class(self):
        """Test extracting Javadocs from a simple Java class."""
        source_code = '''
/**
 * This is a simple class.
 * @author John Doe
 */
public class SimpleClass {
    
    /**
     * This is a field.
     */
    private String name;
    
    /**
     * This is a method.
     * @param value the input value
     * @return processed value
     */
    public String process(String value) {
        return value.toUpperCase();
    }
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # Should find 3 Javadoc blocks
        self.assertEqual(len(result), 3)

        # Check class Javadoc (starts at line 2)
        self.assertIn(2, result)
        class_doc = result[2]
        self.assertIn("This is a simple class.", class_doc)
        self.assertIn("@author John Doe", class_doc)

        # Check field Javadoc (starts at line 8)
        self.assertIn(8, result)
        field_doc = result[8]
        self.assertIn("This is a field.", field_doc)

        # Check method Javadoc (starts at line 13, not 12)
        self.assertIn(13, result)
        method_doc = result[13]
        self.assertIn("This is a method.", method_doc)
        self.assertIn("@param value the input value", method_doc)
        self.assertIn("@return processed value", method_doc)

    def test_extract_javadocs_complex_formatting(self):
        """Test extracting Javadocs with complex formatting."""
        source_code = '''
/**
 * Complex class with detailed documentation.
 * 
 * This class demonstrates various Javadoc features including:
 * <ul>
 *   <li>HTML formatting</li>
 *   <li>Multiple paragraphs</li>
 *   <li>Code examples</li>
 * </ul>
 * 
 * Example usage:
 * <pre>
 * ComplexClass obj = new ComplexClass();
 * obj.doSomething();
 * </pre>
 * 
 * @author Jane Smith
 * @version 1.0
 * @since 2023-01-01
 * @see SimpleClass
 */
public class ComplexClass {
    
    /**
     * Performs a complex operation with multiple parameters.
     * 
     * This method takes several parameters and performs validation
     * before processing the data.
     * 
     * @param name the name parameter, must not be null
     * @param age the age parameter, must be positive
     * @param active whether the entity is active
     * @return the result of the operation
     * @throws IllegalArgumentException if parameters are invalid
     * @throws ProcessingException if processing fails
     * @deprecated Use {@link #newMethod(String, int)} instead
     */
    public String complexMethod(String name, int age, boolean active) 
            throws IllegalArgumentException, ProcessingException {
        return "result";
    }
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # Should find 2 Javadoc blocks
        self.assertEqual(len(result), 2)

        # Check class Javadoc
        class_doc_line = min(result.keys())
        class_doc = result[class_doc_line]

        self.assertIn("Complex class with detailed documentation.", class_doc)
        self.assertIn("HTML formatting", class_doc)
        self.assertIn("@author Jane Smith", class_doc)
        self.assertIn("@version 1.0", class_doc)
        self.assertIn("@since 2023-01-01", class_doc)
        self.assertIn("@see SimpleClass", class_doc)

        # Check method Javadoc
        method_doc_line = max(result.keys())
        method_doc = result[method_doc_line]

        self.assertIn("Performs a complex operation", method_doc)
        self.assertIn("@param name the name parameter", method_doc)
        self.assertIn("@param age the age parameter", method_doc)
        self.assertIn("@param active whether the entity", method_doc)
        self.assertIn("@return the result", method_doc)
        self.assertIn("@throws IllegalArgumentException", method_doc)
        self.assertIn("@throws ProcessingException", method_doc)
        self.assertIn("@deprecated", method_doc)

    def test_extract_javadocs_single_line(self):
        """Test extracting single-line Javadoc comments."""
        source_code = '''
public class SingleLineTest {
    /** Single line field documentation. */
    private String field;
    
    /** Single line method documentation. */
    public void method() {}
    
    /** Another single line with @param tag. */
    public void methodWithParam(String param) {}
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # Should find 3 single-line Javadocs
        self.assertEqual(len(result), 3)

        # Check that content is properly extracted
        javadoc_contents = list(result.values())
        self.assertIn("Single line field documentation.", javadoc_contents)
        self.assertIn("Single line method documentation.", javadoc_contents)
        self.assertIn("Another single line with @param tag.", javadoc_contents)

    def test_extract_javadocs_nested_classes(self):
        """Test extracting Javadocs from nested classes."""
        source_code = '''
/**
 * Outer class documentation.
 */
public class OuterClass {
    
    /**
     * Inner class documentation.
     */
    public static class InnerClass {
        
        /**
         * Inner method documentation.
         */
        public void innerMethod() {}
    }
    
    /**
     * Another inner class.
     */
    private class AnotherInner {
        /** Inner field. */
        private int value;
    }
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # Should find 5 Javadoc blocks
        self.assertEqual(len(result), 5)

        javadoc_contents = list(result.values())
        self.assertIn("Outer class documentation.", javadoc_contents)
        self.assertIn("Inner class documentation.", javadoc_contents)
        self.assertIn("Inner method documentation.", javadoc_contents)
        self.assertIn("Another inner class.", javadoc_contents)
        self.assertIn("Inner field.", javadoc_contents)

    def test_extract_javadocs_empty_source(self):
        """Test extracting Javadocs from empty source code."""
        result = self.extractor.extract_javadocs("")

        self.assertEqual(len(result), 0)
        self.assertIsInstance(result, dict)

    def test_extract_javadocs_no_javadocs(self):
        """Test extracting Javadocs from source with no Javadoc comments."""
        source_code = '''
public class NoJavadocs {
    // Regular comment
    private String field;
    
    /* Block comment */
    public void method() {
        // Another regular comment
    }
}
'''

        result = self.extractor.extract_javadocs(source_code)

        self.assertEqual(len(result), 0)

    def test_extract_javadocs_malformed(self):
        """Test extracting Javadocs with malformed or incomplete blocks."""
        source_code = '''
/**
 * Valid Javadoc.
 */
public class Test {
    
    /* Not a Javadoc - missing second asterisk */
    private String field1;
    
    /**
     * Valid Javadoc that ends properly.
     */
    private String field2;
    
    /** Incomplete Javadoc without closing
    private String field3;
    
    /**
     * Another valid one.
     */
    public void method() {}
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # The regex will match 3 blocks, but the incomplete one captures more content
        self.assertEqual(len(result), 3)

        javadoc_contents = list(result.values())
        self.assertIn("Valid Javadoc.", javadoc_contents)
        self.assertIn("Valid Javadoc that ends properly.", javadoc_contents)

        # The incomplete Javadoc will capture everything until the next closing */
        # So we check for content that includes both the incomplete part and the valid one
        combined_content = next((content for content in javadoc_contents
                               if "Incomplete Javadoc" in content), None)
        self.assertIsNotNone(combined_content)
        self.assertIn("Another valid one.", combined_content)

    def test_extract_javadocs_with_code_blocks(self):
        """Test extracting Javadocs containing code blocks and special characters."""
        source_code = '''
/**
 * Method with code example.
 * 
 * Example:
 * {@code
 * String result = obj.process("input");
 * if (result != null) {
 *     System.out.println(result);
 * }
 * }
 * 
 * @param input the input string
 * @return processed result or {@code null}
 */
public String processWithExample(String input) {
    return input;
}
'''

        result = self.extractor.extract_javadocs(source_code)

        self.assertEqual(len(result), 1)

        javadoc = list(result.values())[0]
        self.assertIn("Method with code example.", javadoc)
        self.assertIn("{@code", javadoc)
        self.assertIn("String result = obj.process", javadoc)
        self.assertIn("@param input the input string", javadoc)
        self.assertIn("@return processed result or {@code null}", javadoc)

    def test_clean_javadoc_basic(self):
        """Test the _clean_javadoc method with basic formatting."""
        raw_content = '''
     * This is a test comment.
     * 
     * @param value the value
     * @return the result
     '''

        cleaned = self.extractor._clean_javadoc(raw_content)

        expected = "This is a test comment.\n@param value the value\n@return the result"
        self.assertEqual(cleaned, expected)

    def test_clean_javadoc_complex_formatting(self):
        """Test the _clean_javadoc method with complex formatting."""
        raw_content = '''
     * Complex method description.
     *
     * This method does several things:
     *   - First thing
     *   - Second thing
     * 
     * @param name the name parameter
     * @param age the age parameter  
     * @return the formatted result
     * @throws IllegalArgumentException when parameters are invalid
     '''

        cleaned = self.extractor._clean_javadoc(raw_content)

        self.assertIn("Complex method description.", cleaned)
        self.assertIn("This method does several things:", cleaned)
        self.assertIn("- First thing", cleaned)
        self.assertIn("- Second thing", cleaned)
        self.assertIn("@param name the name parameter", cleaned)
        self.assertIn("@param age the age parameter", cleaned)
        self.assertIn("@return the formatted result", cleaned)
        self.assertIn("@throws IllegalArgumentException", cleaned)

        # Should not contain leading asterisks or extra whitespace
        self.assertNotIn(" * ", cleaned)
        self.assertNotIn("     *", cleaned)

    def test_clean_javadoc_single_line(self):
        """Test the _clean_javadoc method with single-line content."""
        raw_content = " Single line documentation. "

        cleaned = self.extractor._clean_javadoc(raw_content)

        self.assertEqual(cleaned, "Single line documentation.")

    def test_clean_javadoc_empty_lines(self):
        """Test the _clean_javadoc method with empty lines and whitespace."""
        raw_content = '''
     * First line.
     *
     * 
     *    
     * Second line after empty lines.
     * 
     '''

        cleaned = self.extractor._clean_javadoc(raw_content)

        expected = "First line.\nSecond line after empty lines."
        self.assertEqual(cleaned, expected)

    def test_clean_javadoc_varied_asterisk_patterns(self):
        """Test the _clean_javadoc method with varied asterisk patterns."""
        raw_content = '''
     * Normal line.
     *Another line without space after asterisk.
     *  Line with extra space.
        * Line with extra indentation.
     Line without asterisk.
     '''

        cleaned = self.extractor._clean_javadoc(raw_content)

        lines = cleaned.split('\n')
        self.assertIn("Normal line.", lines)
        self.assertIn("Another line without space after asterisk.", lines)
        self.assertIn("Line with extra space.", lines)
        self.assertIn("Line with extra indentation.", lines)
        self.assertIn("Line without asterisk.", lines)

    def test_clean_javadoc_html_tags(self):
        """Test the _clean_javadoc method preserving HTML tags."""
        raw_content = '''
     * Description with <b>bold</b> text.
     * 
     * <p>Paragraph with <code>code</code> snippet.</p>
     * 
     * <ul>
     *   <li>First item</li>
     *   <li>Second item</li>
     * </ul>
     '''

        cleaned = self.extractor._clean_javadoc(raw_content)

        self.assertIn("<b>bold</b>", cleaned)
        self.assertIn("<p>Paragraph with <code>code</code>", cleaned)
        self.assertIn("<ul>", cleaned)
        self.assertIn("<li>First item</li>", cleaned)
        self.assertIn("<li>Second item</li>", cleaned)

    def test_extract_javadocs_line_numbers_accuracy(self):
        """Test that line numbers are accurately calculated."""
        source_code = '''package com.example;

import java.util.List;

/**
 * Class at line 5.
 */
public class TestClass {
    
    /**
     * Field at line 10.
     */
    private String field;
    
    /**
     * Method at line 15.
     */
    public void method() {}
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # Verify line numbers are correct
        line_numbers = sorted(result.keys())

        # Class Javadoc should start at line 5
        self.assertIn(5, line_numbers)
        self.assertIn("Class at line 5.", result[5])

        # Field Javadoc should start at line 10
        self.assertIn(10, line_numbers)
        self.assertIn("Field at line 10.", result[10])

        # Method Javadoc should start at line 15
        self.assertIn(15, line_numbers)
        self.assertIn("Method at line 15.", result[15])

    def test_extract_javadocs_unicode_content(self):
        """Test extracting Javadocs with Unicode characters."""
        source_code = '''
/**
 * Class with Unicode: é, ñ, 中文, 🚀
 * @author José García
 */
public class UnicodeTest {
    
    /**
     * Method with émojis and spëcial chars: ★☆✓
     * @param naïve the naïve parameter
     * @return résultat with açcénts
     */
    public String méthodé(String naïve) {
        return "résultat";
    }
}
'''

        result = self.extractor.extract_javadocs(source_code)

        self.assertEqual(len(result), 2)

        javadoc_contents = list(result.values())
        unicode_content = next(content for content in javadoc_contents
                              if "Unicode" in content)

        self.assertIn("é, ñ, 中文, 🚀", unicode_content)
        self.assertIn("@author José García", unicode_content)

        method_content = next(content for content in javadoc_contents
                             if "émojis" in content)

        self.assertIn("★☆✓", method_content)
        self.assertIn("@param naïve", method_content)
        self.assertIn("résultat with açcénts", method_content)

    def test_extract_javadocs_interface_and_enum(self):
        """Test extracting Javadocs from interfaces and enums."""
        source_code = '''
/**
 * Test interface documentation.
 */
public interface TestInterface {
    
    /**
     * Interface method documentation.
     */
    void interfaceMethod();
}

/**
 * Test enum documentation.
 */
public enum TestEnum {
    
    /**
     * Enum constant documentation.
     */
    CONSTANT1,
    
    /**
     * Another enum constant.
     */
    CONSTANT2;
    
    /**
     * Enum method documentation.
     */
    public void enumMethod() {}
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # Should find 6 Javadoc blocks (not 5 as originally expected)
        self.assertEqual(len(result), 6)

        javadoc_contents = list(result.values())
        self.assertIn("Test interface documentation.", javadoc_contents)
        self.assertIn("Interface method documentation.", javadoc_contents)
        self.assertIn("Test enum documentation.", javadoc_contents)
        self.assertIn("Enum constant documentation.", javadoc_contents)
        self.assertIn("Another enum constant.", javadoc_contents)
        self.assertIn("Enum method documentation.", javadoc_contents)

    def test_extract_javadocs_edge_case_patterns(self):
        """Test extracting Javadocs with edge case patterns."""
        source_code = '''
public class EdgeCases {
    
    /***/
    private String emptyJavadoc;
    
    /** */
    private String whitespaceOnlyJavadoc;
    
    /**
     *
     */
    private String emptyLinesOnlyJavadoc;
    
    /** Valid single line. */
    private String validSingleLine;
    
    /**
     * Valid multi-line.
     */
    private String validMultiLine;
}
'''

        result = self.extractor.extract_javadocs(source_code)

        # Should handle empty and whitespace-only Javadocs
        # The cleaning process should filter out empty content
        valid_docs = [doc for doc in result.values() if doc.strip()]

        # Should find at least the valid ones
        self.assertGreaterEqual(len(valid_docs), 2)
        self.assertIn("Valid single line.", valid_docs)
        self.assertIn("Valid multi-line.", valid_docs)


if __name__ == '__main__':
    unittest.main()
