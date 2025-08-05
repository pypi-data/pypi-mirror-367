# SUSTech Work Record Generator (sustech-rawr)

A Python tool that automatically generates work record tables for Southern University of Science and Technology (SUSTech), with intelligent holiday detection and standard Excel format output.

## Features

- 🎯 **Automatic Excel Generation**: Creates work record tables in standard format
- 📅 **Smart Holiday Detection**: Automatically identifies Chinese public holidays, weekends, and compensatory work days
- ⚡ **Concurrent Processing**: Uses multi-threading for fast holiday data retrieval
- 🎨 **Professional Formatting**: Includes standard fonts, borders, alignment, and cell merging
- 💻 **Command Line Interface**: Simple and easy-to-use CLI tool

## Usage

### Command Line Usage

```bash
uvx sustech-rawr -n "张三" -w "数据库" -y 2025 -m 8
```
![image-20250805140600427](https://my-img-typora.oss-cn-chengdu.aliyuncs.com/img/image-20250805140600427.png)


### Parameters

| Parameter | Short | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| `--name` | `-n` | ✅ | None | Visitor name |
| `--work` | `-w` | ✅ | None | Work content description |
| `--year` | `-y` | ✅ | 2025 | Year |
| `--month` | `-m` | ✅ | 7 | Month |
| `--time` | `-t` | ❌ | 9:00-18:00 | Working hours |
| `--output` | `-o` | ❌ | {name}_{year}_{month}.xlsx | Output filename |

## Output File Format

The generated Excel file contains:

- **Title**: Work Record Table
- **Headers**: Date, Visitor Name, Working Hours (Daily Sign), Work Content, Visitor Confirmation (Daily Sign), Teacher Confirmation Signature
- **Data Rows**:
  - Working days: Shows specific work information
  - Holidays: Automatically filled with "/"
- **Formatting**: Professional fonts, borders, alignment, and cell merging

## Project Structure

```
sustechRAWR/
├── src/
│   └── sustechra_record/
│       ├── __init__.py
│       └── main.py          # Main program file
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
└── README.md               # Project documentation
```

## Dependencies

- **get-holiday-cn**: Chinese holiday query library
- **openpyxl**: Excel file manipulation
- **requests**: HTTP request library

## Development

### Local Development Environment Setup

```bash
# Clone the project
git clone https://github.com/huanglune/sustechRAWR.git
cd sustechRAWR

# sync the requirments
uv sync

uv run src/sustech_rawr/main.py -n ...
```

### Code Structure

Main functional modules:

- `main()`: Core business logic, handles date and holiday data
- `draw_excel()`: Excel file generation and formatting
- `run()`: Command line interface handling

## Key Features

### 1. Smart Holiday Detection
- Automatically identifies statutory holidays
- Recognizes weekends
- Handles compensatory work days

### 2. Concurrent Optimization
- Uses thread pool for concurrent holiday data retrieval
- Improves processing speed for longer months (31 days)

### 3. Professional Formatting
- Complies with official document requirements
- Automatically adjusts column widths and row heights
- Standard Chinese font settings

## License

This project uses a standard open source license.

## Contributing

Issues and Pull Requests are welcome to improve this project!

---

**Note**: This tool is specifically designed for SUSTech work record tables, and the generated table format meets the relevant requirements.