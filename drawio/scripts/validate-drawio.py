#!/usr/bin/env python3
import sys
import os
import xml.etree.ElementTree as ET

def validate_drawio(file_path):
    print(f"Validating: {file_path}")
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return False

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"ERROR: Invalid XML format: {e}")
        return False

    # Check root tag is mxfile or mxGraphModel
    if root.tag not in ("mxfile", "mxGraphModel"):
        print(f"ERROR: Root tag must be <mxfile> or <mxGraphModel>, got <{root.tag}>")
        return False

    diagrams = []
    if root.tag == "mxfile":
        diagrams = root.findall(".//diagram")
        if not diagrams:
            print("ERROR: <mxfile> must contain at least one <diagram> element")
            return False
    else:
        # If it's just an mxGraphModel (some exports/snippets)
        diagrams = [root]

    success = True

    for idx, diag in enumerate(diagrams):
        name = diag.get("name", f"Index {idx}")
        diag_id = diag.get("id", "unknown-id")
        print(f"  Checking diagram '{name}' (id: {diag_id})...")

        # Find mxGraphModel inside diagram
        model = diag.find(".//mxGraphModel")
        if model is None and diag.tag == "mxGraphModel":
            model = diag
        elif model is None:
            # Check if compressed/base64 (if diagram is not empty but has text content)
            if diag.text and diag.text.strip():
                print("  WARNING: Diagram data is compressed or Base64 encoded. Cannot validate internal rules.")
                continue
            print("  ERROR: <diagram> does not contain an <mxGraphModel> element")
            success = False
            continue

        # Check root cell elements
        cell_root = model.find("root")
        if cell_root is None:
            print("  ERROR: <mxGraphModel> must contain a <root> element")
            success = False
            continue

        cells = cell_root.findall("mxCell")
        if not cells:
            print("  ERROR: <root> has no <mxCell> elements")
            success = False
            continue

        # Check rule 1: id 0 and 1
        ids = [cell.get("id") for cell in cells]
        if "0" not in ids:
            print("  ERROR: Root cell with id=\"0\" is missing")
            success = False
        if "1" not in ids:
            print("  ERROR: Root cell with id=\"1\" is missing")
            success = False

        # Check rule 2: Unique IDs
        seen_ids = set()
        duplicate_ids = set()
        for cid in ids:
            if cid is not None:
                if cid in seen_ids:
                    duplicate_ids.add(cid)
                seen_ids.add(cid)
        if duplicate_ids:
            print(f"  ERROR: Duplicate cell IDs found: {sorted(list(duplicate_ids))}")
            success = False

        # Gather vertices and check edges
        valid_vertex_ids = set(seen_ids)
        for cell in cells:
            cid = cell.get("id")
            value = cell.get("value", "")
            style = cell.get("style", "")
            is_vertex = cell.get("vertex") == "1"
            is_edge = cell.get("edge") == "1"

            # Check duplicate style keys
            if style:
                keys = []
                for part in style.split(";"):
                    part = part.strip()
                    if part and "=" in part:
                        keys.append(part.split("=")[0].strip())
                    elif part:
                        keys.append(part.strip())
                seen_keys = set()
                dups = set()
                for k in keys:
                    if k in seen_keys:
                        dups.add(k)
                    seen_keys.add(k)
                if dups:
                    print(f"  WARNING: Cell id=\"{cid}\" has duplicate style keys: {list(dups)} in style: \"{style}\"")

            if is_edge:
                # Check rule 6: Connected source and target
                source = cell.get("source")
                target = cell.get("target")
                if not source:
                    print(f"  WARNING: Edge id=\"{cid}\" (value=\"{value}\") has no source attribute")
                elif source not in valid_vertex_ids:
                    print(f"  ERROR: Edge id=\"{cid}\" references non-existent source ID \"{source}\"")
                    success = False
                
                if not target:
                    print(f"  WARNING: Edge id=\"{cid}\" (value=\"{value}\") has no target attribute")
                elif target not in valid_vertex_ids:
                    print(f"  ERROR: Edge id=\"{cid}\" references non-existent target ID \"{target}\"")
                    success = False

                # Check rule 7: Expanded form with mxGeometry child
                geom = cell.find("mxGeometry")
                if geom is None:
                    print(f"  ERROR: Edge id=\"{cid}\" must have an <mxGeometry> child element (cannot be self-closing)")
                    success = False

                # Check edge labels have labelBackgroundColor=none
                if value and value.strip():
                    if "labelBackgroundColor=" not in style:
                        print(f"  WARNING: Labeled edge id=\"{cid}\" (value=\"{value}\") is missing labelBackgroundColor=none")
                    elif "labelBackgroundColor=none" not in style:
                        print(f"  WARNING: Labeled edge id=\"{cid}\" (value=\"{value}\") style does not set labelBackgroundColor to 'none'")

            # Check relative positioning of container children
            parent = cell.get("parent")
            if parent and parent not in ("0", "1") and parent in valid_vertex_ids:
                geom = cell.find("mxGeometry")
                if geom is not None:
                    x = geom.get("x")
                    y = geom.get("y")
                    # If child has very large absolute coordinates, warn about relative positioning
                    try:
                        x_val = float(x) if x else 0
                        y_val = float(y) if y else 0
                        if x_val > 1500 or y_val > 1500:
                            print(f"  WARNING: Child cell id=\"{cid}\" (parent=\"{parent}\") has coordinates ({x_val}, {y_val}) which seem too large for container-relative position.")
                    except ValueError:
                        pass

    if success:
        print("  SUCCESS: Basic validation passed.")
    else:
        print("  FAILED: Validation failed.")
    return success

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate-drawio.py <file1.drawio> [file2.drawio ...]")
        sys.exit(1)

    all_ok = True
    for arg in sys.argv[1:]:
        ok = validate_drawio(arg)
        if not ok:
            all_ok = False

    sys.exit(0 if all_ok else 1)
