#!/usr/bin/env python3
"""Validate explicit SMILES, calculate local descriptors, and render structures."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="JSON structure manifest")
    parser.add_argument("--out", required=True, type=Path, help="New output directory")
    args = parser.parse_args()
    try:
        args.out.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        print(json.dumps({"status": "error", "error": "output_directory_unavailable",
                          "detail": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    result = {"status": "error", "input_sha256": None, "rdkit_version": None,
              "basis": "Calculated from supplied structures; not experimental measurements.",
              "drawing_scope": "Rendered from SMILES; consistency with a user's drawing requires review.",
              "normalization": "Canonical atom ordering only; no salt, tautomer, charge or stereo standardization.",
              "structures": [], "errors": []}
    try:
        raw = args.input.read_bytes()
        result["input_sha256"] = hashlib.sha256(raw).hexdigest()
        entries = json.loads(raw)["structures"]
        if not isinstance(entries, list) or not 1 <= len(entries) <= 4:
            raise ValueError("structures must contain one target and zero to three byproducts")
        ids = set()
        for item in entries:
            if not isinstance(item, dict):
                raise ValueError("each structure must be an object")
            ident = item.get("id")
            if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", ident):
                raise ValueError("id must be 1-64 safe ASCII letters, digits, underscores or hyphens")
            if ident.casefold() in ids:
                raise ValueError("duplicate id: " + ident)
            ids.add(ident.casefold())
            if item.get("role") not in ("target", "byproduct"):
                raise ValueError("role must be target or byproduct")
            if not isinstance(item.get("smiles"), str) or not item["smiles"].strip():
                raise ValueError("smiles must be a nonempty string")
        if sum(x["role"] == "target" for x in entries) != 1:
            raise ValueError("exactly one target is required")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result["errors"].append({"code": "invalid_input", "detail": str(exc)})
        return finish(result, args.out, 2)
    try:
        from rdkit import Chem, rdBase
        from rdkit.Chem import rdMolDescriptors
        from rdkit.Chem.Draw import rdMolDraw2D
    except ImportError as exc:
        result["errors"].append({"code": "missing_dependency", "detail": "RDKit unavailable: " + str(exc),
                                 "action": "Use an existing RDKit Python environment; nothing was installed."})
        return finish(result, args.out, 3)
    result["rdkit_version"] = rdBase.rdkitVersion
    for item in entries:
        record = {"id": item["id"], "role": item["role"], "supplied_smiles": item["smiles"],
                  "status": "error", "artifacts": {}}
        result["structures"].append(record)
        try:
            params = Chem.SmilesParserParams()
            params.parseName = False
            mol = Chem.MolFromSmiles(item["smiles"], params)
            if mol is None or mol.GetNumAtoms() == 0:
                raise ValueError("SMILES could not be parsed and sanitized")
            if any(atom.GetAtomicNum() == 0 or atom.HasQuery() for atom in mol.GetAtoms()):
                raise ValueError("Wildcard or query atoms do not define a confirmed molecular structure")
            stereo = [{"type": str(s.type), "centered_on": int(s.centeredOn),
                       "specified": str(s.specified), "descriptor": str(s.descriptor)}
                      for s in Chem.FindPotentialStereo(mol)]
            record.update({"canonical_isomeric_smiles": Chem.MolToSmiles(mol, isomericSmiles=True),
                           "formula": rdMolDescriptors.CalcMolFormula(mol),
                           "net_charge": Chem.GetFormalCharge(mol),
                           "exact_mass_da_calculated": rdMolDescriptors.CalcExactMolWt(mol),
                           "fragment_formulas": [rdMolDescriptors.CalcMolFormula(m)
                               for m in Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True)],
                           "potential_stereochemistry": stereo,
                           "unspecified_stereochemistry": [s for s in stereo if s["specified"] != "Specified"]})
            for extension, drawer in (("svg", rdMolDraw2D.MolDraw2DSVG(560, 420)),
                                      ("png", rdMolDraw2D.MolDraw2DCairo(560, 420))):
                drawer.DrawMolecule(mol, legend=item["id"])
                drawer.FinishDrawing()
                artifact = args.out / (item["id"] + "." + extension)
                content = drawer.GetDrawingText()
                artifact.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
                record["artifacts"][extension] = str(artifact.resolve())
            record["status"] = "ok"
        except Exception as exc:
            record["error"] = {"code": "structure_or_render_failed", "detail": str(exc)}
    failed = any(x["status"] != "ok" for x in result["structures"])
    result["status"] = "partial_failure" if failed else "ok"
    return finish(result, args.out, 1 if failed else 0)


def finish(result, out, code):
    target = out / "results.json"
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "results": str(target.resolve())}, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main())
