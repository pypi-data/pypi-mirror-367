import argparse
import json
import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        description="Convert Synapse JSON (RTP format) to spreadsheet format (.xlsx)"
    )
    parser.add_argument(
        "input", nargs="?", default="metadata.json",
        help="Path to the input JSON file (default: metadata.json)"
    )
    parser.add_argument(
        "output", nargs="?", default="synapse_library.xlsx",
        help="Path to the output Excel file (default: synapse_library.xlsx)"
    )

    args = parser.parse_args()

    try:
        with open(args.input, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {args.input}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
        return

    try:
        collection = data["Collection"]["name"]
        designator = data["Collection"].get("designator", "")
        collection_url = data["Collection"].get("url", "")

        rows = []
        for category in data["Collection"]["Categories"]:
            for item in category["items"]:
                rows.append({
                    "collection": collection,
                    "category": category["name"],
                    "designator": designator,
                    "collection_url": collection_url,
                    **item
                })

        df = pd.DataFrame(rows)
        df.to_excel(args.output, index=False)
        print(f"✅ Downconverted {args.input} to {args.output}")
    except KeyError as e:
        print(f"❌ Missing expected key in JSON structure: {e}")


if __name__ == "__main__":
    main()
