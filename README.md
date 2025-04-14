# Host Header Fuzzer

Host Header Fuzzer is a Python-based tool that leverages [ffuf](https://github.com/ffuf/ffuf) to fuzz HTTP Host headers for security testing. It supports static wordlists and subdomain enumeration, enabling you to identify potential vulnerabilities and misconfigurations.

## Features

- **Automated Fuzzing**: Uses `ffuf` to fuzz target URLs with custom Host headers.
- **Static Wordlist Support**: Fuzz with a predefined static wordlist.
- **Subdomain Discovery**: Enumerate subdomains with wordlist-based fuzzing.
- **Customizable Options**: Supports user-defined wordlists, match codes, and ffuf options.
- **Result Consolidation**: Merges multiple fuzzing results into a single JSON file.
- **Error Handling**: Gracefully handles issues with wordlist downloads, ffuf execution, and result parsing.

## Requirements

- Python 3.7+
- [ffuf](https://github.com/ffuf/ffuf) installed and available in PATH
- `requests` Python library (install with `pip install requests`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/host-header-fuzzer.git
   cd host-header-fuzzer
   ```

2. Install Python dependencies:
   ```bash
   pip install requests
   ```

3. Ensure `ffuf` is installed and accessible:
   ```bash
   sudo apt install ffuf
   ```

## Usage

```bash
python host_header_fuzzer.py -u <TARGET_URL> [OPTIONS]
```

### Arguments

| Option                  | Description                                                                                       | Default                                |
|-------------------------|---------------------------------------------------------------------------------------------------|----------------------------------------|
| `-u, --url`             | **Required.** Target URL for fuzzing.                                                            | N/A                                    |
| `-sw, --static-wordlist`| Path to static wordlist file for Host header fuzzing.                                             | Downloaded automatically if not set.   |
| `-dw, --subdomain-wordlist` | Path to subdomain wordlist file for subdomain fuzzing.                                         | None                                   |
| `-mc, --match-codes`    | HTTP status codes to match. Comma-separated values.                                               | `200,204,301,302,307,308,401,403,405,500` |
| `-o, --output`          | Output file path (without extension) to save results.                                            | None                                   |
| `--ffuf-path`           | Path to the `ffuf` binary.                                                                       | `ffuf`                                 |
| `--ffuf-options`        | Additional options to pass to `ffuf`.                                                            | None                                   |
| `-v, --verbose`         | Enable debug logging for more detailed output.                                                   | Disabled                               |

### Example Commands

1. **Basic Fuzzing**:
   ```bash
   python host_header_fuzzer.py -u https://example.com
   ```

2. **Using a Static Wordlist**:
   ```bash
   python host_header_fuzzer.py -u https://example.com -sw /path/to/static_wordlist.txt
   ```

3. **Subdomain Enumeration**:
   ```bash
   python host_header_fuzzer.py -u https://example.com -dw /path/to/subdomain_wordlist.txt
   ```

4. **Custom Match Codes**:
   ```bash
   python host_header_fuzzer.py -u https://example.com -mc 200,404
   ```

5. **Save Results to File**:
   ```bash
   python host_header_fuzzer.py -u https://example.com -o results
   ```

6. **Verbose Debugging**:
   ```bash
   python host_header_fuzzer.py -u https://example.com -v
   ```

## Output

- Results are consolidated into a single JSON file (e.g., `results_final.json`).
- Each result contains the response status code, content length, and the Host header used.

## Wordlist Download

If no static wordlist is provided, the script will automatically download the default wordlist from:
[Virtual-host-wordlist](https://raw.githubusercontent.com/cujanovic/Virtual-host-wordlist/master/virtual-host-wordlist.txt).

The downloaded file will be saved as `static_wordlist_cleaned.txt` in the script directory.

## Error Handling

- **Missing `ffuf`**: The script exits if `ffuf` is not installed or accessible.
- **Wordlist Download Issues**: The script logs an error if the default wordlist cannot be downloaded.
- **Invalid URLs**: The script validates URLs to ensure proper formatting.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This tool is intended for authorized security testing only. Misuse of this tool may result in legal consequences. Ensure you have proper authorization before using it.


