from loader import load_all_excel_files

datasets = load_all_excel_files()

companies = datasets["companies"]

print(companies[["id", "company_name"]].head(20))

print("\n")

print(companies["id"].tolist()[:20])