# SpaMosaic

**SpaMosaic** is a Python package for spatial multi-omics data integration using contrastive learning and graph neural networks. It supports integration of partially overlapping modalities and facilitates downstream analyses such as spatial domain identification and modality imputation.

---

## 🔧 Features

- **Horizontal integration**: integrates multiple slices within a single modality
- **Vertical integration**: integrates multiple modalities measured from the same slice
- **Mosaic integration**: integrates multiple slices with overallping modalities 
- **Imputation**: imputes expression profiles of missing omics

---

## 🚀 Installation

### Required Dependencies

SpaMosaic requires external installation of the following packages (not installed automatically):

- PyTorch (version ≥ 2.0)
- PyTorch Geometric (torch-scatter, torch-sparse, etc.)
- harmony-pytorch (version ≥ 0.1.7)

Once these dependencies are installed, simply run:

```bash
pip install spamosaic
```

> ⚠️ Note 
Both CPU and GPU versions of PyTorch and PyTorch Geometric are compatible with SpaMosaic.

## 📚 Documentation
📖 Full tutorials and API reference:
👉 https://spamosaic.readthedocs.io

## 📄 License
SpaMosaic is released under the MIT License.
© 2025 Jinmiao Lab