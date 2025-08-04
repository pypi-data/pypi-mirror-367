# pickle_com

A drop-in replacement for Python's pickle module, automatically patching legacy numpy attributes and inspect.getargspec for compatibility with old pickle files.

## Usage

```python
import pickle_com as pickle
data = pickle.load(open('file.pkl', 'rb'))
