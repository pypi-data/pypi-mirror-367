import logging
import sys
from pathlib import Path
import argparse
from sixel import converter
import io

def main():
    parser = argparse.ArgumentParser(prog='PySixel converter example')

    parser.add_argument('image_path', type=Path)
    args = parser.parse_args()

    if not args.image_path.exists():
        logging.error(f"Path '{args.image_path}' does not exist.")
        return

    sixel_converter = converter.SixelConverter(args.image_path)
    
    # sixel_converter.write(sys.stdout)

    output_var = io.StringIO()
    sixel_converter.write(output_var)
    result_str = output_var.getvalue()
    output_var.close()
    print(result_str)
    with open("demofile.sixel", "w") as f:
        f.write(result_str)

if __name__ == "__main__":
    main()
