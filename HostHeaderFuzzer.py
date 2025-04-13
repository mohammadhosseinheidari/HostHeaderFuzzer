import subprocess
import argparse
import re
import os

class HostHeaderFuzzer:
    """
    A sophisticated class for performing Host Header Fuzzing using the ffuf tool,
    specifically filtering for HTTP 200 OK responses and avoiding redundant downloads.
    """

    def __init__(self, target_url, wordlist_url, subdomains_file=None):
        """
        Initializes the HostHeaderFuzzer instance.

        Args:
            target_url (str): The target URL for fuzzing.
            wordlist_url (str): The URL of the main wordlist file.
            subdomains_file (str, optional): Path to the file containing a list of subdomains (one per line).
                                             Defaults to None.
        """
        self.target_url = target_url
        self.wordlist_url = wordlist_url
        self.subdomains_file = subdomains_file
        self.base_wordlist_file = "base_wordlist.txt"
        self.cleaned_wordlist_file = "cleaned_wordlist.txt"
        self.combined_wordlist_file = "combined_wordlist.txt"

    def _download_wordlist(self):
        """
        Downloads the main wordlist from the given URL if it doesn't already exist.
        """
        if self.wordlist_url == "https://raw.githubusercontent.com/cujanovic/Virtual-host-wordlist/master/virtual-host-wordlist.txt" and os.path.exists(self.base_wordlist_file):
            print(f"[+] Using existing wordlist: {self.base_wordlist_file}")
            return self.base_wordlist_file
        else:
            print(f"[+] Downloading wordlist from: {self.wordlist_url}")
            try:
                subprocess.run(["wget", "-O", self.base_wordlist_file, self.wordlist_url], check=True, capture_output=True)
                return self.base_wordlist_file
            except subprocess.CalledProcessError as e:
                print(f"[-] Error downloading wordlist: {e}")
                return None

    def _clean_wordlist(self, base_wordlist_file):
        """
        Removes the '.%s' suffix from each line of the downloaded wordlist.
        """
        print("[+] Cleaning the downloaded wordlist...")
        cleaned_lines = []
        try:
            with open(base_wordlist_file, "r") as infile:
                for line in infile:
                    cleaned_line = re.sub(r'\.%s$', '', line.strip())
                    cleaned_lines.append(cleaned_line)
            with open(self.cleaned_wordlist_file, "w") as outfile:
                for line in cleaned_lines:
                    outfile.write(f"{line}\n")
            return self.cleaned_wordlist_file
        except FileNotFoundError:
            print(f"[-] Base wordlist file '{base_wordlist_file}' not found for cleaning.")
            return None

    def _generate_combined_wordlist(self, cleaned_wordlist_file):
        """
        Generates a combined wordlist including the cleaned wordlist, domain appended versions, and provided subdomains.
        """
        print("[+] Creating combined wordlist...")
        with open(self.combined_wordlist_file, "w") as outfile:
            if cleaned_wordlist_file:
                with open(cleaned_wordlist_file, "r") as infile:
                    for line in infile:
                        word = line.strip()
                        outfile.write(f"{word}\n")
                        outfile.write(f"{word}.{self.target_url.split('://')[-1]}\n") # Append domain

            if self.subdomains_file:
                try:
                    with open(self.subdomains_file, "r") as infile:
                        for line in infile:
                            subdomain = line.strip()
                            outfile.write(f"{subdomain}\n")
                except FileNotFoundError:
                    print(f"[-] Subdomains file '{self.subdomains_file}' not found.")

        if self.base_wordlist_file:
            subprocess.run(["rm", self.base_wordlist_file], check=False) # Remove base wordlist file
        if self.cleaned_wordlist_file:
            subprocess.run(["rm", self.cleaned_wordlist_file], check=False) # Remove cleaned wordlist file

        print(f"[+] Combined wordlist created at '{self.combined_wordlist_file}'.")
        return self.combined_wordlist_file

    def run_fuzzing(self):
        """
        Executes the fuzzing process using the ffuf tool and filters results for HTTP 200 OK responses.
        """
        base_wordlist = self._download_wordlist()
        if not base_wordlist and not self.subdomains_file:
            print("[-] No wordlist available for fuzzing.")
            return

        cleaned_wordlist = self._clean_wordlist(base_wordlist)
        if not cleaned_wordlist and not self.subdomains_file:
            print("[-] Error cleaning the wordlist.")
            return

        combined_wordlist = self._generate_combined_wordlist(cleaned_wordlist)
        if not combined_wordlist:
            print("[-] Error creating combined wordlist.")
            return

        print("[+] Starting Host Header Fuzzing with ffuf and filtering for HTTP 200 responses...")
        command = [
            "ffuf",
            "-w", combined_wordlist,
            "-u", self.target_url,
            "-H", "host: FUZZ",
            "-H", "User-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0",
            "-fs", "0"  # Filter out responses with size 0 (often errors)
        ]

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # Check if the line contains "[200]" indicating an HTTP 200 response
                    if "[200]" in output:
                        print(output.strip())
            _, stderr = process.communicate()
            if stderr:
                print(f"[-] ffuf errors: {stderr}")

        except FileNotFoundError:
            print("[-] Error: ffuf command not found. Please ensure ffuf is installed and in your system's PATH.")
        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")
        finally:
            subprocess.run(["rm", self.combined_wordlist_file], check=False) # Remove combined wordlist file


def main():
    parser = argparse.ArgumentParser(description="Advanced Python script for Host Header Fuzzing with ffuf, filtering for HTTP 200 OK responses and checking for existing default wordlist.")
    parser.add_argument("target_url", help="The target URL for fuzzing (e.g., https://example.com)")
    parser.add_argument("--wordlist", default="https://raw.githubusercontent.com/cujanovic/Virtual-host-wordlist/master/virtual-host-wordlist.txt",
                        help="The URL of the main wordlist file (default: https://raw.githubusercontent.com/cujanovic/Virtual-host-wordlist/master/virtual-host-wordlist.txt)")
    parser.add_argument("--subdomains", help="Path to the file containing a list of subdomains (one per line)")

    args = parser.parse_args()

    fuzzer = HostHeaderFuzzer(args.target_url, args.wordlist, args.subdomains)
    fuzzer.run_fuzzing()

if __name__ == "__main__":
    main()
