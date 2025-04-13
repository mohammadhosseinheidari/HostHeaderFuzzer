# Host Header Fuzzer

An advanced Python-based script for performing **Host Header Fuzzing** using the `ffuf` tool. This script filters for HTTP 200 OK responses and ensures efficiency by avoiding redundant downloads of the wordlist. It also supports merging custom subdomains into the fuzzing process. 

## Features

- **Automated Wordlist Management**: Downloads a default wordlist or uses a custom one.
- **Dynamic Wordlist Cleaning**: Cleans and combines wordlists to avoid redundant entries.
- **Subdomain Support**: Integrates subdomains from a user-provided file into the fuzzing process.
- **HTTP 200 Filtering**: Filters results to display only valid HTTP 200 responses.
- **Customizable User-Agent**: Uses a realistic User-Agent for HTTP requests.
- **Ease of Use**: Simple CLI interface for straightforward execution.

## Requirements

- Python 3.6+
- `ffuf` (fuzzing tool) installed and available in the system's PATH
- `wget` (for downloading wordlists)
- Required Python libraries: `argparse`, `os`, `re`, `subprocess`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/host-header-fuzzer.git
   cd host-header-fuzzer
   ```

2. Ensure `ffuf` is installed:
   ```bash
   sudo apt install ffuf
   ```

3. (Optional) Install `wget` if not already available:
   ```bash
   sudo apt install wget
   ```

4. Make the script executable:
   ```bash
   chmod +x host_header_fuzzer.py
   ```

## Usage

Run the script from the command line with the following options:

```bash
python3 host_header_fuzzer.py <target_url> [--wordlist <wordlist_url>] [--subdomains <subdomains_file>]
```

### Positional Arguments:

- **`target_url`**: The target URL for fuzzing (e.g., `https://example.com`).

### Optional Arguments:

- **`--wordlist`**: URL of the main wordlist file. Defaults to the following:
  ```
  https://raw.githubusercontent.com/cujanovic/Virtual-host-wordlist/master/virtual-host-wordlist.txt
  ```
- **`--subdomains`**: Path to a file containing a list of subdomains (one per line). 

### Example Commands

1. **Basic Fuzzing with Default Wordlist**:
   ```bash
   python3 host_header_fuzzer.py https://example.com
   ```

2. **Fuzzing with a Custom Wordlist**:
   ```bash
   python3 host_header_fuzzer.py https://example.com --wordlist https://example.com/custom-wordlist.txt
   ```

3. **Fuzzing with Subdomains File**:
   ```bash
   python3 host_header_fuzzer.py https://example.com --subdomains subdomains.txt
   ```

## How It Works

1. **Wordlist Download**:
   - The script downloads the default wordlist if no custom wordlist is provided.
   - If the default wordlist already exists locally, it skips the download.

2. **Wordlist Cleaning**:
   - Removes redundant suffixes (e.g., `.%s`) from the downloaded wordlist.

3. **Wordlist Combination**:
   - Merges the cleaned wordlist with subdomains from the user-provided file (if available).
   - Appends domain-specific entries for better fuzzing results.

4. **Fuzzing Execution**:
   - Uses `ffuf` for fuzzing with the combined wordlist.
   - Filters results to show only HTTP 200 responses.

5. **Output**:
   - Displays valid HTTP 200 responses in real-time.

## Dependencies

The following Python libraries are used in the script:

- **argparse**: For parsing command-line arguments.
- **os**: For file and path management.
- **re**: For regex-based wordlist cleaning.
- **subprocess**: For executing system commands (e.g., `wget` and `ffuf`).

## Example Output

```plaintext
[+] Using existing wordlist: base_wordlist.txt
[+] Cleaning the downloaded wordlist...
[+] Creating combined wordlist...
[+] Combined wordlist created at 'combined_wordlist.txt'.
[+] Starting Host Header Fuzzing with ffuf and filtering for HTTP 200 responses...
https://example.com [200] Size: 1234 Words: 567 Lines: 89
https://admin.example.com [200] Size: 4321 Words: 765 Lines: 98
```

## Troubleshooting

1. **`ffuf` Not Found**:
   - Ensure `ffuf` is installed and available in your system's PATH.
   - Install using `sudo apt install ffuf`.

2. **Wordlist Download Fails**:
   - Ensure `wget` is installed.
   - Check your internet connection or the availability of the wordlist URL.

3. **Permission Errors**:
   - Run the script with sufficient permissions (e.g., use `sudo` if necessary).

4. **Subdomains File Not Found**:
   - Verify the file path for the `--subdomains` option.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **ffuf**: [ffuf GitHub Repository](https://github.com/ffuf/ffuf)
- **Virtual Host Wordlist**: [cujanovic/Virtual-host-wordlist](https://github.com/cujanovic/Virtual-host-wordlist)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to contribute to the project.

## Disclaimer

This tool is intended for educational and legal security testing purposes only. The author is not responsible for any misuse of this tool.
