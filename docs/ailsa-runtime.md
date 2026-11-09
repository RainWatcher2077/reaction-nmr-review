# 配置 AILSA 运行环境

`ailsa-nmr` 是 Codex 技能。它调用独立安装的 [AILSA](https://github.com/steinbeck/ailsa) CLI。下列步骤为 macOS 或 Linux 配置用户目录中的运行环境，需要 Git、[uv](https://docs.astral.sh/uv/getting-started/installation/)、curl、tar、make 和 C 编译器。macOS 可使用 Xcode Command Line Tools 提供的编译器。

已有能用的 AILSA 包装器时，直接验证并使用其绝对路径。也可将 `AILSA_HOME` 设为已有源码目录（其中含 `.venv/bin/ailsa` 和 `.venv/bin/python`），用 `LSD_BIN_DIR` 指向包含 `lsd` 和 `outlsd` 的目录，并用 `LUCY_DATABASE` 指向已有的 SQLite `.db` 文件。使用绝对路径。

## 1. 安装 CLI 和预测依赖

以下命令适用于新目录。若目录已有 AILSA，先验证并复用已有安装。

```sh
export AILSA_HOME="${AILSA_HOME:-$HOME/.local/share/reaction-nmr-review/ailsa}"
(
  set -eu
  if [ -e "$AILSA_HOME" ]; then
    printf 'AILSA_HOME already exists: %s\n' "$AILSA_HOME" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$AILSA_HOME")"
  git init -q "$AILSA_HOME"
  cd "$AILSA_HOME"
  git fetch --depth 1 https://github.com/steinbeck/ailsa.git 0557c37097d5ed95674e81e80b9a2cdfb3e30a63
  git checkout --detach FETCH_HEAD
  uv sync --locked --python 3.12 --no-dev --inexact
  uv pip install --python .venv/bin/python --no-deps \
    'git+https://github.com/Ratsemaat/HOSE_code_generator.git@e4ae6c9a103e29e49d678d3bd7d73190274e11ee'
)
```

HOSE 生成器的 `--no-deps` 跳过其旧测试依赖。RDKit 已由 AILSA 的环境提供。若只在 Python 依赖阶段中断，进入已检出的源码目录重试两条 `uv` 命令即可。

## 2. 配置 LSD 求解器

需要运行 CASE 求解时，使用已有的 LSD 和 outlsd，或按以下步骤构建官方 LSD 3.5.3。两者的可执行文件都会生成在解压目录中。

```sh
(
  set -eu
  mkdir -p "$AILSA_HOME/.local"
  cd "$AILSA_HOME/.local"
  curl -fsSL https://nuzillard.github.io/LSD/LSD-3.5.3.tar.gz -o LSD-3.5.3.tar.gz
  checksum='31cb9a11224f70487eae12f0e5fb062b081a939f38f4c21f35b1ef7ba3d26223'
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s  LSD-3.5.3.tar.gz\n' "$checksum" | sha256sum -c -
  else
    printf '%s  LSD-3.5.3.tar.gz\n' "$checksum" | shasum -a 256 -c -
  fi
  tar -xzf LSD-3.5.3.tar.gz
  cd LSD-3.5.3
  sh install.sh
  test -x lsd && test -x outlsd
)
```

## 3. 配置数据库并验收

从本仓库根目录执行。也可将 `AILSA` 设为已安装的 `ailsa-nmr` 技能内 `scripts/ailsa` 的绝对路径。下载前检查是否已有可复用的数据库。官方 [Figshare v3](https://doi.org/10.6084/m9.figshare.31073554.v3) 下载约 830 MB，解压后约 2.8 GB。

```sh
AILSA="$PWD/skills/ailsa-nmr/scripts/ailsa"
export AILSA_HOME="${AILSA_HOME:-$HOME/.local/share/reaction-nmr-review/ailsa}"
export LUCY_DATABASE="${LUCY_DATABASE:-$AILSA_HOME/data/reference/ailsa-derep.db}"
if [ ! -f "$LUCY_DATABASE" ]; then
  "$AILSA" database download -o "$LUCY_DATABASE"
fi
"$AILSA" --version
"$AILSA_HOME/.venv/bin/python" -c 'import rdkit; print(rdkit.__version__)'
"$AILSA" lsd check
"$AILSA" database info "$LUCY_DATABASE"
"$AILSA" predict c13 CCO --db "$LUCY_DATABASE" --format json
"$AILSA" detect hybridisation 130.5 --db "$LUCY_DATABASE" --format json
```

- 求解需要 `lsd check` 同时报告 `LSD: available` 与 `outlsd: available`。
- 官方 v3 数据库显示 schema 3、928,443 个化合物。预测冒烟测试应为乙醇的两个碳返回两条预测。
- 检测结果 `has_data: false` 代表统计先验不可用。记录为受限 CASE，保留基于实验约束的推理。
- 固定版本的 `lsd rank --spectrum` 有已知读峰问题。对经复核的实验峰列表使用 `lsd rank solutions.smi --shifts '180.5,140.8,137.0,129.4'`，将示例数值替换为实际测量值。

AILSA 由 Christoph Steinbeck 开发并采用 MIT 许可。LSD 由 Jean-Marc Nuzillard 开发，研究使用请按上游说明引用。Figshare 数据库采用 CC BY 4.0。[AILSA 安装与引用说明](https://github.com/steinbeck/ailsa/blob/0557c37097d5ed95674e81e80b9a2cdfb3e30a63/README.md#installation) · [LSD 官网](https://nuzillard.github.io/LSD/) · [HOSE 生成器](https://github.com/Ratsemaat/HOSE_code_generator)
