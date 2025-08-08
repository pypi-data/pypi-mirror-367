# Oresme Jax

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15874178.svg)](https://doi.org/10.5281/zenodo.15874178)

[![WorkflowHub DOI](https://img.shields.io/badge/DOI-10.48546/WORKFLOWHUB.DATAFILE.19.1-blue)](https://doi.org/10.48546/WORKFLOWHUB.DATAFILE.19.1)

[![figshare DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.29554532-blue)](https://doi.org/10.6084/m9.figshare.29554532)

[![ResearchGate DOI](https://img.shields.io/badge/DOI-10.13140/RG.2.2.30518.41284-blue)](https://doi.org/10.13140/RG.2.2.30518.41284)

[![Anaconda-Server Badge](https://anaconda.org/bilgi/oresmej/badges/version.svg)](https://anaconda.org/bilgi/oresmej)
[![Anaconda-Server Badge](https://anaconda.org/bilgi/oresmej/badges/latest_release_date.svg)](https://anaconda.org/bilgi/oresmej)
[![Anaconda-Server Badge](https://anaconda.org/bilgi/oresmej/badges/platforms.svg)](https://anaconda.org/bilgi/oresmej)
[![Anaconda-Server Badge](https://anaconda.org/bilgi/oresmej/badges/license.svg)](https://anaconda.org/bilgi/oresmej)
[![Open Source](https://img.shields.io/badge/Open%20Source-Open%20Source-brightgreen.svg)](https://opensource.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python CI](https://github.com/WhiteSymmetry/oresmej/actions/workflows/python_ci.yml/badge.svg?branch=main)](https://github.com/WhiteSymmetry/oresmej/actions/workflows/python_ci.yml)
[![codecov](https://codecov.io/gh/WhiteSymmetry/oresmej/graph/badge.svg?token=T9XPI1HSKF)](https://codecov.io/gh/WhiteSymmetry/oresmej)
[![Documentation Status](https://readthedocs.org/projects/oresmej/badge/?version=latest)](https://oresmej.readthedocs.io/en/latest/)
[![Binder](https://terrarium.evidencepub.io/badge_logo.svg)](https://terrarium.evidencepub.io/v2/gh/WhiteSymmetry/oresmej/HEAD)
[![PyPI version](https://badge.fury.io/py/oresmej.svg)](https://badge.fury.io/py/oresmej)
[![PyPI Downloads](https://static.pepy.tech/badge/oresmej)](https://pepy.tech/projects/oresmej)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md) 
[![Linted with Ruff](https://img.shields.io/badge/Linted%20with-Ruff-green?logo=python&logoColor=white)](https://github.com/astral-sh/ruff)

---

<p align="left">
    <table>
        <tr>
            <td style="text-align: center;">PyPI</td>
            <td style="text-align: center;">
                <a href="https://pypi.org/project/oresmej/">
                    <img src="https://badge.fury.io/py/oresmej.svg" alt="PyPI version" height="18"/>
                </a>
            </td>
        </tr>
        <tr>
            <td style="text-align: center;">Conda</td>
            <td style="text-align: center;">
                <a href="https://anaconda.org/bilgi/oresmej">
                    <img src="https://anaconda.org/bilgi/oresmej/badges/version.svg" alt="conda-forge version" height="18"/>
                </a>
            </td>
        </tr>
        <tr>
            <td style="text-align: center;">DOI</td>
            <td style="text-align: center;">
                <a href="https://doi.org/10.5281/zenodo.15874178">
                    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.15874178.svg" alt="DOI" height="18"/>
                </a>
            </td>
        </tr>
        <tr>
            <td style="text-align: center;">License: MIT</td>
            <td style="text-align: center;">
                <a href="https://opensource.org/licenses/MIT">
                    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License" height="18"/>
                </a>
            </td>
        </tr>
    </table>
</p>

---


Oresme numbers refer to the sums related to the harmonic series.

---
### **Türkçe Tanım:**
**Oresme Sayıları**, 14. yüzyılda Nicole Oresme tarafından incelenen matematiksel serilerdir. Oresme sayıları harmonik seriye ait toplamları ifade eder. İki türü vardır:  
1. **\( \frac{n}{2^n} \) serisi** (Oresme'nin orijinal çalışması),  
2. **Harmonik sayılar** (\( H_n = 1 + \frac{1}{2} + \cdots + \frac{1}{n} \)).  
Bu sayılar, analiz ve sayı teorisinde önemli rol oynar.

---

### **English Definition:**
**Oresme Numbers** are mathematical series studied by Nicole Oresme in the 14th century. Oresme numbers refer to the sums related to the harmonic series. They include two types:  
1. The **\( \frac{n}{2^n} \) sequence** (Oresme's original work),  
2. **Harmonic numbers** (\( H_n = 1 + \frac{1}{2} + \cdots + \frac{1}{n} \)).  
These numbers play a key role in analysis and number theory.

---

### **Fark/Karşılaştırma (Difference):**
- **Oresme'nin \( \frac{n}{2^n} \) serisi** ıraksaklık kanıtları için önemlidir.  
- **Harmonik sayılar** (\( H_n \)) ise logaritmik büyüme gösterir ve \( n \to \infty \) iken ıraksar.  
- Modern literatürde "Oresme numbers" terimi daha çok tarihsel bağlamda kullanılır.

---

## Kurulum (Türkçe) / Installation (English)

### Python ile Kurulum / Install with pip, conda, mamba
```bash
pip install oresmej -U
python -m pip install -U oresmej
conda install bilgi::oresmej -y
mamba install bilgi::oresmej -y
```

```diff
- pip uninstall Oresme -y
+ pip install -U oresmej
+ python -m pip install -U oresmej
```

[PyPI](https://pypi.org/project/Oresme/)

### Test Kurulumu / Test Installation

```bash
pip install -i https://test.pypi.org/simple/ oresmej -U
```

### Github Master Kurulumu / GitHub Master Installation

**Terminal:**

```bash
pip install git+https://github.com/WhiteSymmetry/oresmej.git
```

**Jupyter Lab, Notebook, Visual Studio Code:**

```python
!pip install git+https://github.com/WhiteSymmetry/oresmej.git
# or
%pip install git+https://github.com/WhiteSymmetry/oresmej.git
```

---

## Kullanım (Türkçe) / Usage (English)

```python
import oresmej as oj
import numpy as np
import jax
import jax.numpy as jnp
import time
from oresmej import *
import matplotlib.pyplot as plt

# Simple usage example
plt.figure(figsize=(10, 5))
plt.plot(oj.harmonic_numbers_jax(500))
plt.title("First 5000000 Harmonic Numbers")
plt.xlabel("n")
plt.ylabel("H(n)")
plt.show()
```

```python
import oresmej
oresmej.__version__
```

```python
import importlib
import inspect
import oresmej as oj  # Varsa import hatasını yakalamak için
import jax.numpy as jnp

def diagnose_module(module_name):
    try:
        # Modülü yükle
        module = importlib.import_module(module_name)
        
        print(f"\n{' Modül Tanılama Raporu ':=^80}")
        print(f"Modül adı: {module_name}")
        print(f"Modül dosya yolu: {inspect.getfile(module)}")
        
        # Modülün tüm özelliklerini listele
        print("\nModülde bulunan özellikler:")
        members = inspect.getmembers(module)
        public_members = [name for name, _ in members if not name.startswith('_')]
        print(public_members)
        
        # Özel olarak kontrol edilecek fonksiyonlar
        required_functions = [
            'oresme_sequence',
            'harmonic_numbers',
            'harmonic_number',
            'harmonic_number_jax',
            'harmonic_numbers_jax',
            'harmonic_generator_jax',
            'harmonic_number_approx'
        ]
        
        print("\nEksik olan fonksiyonlar:")
        missing = [fn for fn in required_functions if not hasattr(module, fn)]
        print(missing if missing else "Tüm gerekli fonksiyonlar mevcut")
        
        # __all__ değişkenini kontrol et
        print("\n__all__ değişkeni:")
        if hasattr(module, '__all__'):
            print(module.__all__)
        else:
            print("__all__ tanımlı değil (tüm public fonksiyonlar içe aktarılır)")
            
    except ImportError as e:
        print(f"\nHATA: Modül yüklenemedi - {e}")
    except Exception as e:
        print(f"\nBeklenmeyen hata: {e}")

# Tanılama çalıştır
diagnose_module('oresmej')

# Alternatif olarak doğrudan kontrol
print("\nDoğrudan fonksiyon varlığı kontrolü:")
try:
    print("harmonic_numbers_jax mevcut mu?", hasattr(oj, 'harmonic_numbers_jax'))
    if hasattr(oj, 'harmonic_numbers_jax'):
        print("Fonksiyon imzası:", inspect.signature(oj.harmonic_numbers_jax))
    else:
        print("Eksik fonksiyon: harmonic_numbers_jax")
except Exception as e:
    print("Kontrol sırasında hata:", e)
```

```python
# 1. Alternatif içe aktarma yöntemi
from oresmej import harmonic_numbers_jax  # Doğrudan import deneyin
import oresmej as oj
import jax.numpy as jnp

# 2. Modülü yeniden yükleme
import importlib
importlib.reload(oj)

# 3. Fonksiyonun alternatif isimle var olup olmadığını kontrol
print("Alternatif fonksiyon isimleri:", [name for name in dir(oj) if 'harmonic' in name.lower()])
```
---

### Development
```bash
# Clone the repository
git clone https://github.com/WhiteSymmetry/oresmej.git
cd oresmej

# Install in development mode
python -m pip install -ve . # Install package in development mode

# Run tests
pytest

Notebook, Jupyterlab, Colab, Visual Studio Code
!python -m pip install git+https://github.com/WhiteSymmetry/oresmej.git
```
---

## Citation

If this library was useful to you in your research, please cite us. Following the [GitHub citation standards](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/creating-a-repository-on-github/about-citation-files), here is the recommended citation.

### BibTeX


### APA

```
Keçeci, M. (2025). Dynamic vs Static Number Sequences: The Case of Keçeci and Oresme Numbers. Open Science Articles (OSAs), Zenodo. https://doi.org/10.5281/zenodo.15833351

Keçeci, M. (2025). oresmej [Data set]. ResearchGate. https://doi.org/10.13140/RG.2.2.30518.41284

Keçeci, M. (2025). oresmej [Data set]. figshare. https://doi.org/10.6084/m9.figshare.29554532

Keçeci, M. (2025). oresmej [Data set]. WorkflowHub. https://doi.org/10.48546/WORKFLOWHUB.DATAFILE.19.1

Keçeci, M. (2025). oresmej. Open Science Articles (OSAs), Zenodo. https://doi.org/10.5281/zenodo.15874178
```

### Chicago

```
Keçeci, Mehmet. Dynamic vs Static Number Sequences: The Case of Keçeci and Oresme Numbers. Open Science Articles (OSAs), Zenodo, 2025. https://doi.org/10.5281/zenodo.15833351

Keçeci, Mehmet. oresmej [Data set]. ResearchGate, 2025. https://doi.org/10.13140/RG.2.2.30518.41284

Keçeci, Mehmet (2025). oresmej [Data set]. figshare, 2025. https://doi.org/10.6084/m9.figshare.29554532

Keçeci, Mehmet. oresmej [Data set]. WorkflowHub, 2025. https://doi.org/10.48546/WORKFLOWHUB.DATAFILE.19.1

Keçeci, Mehmet. oresmej. Open Science Articles (OSAs), Zenodo, 2025. https://doi.org/10.5281/zenodo.15874178

```


### Lisans (Türkçe) / License (English)

```
This project is licensed under the MIT License.
```
