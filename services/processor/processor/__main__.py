import sys

from .processor import HierarchyTemplateProcessor


if __name__ == "__main__":
    processor = HierarchyTemplateProcessor()
    sys.exit(processor.start_processing())
