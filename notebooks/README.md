# Google Colab starter

The tested Python modules live in src/orion so Colab and the dashboard can reuse the same functions.

In a Colab notebook, run:

```python
!git clone https://github.com/zakir-si/ORION-Quant.git
%cd ORION-Quant
!pip install -e .
!pip install -r requirements-dev.txt
!python -m pytest -q
```

Begin with synthetic demo prices. Do not add brokerage passwords or real-money order code to notebooks.
