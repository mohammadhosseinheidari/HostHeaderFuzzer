import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import json
from typing import Optional, Union, List, Dict, Any, Set, Tuple
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found. Please install it using: pip install requests", file=sys.stderr)
    sys.exit(1)

# --- Configuration ---
DEFAULT_STATIC_WORDLIST_URL = "https://raw.githubusercontent.com/cujanovic/Virtual-host-wordlist/master/virtual-host-wordlist.txt"
DEFAULT_WORDLIST_FILENAME = "static_wordlist_cleaned.txt"
DEFAULT_FFUF_PATH = "ffuf"
DOWNLOAD_USER_AGENT = "HostHeaderFuzzerScript/1.0"
DEFAULT_MATCH_CODES = "200,204,301,302,307,308,401,403,405,500"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.ERROR,
    format="%(message)s",
)
log = logging.getLogger(__name__)

class HostHeaderFuzzer:
    def __init__(
        self,
        target_url: str,
        static_wordlist: Optional[str] = None,
        subdomain_wordlist: Optional[str] = None,
        ffuf_path: str = DEFAULT_FFUF_PATH,
        output_file: Optional[str] = None,
        ffuf_options: str = "",
        match_codes: str = DEFAULT_MATCH_CODES,
    ):
        self.target_url = self._validate_url(target_url)
        parsed_url = urlparse(self.target_url)
        self.target_domain = parsed_url.netloc.split(":")[0]

        self.static_wordlist_path = static_wordlist
        self.subdomain_wordlist_path = subdomain_wordlist
        self.ffuf_path = ffuf_path
        self.final_output_path = output_file
        self.ffuf_options = ffuf_options
        self.match_codes_str = match_codes

        self._temp_ffuf_output_files: List[str] = []

    def _validate_url(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        parsed = urlparse(url)
        if not parsed.netloc:
            sys.exit(1)
        return url

    def _check_ffuf(self) -> str:
        path = shutil.which(self.ffuf_path)
        if not path:
            sys.exit(1)
        return path

    def _download_default_wordlist(self) -> Optional[str]:
        save_path = os.path.join(os.path.dirname(__file__), DEFAULT_WORDLIST_FILENAME)
        if os.path.exists(save_path):
            return save_path

        try:
            response = requests.get(DEFAULT_STATIC_WORDLIST_URL, headers={"User-Agent": DOWNLOAD_USER_AGENT}, timeout=30)
            response.raise_for_status()

            cleaned_lines = [line.replace(".%s", "").strip() for line in response.text.splitlines() if line.strip()]
            with open(save_path, "w", encoding="utf-8") as f:
                f.write("\n".join(cleaned_lines))
            return save_path
        except Exception as e:
            print(f"Error downloading wordlist: {e}")
            return None

    def _build_ffuf_command(self, mode: str, wordlist: str, ffuf_exec: str) -> Tuple[List[str], Optional[str]]:
        cmd = [
            ffuf_exec,
            "-u", self.target_url,
            "-w", wordlist,
            "-mc", self.match_codes_str,
            "-s"  # Silent output: فقط نتایج
        ]

        host_header = {
            "static": "Host: FUZZ",
            "static_append": f"Host: FUZZ.{self.target_domain}",
            "subdomain": "Host: FUZZ",
        }.get(mode)

        if not host_header:
            raise ValueError(f"Unknown mode: {mode}")

        cmd.extend(["-H", host_header])

        temp_output = None
        if self.final_output_path:
            temp_output = f"{self.final_output_path}_{mode}.json"
            cmd.extend(["-o", temp_output, "-of", "json"])

        if self.ffuf_options:
            extra_opts = [opt for opt in self.ffuf_options.split() if opt not in ("-mc", "-o", "-of", "-s")]
            if extra_opts:
                cmd.extend(extra_opts)

        return cmd, temp_output

    def _run_ffuf(self, cmd: List[str], temp_out: Optional[str]):
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if proc.stdout:
                for line in proc.stdout:
                    sys.stdout.write(line)
            proc.wait()
            if proc.returncode == 0 and temp_out and os.path.getsize(temp_out) > 0:
                self._temp_ffuf_output_files.append(temp_out)
        except Exception as e:
            print(f"Error running ffuf: {e}")

    def _consolidate_results(self):
        if not self.final_output_path or not self._temp_ffuf_output_files:
            return

        results: List[Dict[str, Any]] = []
        seen: Set[Tuple[int, int]] = set()

        for file in self._temp_ffuf_output_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for r in data.get("results", []):
                        key = (r.get("status"), r.get("length"))
                        if None not in key and key not in seen:
                            seen.add(key)
                            results.append(r)
            except Exception:
                pass

        if results:
            results.sort(key=lambda x: (x.get("status", 0), x.get("host", "")))
            try:
                with open(self.final_output_path + "_final.json", "w", encoding="utf-8") as f:
                    json.dump({
                        "results": results
                    }, f, indent=4)
            except Exception:
                pass

    def run_fuzzing(self):
        ffuf_exec = self._check_ffuf()

        if not self.static_wordlist_path:
            self.static_wordlist_path = self._download_default_wordlist()

        static_modes = os.path.isfile(self.static_wordlist_path) if self.static_wordlist_path else False
        subdomain_mode = os.path.isfile(self.subdomain_wordlist_path) if self.subdomain_wordlist_path else False

        if static_modes:
            for mode in ["static", "static_append"]:
                cmd, out = self._build_ffuf_command(mode, self.static_wordlist_path, ffuf_exec)
                self._run_ffuf(cmd, out)

        if subdomain_mode:
            cmd, out = self._build_ffuf_command("subdomain", self.subdomain_wordlist_path, ffuf_exec)
            self._run_ffuf(cmd, out)

        self._consolidate_results()

    def cleanup(self):
        self._temp_ffuf_output_files = []


def main():
    parser = argparse.ArgumentParser(description="Host Header Fuzzer using ffuf.")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-sw", "--static-wordlist", help="Static wordlist path")
    parser.add_argument("-dw", "--subdomain-wordlist", help="Subdomain wordlist path")
    parser.add_argument("-mc", "--match-codes", default=DEFAULT_MATCH_CODES, help="Match status codes")
    parser.add_argument("-o", "--output", help="Output file (without extension)")
    parser.add_argument("--ffuf-path", default=DEFAULT_FFUF_PATH, help="Path to ffuf binary")
    parser.add_argument("--ffuf-options", default="", help="Extra ffuf options")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    fuzzer = HostHeaderFuzzer(
        target_url=args.url,
        static_wordlist=args.static_wordlist,
        subdomain_wordlist=args.subdomain_wordlist,
        output_file=args.output,
        ffuf_path=args.ffuf_path,
        ffuf_options=args.ffuf_options,
        match_codes=args.match_codes
    )

    try:
        fuzzer.run_fuzzing()
    except KeyboardInterrupt:
        pass
    finally:
        fuzzer.cleanup()


if __name__ == "__main__":
    main()
