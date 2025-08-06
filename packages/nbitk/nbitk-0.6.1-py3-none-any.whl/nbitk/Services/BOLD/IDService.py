import json
import time
from typing import Dict, List
from Bio.SeqRecord import SeqRecord
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from json.decoder import JSONDecodeError

from nbitk.config import Config
from nbitk.logger import get_formatted_logger


class IDService:

    def __init__(self, config: Config):
        """
        Client for running BOLD identification analyses. The configuration object may contain settings such as:
        - `log_level`: Logging level for the service (default is WARNING)
        - `bold_database`: The BOLD database to use (default is 1 for public.bin-tax-derep)
        - `bold_operating_mode`: The operating mode for BOLD (default is 1 for 94% similarity)
        - `bold_timeout`: Timeout for BOLD requests in seconds (default is 300 seconds)
        - `bold_params`: Additional parameters for BOLD requests (default is an empty dictionary)

        The additional bold parameters can include:
        - `db`, which is one of "public.bin-tax-derep" (default), "species", "all.bin-tax-derep", "DS-CANREF22",
                "public.plants", "public.fungi", "all.animal-alt", "DS-IUCNPUB",
        - `mi`, minimum identity, e.g. 0.8 for 80% similarity
        - `maxh`, maximum hits, e.g. 100 for 100 hits
        - `mo` ?
        - `order` ?


        :param config: NBITK configuration object containing BOLD connection settings
        """
        self.config = config
        if config.get('log_level') is None:
            config.set('log_level', 'WARNING')
        self.logger = get_formatted_logger(__name__, config)

        # Get BOLD-specific configuration with defaults
        self.database = config.get('bold_database', 1)  # Default to public.bin-tax-derep
        self.operating_mode = config.get('bold_operating_mode', 1)  # Default to 94% similarity
        self.timeout = config.get('bold_timeout', 300)  # 5 minutes default timeout
        self.params = config.get('bold_params', {})

        # Build URL and parameters from config
        self.base_url, self.params = self._build_url_params()

        self.logger.info(
            f"Initialized BOLD service with database {self.database}, operating mode {self.operating_mode}")

    def _build_url_params(self) -> tuple:
        """
        Build the base URL and parameters for BOLD requests.

        :return: A tuple containing the base URL and a dictionary of parameters
        """
        # Database mapping
        idx_to_database = {
            1: "public.bin-tax-derep",
            2: "species",
            3: "all.bin-tax-derep",
            4: "DS-CANREF22",
            5: "public.plants",
            6: "public.fungi",
            7: "all.animal-alt",
            8: "DS-IUCNPUB",
        }

        # Operating mode mapping
        idx_to_operating_mode = {
            1: {"mi": 0.94, "maxh": 25},
            2: {"mi": 0.9, "maxh": 50},
            3: {"mi": 0.75, "maxh": 100},
        }

        if self.database not in idx_to_database:
            raise ValueError(f"Invalid database: {self.database}. Must be 1-8.")

        if self.operating_mode not in idx_to_operating_mode:
            raise ValueError(f"Invalid operating mode: {self.operating_mode}. Must be 1-3.")

        params = {
            "db": idx_to_database[self.database],
            "mi": idx_to_operating_mode[self.operating_mode]["mi"],
            "mo": 100,
            "maxh": idx_to_operating_mode[self.operating_mode]["maxh"],
            "order": 3,
        }

        # Override with any additional parameters from config
        conf_parms = self.config.get('bold_params', {})
        for key in params.keys():
            if key in conf_parms:
                params[key] = conf_parms[key]

        base_url = "https://id.boldsystems.org/submission?db={}&mi={}&mo={}&maxh={}&order={}".format(
            params["db"], params["mi"], params["mo"], params["maxh"], params["order"]
        )

        return base_url, params

    def _submit_sequences(self, records: List[SeqRecord]) -> str:
        """
        Submit a sequence to BOLD and return the submission ID.

        :param record: A Bio.SeqRecord object containing the sequence to submit
        :return: The submission ID returned by BOLD
        """
        # Create session with retry strategy
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
        })
        retry_strategy = Retry(total=10, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        # Format sequence data for submission
        data = "".join(f">{record.id}\n{record.seq}\n" for record in records)
        files = {"file": ("submitted.fas", data, "text/plain")}

        try:
            while True:
                try:
                    # Submit the POST request
                    self.logger.debug(f"Submitting sequences to BOLD")
                    response = session.post(self.base_url, params=self.params, files=files)
                    response.raise_for_status()
                    result = json.loads(response.text)
                    break
                except (JSONDecodeError, requests.RequestException) as e:
                    self.logger.warning(f"Request failed: {e}, retrying in 60 seconds")
                    time.sleep(60)

            sub_id = result['sub_id']
            self.logger.debug(f"Received submission ID: {sub_id}")
            return sub_id
        finally:
            session.close()

    def _wait_for_and_get_results(self, sub_id: str, records: List[SeqRecord]) -> List[Dict]:
        """
        Wait for BOLD processing to complete and return parsed results.

        :param sub_id: The submission ID returned by BOLD
        :param records: The list of input SeqRecord objects to match against results
        :return: A list of dictionaries containing the parsed results
        """
        results_url = f"https://id.boldsystems.org/submission/results/{sub_id}"

        # Create session for polling results
        session = requests.Session()
        retry_strategy = Retry(total=5, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        start_time = time.time()

        try:
            while time.time() - start_time < self.timeout:
                try:
                    self.logger.debug(f"Checking BOLD results for submission {sub_id}")
                    response = session.get(results_url)
                    response.raise_for_status()

                    # Try to parse JSON-L response
                    result = []
                    data = response.text
                    for json_line in data.splitlines():
                        json_object = json.loads(json_line)
                        result.append({
                            'seqid': json_object['seqid'],
                            'sequence': json_object['sequence'],
                            'results': self._parse_bold_result(json_object)
                        })

                    return result

                except requests.RequestException as e:
                    self.logger.debug(f"Request error while checking results: {e}, retrying...")
                    time.sleep(10)
                except json.JSONDecodeError:
                    # Results might not be ready if we can't parse JSON
                    self.logger.debug("Results not ready (invalid JSON), waiting...")
                    time.sleep(10)

            raise TimeoutError(f"BOLD processing timed out after {self.timeout} seconds")

        finally:
            session.close()

    def _parse_bold_result(self, result_data: Dict) -> List[Dict]:
        """
        Parse a BOLD result response into our standard format.

        :param result_data: The raw result data from BOLD
        :return: A list of dictionaries containing parsed results
        """
        results = []
        bold_results = result_data.get("results", {})

        if bold_results:
            for key, result_info in bold_results.items():
                # Parse the key format: process_id|primer|bin_uri|taxid|etc
                key_parts = key.split("|")
                process_id = key_parts[0] if len(key_parts) > 0 else ""
                primer = key_parts[1] if len(key_parts) > 1 else ""
                bin_uri = key_parts[2] if len(key_parts) > 2 else ""
                taxid = key_parts[3] if len(key_parts) > 3 else ""

                # Extract alignment metrics
                pident = result_info.get("pident", 0.0)
                bitscore = result_info.get("bitscore", 0.0)
                evalue = result_info.get("evalue", 1.0)

                # Extract taxonomy information
                taxonomy = result_info.get("taxonomy", {})
                result_dict = {
                    "phylum": taxonomy.get("phylum"),
                    "class": taxonomy.get("class"),
                    "order": taxonomy.get("order"),
                    "family": taxonomy.get("family"),
                    "subfamily": taxonomy.get("subfamily"),  # Include subfamily if present
                    "genus": taxonomy.get("genus"),
                    "species": taxonomy.get("species"),
                    "pct_identity": pident,
                    "bitscore": bitscore,
                    "evalue": evalue,
                    "process_id": process_id,
                    "primer": primer,
                    "bin_uri": bin_uri,
                    "taxid": taxid,
                    "taxid_count": taxonomy.get("taxid_count", "")
                }
                results.append(result_dict)
        else:
            # No matches found
            self.logger.debug(f"No matches found for sequence {result_data.get('seqid', 'unknown')}")

        return results

    def identify_seqrecords(self, records: List[SeqRecord]) -> List[Dict]:
        """
        Identify a sequence using BOLD and return the results.

        :param records: A list of Bio.SeqRecord objects containing the sequences to identify
        :return: A list of dictionaries containing the identification results
        """
        self.logger.info(f"Identifying {len(records)} sequences using BOLD")

        # Submit the sequence to BOLD
        sub_id = self._submit_sequences(records)

        # Wait for results and get parsed data
        results = self._wait_for_and_get_results(sub_id, records)

        if not results:
            self.logger.warning(f"No identification results found for sequences")

        return results

if __name__ == "__main__":
    import argparse
    from Bio import SeqIO
    from nbitk.config import Config

    # Process command line arguments
    parser = argparse.ArgumentParser(description="BOLD ID Service Example")
    parser.add_argument('--bold_database', type=int, help='BOLD database', default=1)
    parser.add_argument('--bold_operating_mode', type=int, help='BOLD operating mode', default=1)
    parser.add_argument('--bold_timeout', type=int, help='BOLD request timeout in seconds', default=300)
    parser.add_argument('--log_level', type=str, help='Logging level', default='WARNING')
    parser.add_argument('--input_file', type=str, help='Input FASTA file', required=True)
    args = parser.parse_args()

    # Create a Config object and set parameters from command line arguments
    config = Config()
    config.config_data = {
        'bold_database': args.bold_database,
        'bold_operating_mode': args.bold_operating_mode,
        'bold_timeout': args.bold_timeout,
        'log_level': args.log_level
    }
    config.initialized = True

    # Initialize the IDService with the configuration
    id_service = IDService(config)

    # Process the input FASTA file and print TSV output
    id_service.logger.info(f"Processing input file: {args.input_file}")

    # Read the input FASTA file into a list of SeqRecord objects
    with open(args.input_file, 'r') as handle:
        seqrecords = list(SeqIO.parse(handle, 'fasta'))
        results = id_service.identify_seqrecords(seqrecords)

        # Prints the header only once
        header = results[0].keys()
        print("\t".join(header))

        # Print the results in TSV format
        for results_dict in results:
            print("\t".join(str(results_dict.get(key, '')) for key in header))


