#!/usr/bin/env python3
"""
Component Generator: Create React component files with consistent structure.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


COMPONENT_TEMPLATE = '''import React from 'react';
import {{ Box }} from '@mui/material';

export interface {ComponentName}Props {{
  /** Component description */
  children?: React.ReactNode;
}}

/**
 * {ComponentName} component
 * 
 * @description Add component description here
 */
export function {ComponentName}({{ children }}: {ComponentName}Props) {{
  return (
    <Box>
      {{children}}
    </Box>
  );
}}

export default {ComponentName};
'''

TEST_TEMPLATE = '''import {{ describe, it, expect }} from 'vitest';
import {{ render, screen }} from '@testing-library/react';
import {{ {ComponentName} }} from './{ComponentName}';

describe('{ComponentName}', () => {{
  it('renders correctly', () => {{
    render(<{ComponentName}>Test content</{ComponentName}>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  }});
}});
'''

STORY_TEMPLATE = '''import type { Meta, StoryObj } from '@storybook/react';
import { {ComponentName} } from './{ComponentName}';

const meta: Meta<typeof {ComponentName}> = {{
  title: 'Components/{ComponentName}',
  component: {ComponentName},
  parameters: {{
    layout: 'centered',
  }},
  tags: ['autodocs'],
}};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {{
  args: {{
    children: '{ComponentName} content',
  }},
}};
'''


def generate_component(name: str, output_dir: Path, with_story: bool = False, with_test: bool = True) -> None:
    """Generate component files."""
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Format component name (PascalCase)
    component_name = ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))
    
    # Generate component file
    component_file = output_dir / f"{component_name}.tsx"
    component_content = COMPONENT_TEMPLATE.format(ComponentName=component_name)
    component_file.write_text(component_content)
    print(f"  ✓ Created: {component_file}")
    
    # Generate test file
    if with_test:
        test_file = output_dir / f"{component_name}.test.tsx"
        test_content = TEST_TEMPLATE.format(ComponentName=component_name)
        test_file.write_text(test_content)
        print(f"  ✓ Created: {test_file}")
    
    # Generate story file
    if with_story:
        story_file = output_dir / f"{component_name}.stories.tsx"
        story_content = STORY_TEMPLATE.format(ComponentName=component_name)
        story_file.write_text(story_content)
        print(f"  ✓ Created: {story_file}")
    
    print(f"\n✅ Component '{component_name}' generated successfully!")
    print(f"   Location: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate React component files with consistent structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s Button                           # Generate Button component
  %(prog)s UserCard --dir src/components    # Generate in specific directory
  %(prog)s Header --story                   # Include Storybook story
  %(prog)s Footer --no-test                 # Skip test file
        """
    )
    
    parser.add_argument("name", help="Component name (e.g., 'Button', 'UserCard')")
    parser.add_argument("--dir", default=".", help="Output directory (default: current)")
    parser.add_argument("--story", action="store_true", help="Generate Storybook story file")
    parser.add_argument("--no-test", action="store_true", help="Skip generating test file")
    
    args = parser.parse_args()
    
    output_dir = Path(args.dir).resolve()
    generate_component(args.name, output_dir, args.story, not args.no_test)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
