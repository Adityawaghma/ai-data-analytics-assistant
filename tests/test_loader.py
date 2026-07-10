import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest
import pandas as pd
from src.loader import load_file
def test_load_csv(tmp_path):
   f = tmp_path / 'test.csv'
   f.write_text('a,b\n1,2\n3,4')
   df = load_file(str(f))
   assert len(df) == 2
def test_invalid_ext():
   with pytest.raises(ValueError):
     load_file('file.pdf')

def test_missing_file():
   with pytest.raises(FileNotFoundError):
     load_file('nonexistent.csv')