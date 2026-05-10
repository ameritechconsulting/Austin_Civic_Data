# Repository Maintenance Guide

*Simple Public Database Maintenance Guide — Austin Civic Data*
*Generated: May 2026*

---

## 1. Folder Structure

```
Austin_Civic_Data/
├── README.md
├── LICENSE
├── data/
├── analysis/
├── visuals/
├── reports/
├── scripts/
├── archive/
├── docs/
└── website/
```

## 2. Data Folder Structure

```
data/
├── raw/
├── cleaned/
└── processed/
```

## 3. File Naming Format

Use this format: `YYYY_MM_topic_description_version.ext`

**Examples:**
- `2026_05_vendor_data_raw.csv`
- `2026_05_contract_analysis_v1.xlsx`
- `2026_05_food_access_map.png`

## 4. README Structure

Every folder should contain a `README.md` file.

**Template:**
```markdown
# Folder Name

## Purpose
Short explanation here.

## Contents
- item 1
- item 2
- item 3

## Documentation
- ../docs/contact.md
- ../docs/methodology.md
```

## 5. Contact File

Master contact file is at: [docs/contact.md](contact.md)

## 6. Clickable Links in README Files

Website link: `[My Website](https://yourwebsite.com)`

Internal repository file: `[Methodology](../docs/methodology.md)`

GitHub automatically makes these clickable.

## 7. Monthly Maintenance Checklist

1. Backup current files into `archive/` folder
2. Add new datasets to project `data/raw/`
3. Clean datasets into project `data/cleaned/`
4. Update README dates
5. Check links inside README files
6. Review public statements for accuracy
7. Push updates to GitHub
8. Update changelog

## 8. Final Review Before Publishing

1. Open README previews in VSCode (`CMD + SHIFT + V`)
2. Test clickable links
3. Confirm folder names are consistent (lowercase_with_underscores)
4. Confirm filenames are standardized
5. Verify data sources are listed
6. Confirm methodology notes are updated
7. Push final updates to GitHub

## 9. AI Cleanup Prompt

```
You are helping me clean and organize a public civic data repository.

Tasks:
1. Rename files using lowercase_with_underscores
2. Organize files into folders
3. Check README files
4. Verify links work
5. Standardize documentation
6. Preserve raw data separately
7. Create GitHub-ready structure
8. Flag duplicate files
9. Keep wording professional and factual
10. Maintain consistency across the repository
```
