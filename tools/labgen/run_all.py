import runpy, os
d = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, d)
for b in ['batch1', 'batch2']:
    runpy.run_path(os.path.join(d, b + '.py'))
import forms
# batch3 modifies forms.S in the same interpreter
exec(open(os.path.join(d, 'batch3.py'), encoding='utf-8').read(), {'__name__': 'b3', '__file__': os.path.join(d, 'batch3.py')})
# batch4 тоже правит forms.S
exec(open(os.path.join(d, 'batch4.py'), encoding='utf-8').read(), {'__name__': 'b4', '__file__': os.path.join(d, 'batch4.py')})
# batch5 тоже правит forms.S (после batch4)
exec(open(os.path.join(d, 'batch5.py'), encoding='utf-8').read(), {'__name__': 'b5', '__file__': os.path.join(d, 'batch5.py')})
# batch6 тоже правит forms.S
exec(open(os.path.join(d, 'batch6.py'), encoding='utf-8').read(), {'__name__': 'b6', '__file__': os.path.join(d, 'batch6.py')})
forms.write_forms()
runpy.run_path(os.path.join(d, 'build_data_module.py'))
print('ALL OK')
