from loader import load_all_excel_files

datasets = load_all_excel_files()

companies = datasets["companies"]

valid_ids = set(companies["id"].astype(str).str.strip())

print(f"Companies IDs: {len(valid_ids)}")

for name, df in datasets.items():

    if name == "companies":
        continue

    if "company_id" not in df.columns:
        continue

    ids = set(df["company_id"].astype(str).str.strip())

    invalid = ids - valid_ids

    print("\n----------------------------")
    print(name)
    print("Unique company IDs :", len(ids))
    print("Invalid IDs :", len(invalid))

    if invalid:
        print("First 10 invalid IDs:")
        print(sorted(list(invalid))[:10])