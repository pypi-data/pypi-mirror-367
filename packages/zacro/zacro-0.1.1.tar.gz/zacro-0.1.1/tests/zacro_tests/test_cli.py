#!/usr/bin/env python

import os
import subprocess
import sys
import tempfile
import unittest


class TestCLI(unittest.TestCase):
    """Test command-line interface"""

    def setUp(self):
        """Set up temporary files for testing"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_cli_help(self):
        """Test CLI help command"""
        result = subprocess.run([sys.executable, '-m', 'zacro.cli', '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Fast Rust implementation of xacro', result.stdout)

    def test_cli_simple_processing(self):
        """Test basic CLI processing"""
        # Create test input file
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="simple_link" params="name">
    <link name="${name}"/>
  </xacro:macro>
  <xacro:simple_link name="test_link"/>
</robot>'''

        input_file = os.path.join(self.temp_dir, "test.xacro")
        with open(input_file, 'w') as f:
            f.write(input_content)

        # Test stdout output
        result = subprocess.run([sys.executable, '-m', 'zacro.cli', input_file],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('<link name="test_link"', result.stdout)

    def test_cli_file_output(self):
        """Test CLI with file output"""
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:property name="size" value="1.0"/>
  <link name="base">
    <visual>
      <geometry>
        <box size="${size} ${size} ${size}"/>
      </geometry>
    </visual>
  </link>
</robot>'''

        input_file = os.path.join(self.temp_dir, "test.xacro")
        output_file = os.path.join(self.temp_dir, "test.urdf")

        with open(input_file, 'w') as f:
            f.write(input_content)

        # Test file output
        result = subprocess.run([
            sys.executable, '-m', 'zacro.cli',
            input_file, '-o', output_file, '--format'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r') as f:
            content = f.read()

        self.assertIn('<link name="base">', content)
        self.assertIn('size="1.0 1.0 1.0"', content)

    def test_cli_format_option(self):
        """Test CLI format option"""
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <link name="test"/>
</robot>'''

        input_file = os.path.join(self.temp_dir, "test.xacro")
        with open(input_file, 'w') as f:
            f.write(input_content)

        # Test formatted output
        result = subprocess.run([
            sys.executable, '-m', 'zacro.cli',
            input_file, '--format'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.startswith('<?xml version="1.0" encoding="UTF-8"?>'))
        self.assertGreater(result.stdout.count('\n'), 2)

    def test_cli_remove_first_joint(self):
        """Test CLI remove-first-joint option"""
        input_content = '''<?xml version="1.0"?>
<robot xmlns:xacro="http://ros.org/wiki/xacro">
  <xacro:macro name="module" params="name">
    <joint name="${name}_connection" type="fixed">
      <parent link="base"/>
      <child link="${name}_link"/>
    </joint>
    <link name="${name}_link"/>
  </xacro:macro>

  <link name="base"/>
  <xacro:module name="test"/>
</robot>'''

        input_file = os.path.join(self.temp_dir, "test.xacro")
        with open(input_file, 'w') as f:
            f.write(input_content)

        # Test with remove-first-joint
        result = subprocess.run([
            sys.executable, '-m', 'zacro.cli',
            input_file, '--remove-first-joint'
        ], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count('<joint'), 0)
        self.assertIn('<link name="test_link"', result.stdout)

    def test_cli_error_handling(self):
        """Test CLI error handling"""
        # Test with non-existent file
        result = subprocess.run([
            sys.executable, '-m', 'zacro.cli',
            'non_existent_file.xacro'
        ], capture_output=True, text=True)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not found', result.stderr)


if __name__ == '__main__':
    unittest.main()
