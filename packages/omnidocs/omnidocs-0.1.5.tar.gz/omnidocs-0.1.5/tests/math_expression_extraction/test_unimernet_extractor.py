"""
Simple UniMERNetExtractor test - just pass an image and print the full output.
"""

# Copyright (c) OpenDataLab (https://github.com/opendatalab/UniMERNet)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from omnidocs.tasks.math_expression_extraction.extractors.unimernet import UniMERNetExtractor

def main():
    """Simple test - just pass an image and print the output."""

    print("Simple UniMERNetExtractor Test")
    print("=" * 50)

    try:
        # Initialize extractor
        print("Initializing UniMERNetExtractor...")
        extractor = UniMERNetExtractor(
            device='cpu',
            show_log=True
        )
        print("UniMERNetExtractor initialized!")

        # Test with the math equation image
        image_path = "tests/math_expression_extraction/assets/math_equation.png"
        print(f"Processing image: {image_path}")

        result = extractor.extract(image_path)

        print("\n" + "=" * 80)
        print("UNIMERNET OUTPUT:")
        print("=" * 80)
        print(f"Result type: {type(result)}")
        print(f"Result object: {result}")

        if hasattr(result, 'expressions'):
            print(f"Number of expressions: {len(result.expressions)}")
            for i, expr in enumerate(result.expressions):
                print(f"\nExpression {i+1}:")
                print(f"  Raw: {repr(expr)}")
                print(f"  Display: {expr}")
                print(f"  Length: {len(expr)} characters")

        if hasattr(result, 'source_img_size'):
            print(f"Source image size: {result.source_img_size}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
