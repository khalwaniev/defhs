#!/usr/bin/env python3
"""Execute extracted production locate_audio logic against synthetic Kaggle mount layouts."""
import ast,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'kaggle/rs_final_breakthrough_asr_train826_001/run.py'
def main():
 source=RUN.read_text(encoding='utf-8')
 module=ast.parse(source)
 fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='locate_audio')
 function_module=ast.Module(body=[fn],type_ignores=[])
 def failed(stage,message):raise RuntimeError(stage+': '+str(message))
 with tempfile.TemporaryDirectory() as tmp:
  root=Path(tmp);mount=root/'kaggle/input/competitions/dataverse-detecting-emotions-from-hindi-speech'
  ns={'Path':lambda p:root/str(p).lstrip('/'),'fail':failed}
  exec(compile(function_module,str(RUN),'exec'),ns)
  resolver=ns['locate_audio'];rows=[{'filename':'audio_000001.wav'},{'filename':'audio_001035.wav'}]
  # The Kaggle competition_source directory is one level BELOW competitions.
  first=mount/'train';first.mkdir(parents=True)
  for row in rows:(first/row['filename']).touch()
  assert resolver(rows)==first,'Standard Kaggle competition train path broken'
  for row in rows:(first/row['filename']).unlink()
  # Allow organizer-added directories, but never use test-only files.
  nested=mount/'dataset/raw/train';nested.mkdir(parents=True)
  for row in rows:(nested/row['filename']).touch()
  assert resolver(rows)==nested,'Extra train nesting recovery broken'
  for row in rows:(nested/row['filename']).unlink()
  test=mount/'test';test.mkdir(parents=True)
  for row in rows:(test/row['filename']).touch()
  try:resolver(rows)
  except RuntimeError as e:assert str(e).startswith('MOUNT:'),str(e)
  else:raise AssertionError('Invalid test-only data accepted')
 print('MOUNT_DISCOVERY_REGRESSION_PASS: standard, nested, test-only rejected')
if __name__=='__main__':main()
