# adiff - Advanced XML Comparison CLI Tool

## Overview

`adiff` is a Python-based command-line tool that compares one or more XML files against a main reference XML file. It highlights differences, supports filtering, and can generate well-formatted Excel reports for analysis.

## Features

* Compare one or more XML files against a reference XML
* Detect missing or extra tags/attributes
* Filter by tag label (e.g., CAMERA, SENSOR, etc.)
* Output console-friendly tabulated results
* Export to Excel with color-coded formatting
* Options to show only differences for large datasets

---

## Prerequisites

### On Ubuntu/Debian Systems:

```bash
sudo apt update
sudo apt install python3 python3-pip

```

## Installation via pip


```bash
pip install adiff
```
---

## Usage Examples

### 1. Basic Comparison

```bash
adiff main-update.xml *.xml
```

Compare all XML files in the current directory against `main-update.xml`.

### 2. Compare Specific Files

```bash
adiff main-update.xml file1.xml file2.xml file3.xml
```

### 3. Show Only Differences

```bash
adiff main-update.xml *.xml --differences-only
```

### 4. Filter by Label

```bash
adiff main-update.xml *.xml --filter-label "CAMERA"
```

### 5. Excel Output

```bash
adiff main-update.xml *.xml --excel comparison_results.xlsx
```

Generates a colorful Excel file with formatted comparison results.

### 6. Excel Output - Differences Only

```bash
adiff main-update.xml *.xml --excel differences.xlsx --differences-only
```

---
