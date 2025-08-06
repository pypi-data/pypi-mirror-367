import json
import zipfile

import pydantic
import requests
from requests import HTTPError
from tabulate import tabulate
from pprint import pprint

from config import DynexConfig
from interfaces.api import Job, JobOpts


class DynexAPI:
    """Dynex API"""
    __slots__ = [
        "avg_block_fee",
        "config",
        "logger",
        "logging",
    ]
    avg_block_fee: float

    def __init__(self, config: DynexConfig = None, logging: bool = False):
        self.config = config if config is not None else DynexConfig()
        self.logger = getattr(self.config, "logger", None)
        self.logging = logging

    @staticmethod
    def _post_request(url: str, opts: dict, file_path: str) -> requests.Response:
        opts_json = json.dumps(opts)
        with open(file_path, 'rb') as file:
            files = {
                'opts': (None, opts_json, 'application/json'),
                'job': (file_path, file, 'application/octet-stream')
            }
            response = requests.post(url, files=files)
        return response

    def _make_base_post_request(self, url: str, payload: dict, headers: dict = None, files: dict = None) -> dict:
        """Make base post request."""

        if headers is None:
            headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=json.dumps(payload), files=files)
        if response.status_code != 200:
            msg = f'[ERROR] Error code: {response.status_code}. Reason: {response.reason}'
            self.logger.error(msg)
            raise Exception(msg)
        else:
            return response.json()

    def update_job_api(self, job_id: int) -> bool:
        """
        `Internal Function`
        Dynex API call to update an ongoing job

        :Returns:
        - TRUE if the API call was successful, FALSE if the API call was not successful (`bool`)
        """
        url = f'{self.config.api_endpoint}/v2/sdk/job/update?api_key={self.config.api_key}&api_secret={self.config.api_secret}'
        response_data = self._make_base_post_request(url=url, payload={'job_id': job_id})
        return bool(Job.model_validate(response_data))

    def report_invalid(self, filename: str, reason: str) -> bool:
        """
        `Internal Function`
        Dynex API call to report invalid solution file

        :Returns:
        - TRUE if the API call was successful, FALSE if the API call was not successful (`bool`)
        """

        url = f"{self.config.api_endpoint}/v2/sdk/job/invalidate_solution?api_key={self.config.api_key}&api_secret={self.config.api_secret}"
        response_data = self._make_base_post_request(url=url, payload={"filename": filename, "reason": reason})
        return bool(response_data)

    def cancel_job_api(self, job_id: int) -> int:
        """
        `Internal Function`
        Dynex API call to cancel an ongoing job

        :Returns:
        - TRUE if the API call was successful, FALSE if the API call was not successful (`bool`)
        """
        url = f'{self.config.api_endpoint}/v2/sdk/job/cancel?api_key={self.config.api_key}&api_secret={self.config.api_secret}'
        response_data = self._make_base_post_request(url=url, payload={"job_id": job_id})
        return bool(response_data)

    def finish_job_api(self, job_id: int, min_loc: float, min_energy: float) -> bool:
        """
        `Internal Function`

        Dynex API call to finish an ongoing job

        :Returns:

        - TRUE if the API call was successful, FALSE if the API call was not successful (`bool`)
        """
        url = f"{self.config.api_endpoint}/v2/sdk/job/finish?api_key={self.config.api_key}&api_secret={self.config.api_secret}"
        payload = {"job_id": job_id, "min_loc": min_loc, "min_energy": min_energy}
        response_data = self._make_base_post_request(url=url, payload=payload)
        return bool(response_data)

    def create_job_api(
            self,
            sampler: "DynexSampler",
            annealing_time: int,
            switchfraction: int,
            num_reads: int,
            alpha: int = 20,
            beta: int = 20,
            gamma: int = 1,
            delta: int = 1,
            epsilon: int = 1,
            zeta: int = 1,
            minimum_stepsize: float = 0.00000006,
            block_fee: int = 0,
            is_cluster: bool = False,
            cluster_type: int = 1,
            shots: int = 1,
            target_energy: int = 0
    ) -> tuple:
        """
        `Internal Function`

        Dynex API call to create a job file and start computing

        :Returns:

        - job_id
        """

        if block_fee == 0:
            block_fee = self._price_oracle()

        self.logger.info(f'[DYNEX] AVERAGE BLOCK FEE: {block_fee / 1000000000} DNX')
        # parameters:
        url = f'{self.config.api_endpoint}/v2/sdk/job/create?api_key={self.config.api_key}&api_secret={self.config.api_secret}'
        opts = {
            "annealing_time": annealing_time,
            "switch_fraction": switchfraction,
            "num_reads": num_reads,
            "params": [alpha, beta, gamma, delta, epsilon, zeta],
            "min_step_size": minimum_stepsize,
            "description": sampler.description,
            "block_fee": block_fee,
            "is_cluster": is_cluster,
            "cluster_type": cluster_type,
            "shots": shots,
            "solver_family": 0,
            "target_energy": target_energy
        }
        if self.config.solver_version == 2:
            opts.update({
                "solver_family": 1,
                "population_size": annealing_time
            })

        # file:
        file_path = sampler.filepath + sampler.filename
        # compress:
        file_zip = sampler.filepath + sampler.filename + '.zip'
        with zipfile.ZipFile(file_zip, 'w', zipfile.ZIP_DEFLATED) as f:
            f.write(file_path, arcname=sampler.filename)
        self.logger.info('[DYNEX] SUBMITTING FILE FOR WORLDWIDE DISTRIBUTION...')
        # Retry logic for post request
        last_exception = None
        for try_count in range(self.config.retry_count, 0, -1):
            try:
                response = self._post_request(url, {"opts": opts}, file_zip)
                json_data = response.json()

                # Check for API error response
                if 'error' in json_data:
                    error_msg = json_data['error']
                    self.logger.error(f"[ERROR] {error_msg}")
                    if try_count > 1:
                        self.logger.info(f"Retrying... ({try_count - 1} attempts left)")
                        continue
                    raise Exception(error_msg)
                job_id = JobOpts.model_validate(json_data)

                # If we get here, request was successful
                retval = job_id.job_id
                link = job_id.link
                filename = link.split('/')[-1]
                price_per_block = job_id.price_per_block
                qasm = job_id.qasm
                self.logger.info(f'[DYNEX] COST OF COMPUTE: {price_per_block / 1000000000} DNX')
                return retval, filename, price_per_block, qasm

            except (requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
                last_exception = e
                self.logger.error(f"Request failed: {str(e)}")
                if try_count > 1:
                    self.logger.info(f"Retrying... ({try_count - 1} attempts left)")
                else:
                    self.logger.error("All retry attempts exhausted")
                    raise SystemExit(e)
            except pydantic.ValidationError as e:
                self.logger.error(f"API Validation error: {json_data}")
                raise SystemExit(e)
            except Exception as e:
                last_exception = e
                self.logger.error(f"Unexpected error: {str(e)}")
                if try_count > 1:
                    self.logger.info(f"Retrying... ({try_count - 1} attempts left)")
                else:
                    self.logger.error("All retry attempts exhausted")
                    raise SystemExit(e)

        # This line should theoretically never be reached
        raise SystemExit(f"Failed after {self.config.retry_count} attempts: {str(last_exception)}")

    @staticmethod
    def _find_largest_value(lst: list) -> int:
        """
        `Internal Function`
        :Returns:
        - The largest variable in a list of clauses (`int`)
        """

        largest_value = None

        for sublist in lst:
            for value in sublist:
                if largest_value is None or value > largest_value:  # FIXME what the fuck?
                    largest_value = value

        return largest_value

    @staticmethod
    def _sat_creator(variables: list, clause_type: int, dummy_number: int, results_clauses: list):
        """
        `Internal Function`

        Converts a k-sat clause to a number of 3-sat clauses.

        :Parameters:

        - :variables:
        - :clause_type:
        - :dummy_number:
        - :results_clauses:

        :Returns:

        - :dummy_number:
        - :results_clauses:

        """

        if clause_type == 1:
            # Beginning clause
            results_clauses.append([variables[0], variables[1], dummy_number])
            dummy_number *= -1

        elif clause_type == 2:
            # Middle clause
            for i in range(len(variables)):
                temp = dummy_number
                dummy_number *= -1
                dummy_number += 1
                results_clauses.append([temp, variables[i], dummy_number])
                dummy_number *= -1

        elif clause_type == 3:
            # Final clause
            for i in range(len(variables) - 2):
                temp = dummy_number
                dummy_number *= -1
                dummy_number += 1
                results_clauses.append([temp, variables[i], dummy_number])
                dummy_number *= -1
            results_clauses.append([dummy_number, variables[-2], variables[-1]])
            dummy_number *= -1
            dummy_number += 1

        return dummy_number, results_clauses

    def k_sat(self, clauses: list) -> list:
        """
        `Internal Function`

        Converts a k-sat formulation into 3-sat.

        :Returns:

        - List of clauses of the converted 3-sat (`list`)
        """
        results_clauses = [[1]]
        variables = self._find_largest_value(clauses)
        dummy_number = variables + 1
        for values in clauses:
            total_variables = len(values)
            # Case 3 variables
            if total_variables == 3:
                results_clauses.append([values[0], values[1], values[2]])
            else:
                # Case 1 variable
                if total_variables == 1:
                    results_clauses.append([values[0]])
                # Case 2 variables
                elif total_variables == 2:
                    results_clauses.append([values[0], values[1]])
                    dummy_number += 1
                # Case more than 3 variable
                else:
                    first_clause = values[:2]
                    dummy_number, results_clauses = self._sat_creator(first_clause, 1, dummy_number, results_clauses)

                    middle_clauses = values[2:len(values) - 2]
                    dummy_number, results_clauses = self._sat_creator(middle_clauses, 2, dummy_number, results_clauses)

                    last_clause = values[len(values) - 2:]
                    dummy_number, results_clauses = self._sat_creator(last_clause, 3, dummy_number, results_clauses)

        return results_clauses

    def _price_oracle(self) -> float:
        """
        `Internal Function`

        Dynex API call to output the current average price for compute on Dynex. Only applicable when using pay-to-go pricing.

        :Returns:

        - TRUE if the API call was successful, FALSE if the API call was not successful (`bool`)
        """
        url = f'{self.config.api_endpoint}/v2/sdk/price_oracle?api_key={self.config.api_key}&api_secret={self.config.api_secret}'
        response = requests.get(url)
        data = response.json()
        if 'error' not in data:
            self.avg_block_fee = data['avg_block_fee']
            if self.logging:
                self.logger.info(f'AVERAGE BLOCK FEE: {self.avg_block_fee / 1000000000} DNX')
            retval = self.avg_block_fee
        else:
            raise Exception('INVALID API CREDENTIALS')
        return retval

    def _check_api_status(self) -> bool:
        """
        `Internal Function`

        Dynex API call to output the status of the Dynex SDK account

        :Returns:

        - TRUE if the API call was successful, FALSE if the API call was not successful (`bool`)
        """

        self.avg_block_fee = self._price_oracle()
        url = f'{self.config.api_endpoint}/v2/sdk/status?api_key={self.config.api_key}&api_secret={self.config.api_secret}'
        response = requests.get(url)
        data = response.json()
        retval = False
        if 'error' not in data:
            if 'billing_type' not in data:
                max_chips = data['max_chips']
                max_annealing_time = data['mas steps']
                max_duration = data['max_duration']
                total_usage = data['total_usage']
                confirmed_balance = data['confirmed_balance']
                account_time = data['account_time']
                if self.logging:
                    self.logger.info(f"""
                                            ACCOUNT: {account_time}\n
                                            API SUCCESSFULLY CONNECTED TO DYNEX\n
                                            -----------------------------------\n
                                            MAXIMUM NUM_READS: {max_chips}\n
                                            CURRENT AVG BLOCK FEE: {self.avg_block_fee / 1000000000}\n
                                            MAXIMUM ANNEALING_TIME: {max_annealing_time}\n
                                            MAXIMUM CONFIRMED BALANCE: {confirmed_balance / 1000000000} \n
                                            MAXIMUM USAGE TOTAL: {total_usage / 1000000000} \n
                                            MAXIMUM JOB DURATION: {max_duration} MINUTES\n
                                            AVAILABLE BALANCE: {confirmed_balance / 1000000000} DNX
                                            """)
                retval = True
            else:
                if data['billing_type'] == 2:  # Subscription pricing
                    if self.logging:
                        max_gates = data['max_gates']
                        max_steps = data['max_steps']
                        max_duration = data['max_duration']
                        subs_until = data['subs_until']
                        account_time = data['account_time']
                        self.logger.info(f"""
                                                ACCOUNT: {account_time}\n
                                                API SUCCESSFULLY CONNECTED TO DYNEX\n
                                                -----------------------------------\n
                                                *** SUBSCRIPTION PRICING ***\n
                                                -----------------------------------\n
                                                MAXIMUM GATES: {max_gates}\n
                                                MAXIMUM ANNEALING_TIME: {max_steps}\n
                                                MAXIMUM JOB DURATION: {max_duration} MINUTES\n
                                                SUBSCRIPTION VALID UNTIL: {subs_until}
                                                """)
                    retval = True
                if data['billing_type'] == 1:  # pay-per-use pricing
                    if self.logging:
                        max_chips = data['max_chips']
                        max_steps = data['max_steps']
                        max_duration = data['max_duration']
                        total_usage = data['total_usage']
                        confirmed_balance = data['confirmed_balance']
                        account_time = data['account_time']
                        self.logger.info(f"""
                        ACCOUNT: {account_time}\n
                        API SUCCESSFULLY CONNECTED TO DYNEX\n
                        -----------------------------------\n
                        *** PAY-PER-USE PRICING ***\n
                        -----------------------------------\n
                        MAXIMUM NUM_READS: {max_chips}\n
                        MAXIMUM TOTAL USAGE usage: {total_usage}\n
                        MAXIMUM ANNEALING_TIME: {max_steps}\n
                        MAXIMUM JOB DURATION: {max_duration} MINUTES\n
                        AVAILABLE BALANCE: {confirmed_balance / 1000000000} DNX
                        """)
                    retval = True

        else:
            raise Exception('INVALID API CREDENTIALS')
        return retval

    def _get_status_details_api(self,
                                job_id: int,
                                annealing_time: int,
                                all_stopped: bool = False,
                                wcnf_offset: int = 0,
                                precision: int = 0
                                ):
        """
        `Internal Function`

        Dynex API call to retrieve status of the job

        :Returns:

        - :LOC_MIN: Lowest value of global falsified soft clauses of the problem which is being sampled (`int`)

        - :ENERGY_MIN: Lowest QUBO energy of the problem which is being sampled (`double`)

        - :CHIPS: The number of chips which are currently sampling (`int`)

        - :retval: Tabulated overview of the job status, showing workers, found assignments, etc. (`string`)
        """

        url = f"{self.config.api_endpoint}/v2/sdk/job/atomics?api_key={self.config.api_key}&api_secret={self.config.api_secret}&job_id={job_id}"

        headers = {
            'Content-Type': 'application/json'
        }
        data = list()
        try:
            response = requests.get(url, headers=headers)
            json_data = response.json()
            data = json_data['data']
        except HTTPError as e:
            self.logger.error('[ERROR] Error code: ', e)

        table = [['WORKER', 'VERSION', 'CIRCUITS', 'LOC', 'ENERGY', 'RUNTIME', 'LAST UPDATE', 'STEPS', 'STATUS']]

        LOC_MIN = 2147483647
        ENERGY_MIN = 2147483647
        CHIPS = 0
        i = 0

        for result in data:
            worker = result['worker_id'][:4] + '..' + result['worker_id'][-4:]
            chips = int(result['chips'])
            loc = int(result['loc'])
            energy = float(result['energy'])
            version = result['version']
            updated_at = result['updated_at']
            update_dur = result['update_dur']
            uptime_dur = result['uptime_dur']
            steps = int(result['steps'])

            # adjust energy to underlying model energy:
            if energy != 0:
                energy = (energy + wcnf_offset) * precision

            # truncate version
            version = version[:15]

            # update mins:
            if loc < LOC_MIN:
                LOC_MIN = loc
            if energy < ENERGY_MIN:
                ENERGY_MIN = energy

            # update number of workers:
            CHIPS = CHIPS + chips

            # calculate progress:
            progress = 0.0
            if steps > 0:
                progress = steps / annealing_time * 100
            steps_str = str(steps) + " ({:.2f}%)".format(progress)

            # status display:
            status = "\033[131m%s\033[0m" % 'WAITING'
            if int(steps) < int(annealing_time):
                status = "\033[132m%s\033[0m" % 'RUNNING'
            if int(steps) >= int(annealing_time):
                status = "\033[131m%s\033[0m" % 'STOPPED'
            if all_stopped:
                status = "\033[131m%s\033[0m" % 'STOPPED'
                steps = 'STOPPED'

            # add worker information to table:
            if (loc < 2147483647 and energy < 2147483647):
                table.append([worker, version, chips, loc, energy, update_dur, updated_at, steps_str, status])
            else:
                table.append([worker, version, chips, -1, -1, update_dur, updated_at, steps_str, status])

            i = i + 1

        # if job not worked on:
        if i == 0:
            table.append(['*** WAITING FOR WORKERS ***', '', '', '', '', '', '', '', ''])
            LOC_MIN = 0
            ENERGY_MIN = 0
            CHIPS = 0

        retval = tabulate(table, headers="firstrow", tablefmt="rounded_grid", stralign="right", floatfmt=".2f")

        return LOC_MIN, ENERGY_MIN, CHIPS, retval

    # def estimate_costs(self, model, num_reads, block_fee=0):  # TODO TO reformat & is it need?
    #     """
    #     Dynex API call to estimate costs for a given job by analysing its complexity, given the number of Dynex chips (num_reads) to be used by calculating its network participation.
    #
    #     :Parameters:
    # x
    #     - :model: Model to compute
    #     - :num_reads: Number of Dynex chips to use
    #     - :block_fee: (optional) block fee to override current network average fee
    #
    #     :Returns:
    #
    #     - :price_per_block: Effective price in nanoDNX (/1e9 for DNX) per block
    #     - :price_per_minute: Effective price in nanoDNX (/1e9 for DNX) per minute
    #     - :job_type: 1 = SAT, 3 = MAXSAT, 5 = ISING/QUBO
    #
    #     :Example:
    #
    #     .. code-block:: Python
    #
    #         model = dynex.BQM(bqm)
    #         dynex.estimate_costs(model, num_reads=10000)
    #         [DYNEX] AVERAGE BLOCK FEE: 282.59 DNX
    #         [DYNEX] SUBMITTING COMPUTE FILE FOR COST ESTIMATION...
    #         [DYNEX] COST OF COMPUTE: 0.537993485 DNX PER BLOCK
    #         [DYNEX] COST OF COMPUTE: 0.268996742 DNX PER MINUTE
    #
    #     """
    #
    #     _sampler = _DynexSampler(model, logging=False, mainnet=True, description='cost estimation', test=False,
    #                              bnb=True)
    #
    #     switchfraction = 0
    #     alpha = beta = gamma = delta = epsilon = zeta = minimum_stepsize = 0
    #     annealing_time = 100
    #
    #     # block fee
    #     if block_fee == 0:
    #         block_fee = self._price_oracle()
    #
    #     print('[DYNEX] AVERAGE BLOCK FEE:', '{:,}'.format(block_fee / 1000000000), 'DNX')
    #
    #     # parameters:
    #     url = f'{self.config.api_endpoint}/v2/sdk/job/estimate?api_key={self.config.api_key}&api_secret={self.config.api_secret}'
    #
    #     # options:
    #     opts = {
    #         "opts": {
    #             "annealing_time": annealing_time,
    #             "switch_fraction": switchfraction,
    #             "num_reads": num_reads,
    #             "params": [alpha, beta, gamma, delta, epsilon, zeta],
    #             "min_step_size": minimum_stepsize,
    #             "description": 'cost estimation',
    #             "block_fee": block_fee,
    #             "is_cluster": False
    #         }
    #     }
    #
    #     # file:
    #     file_path = _sampler.filepath + _sampler.filename
    #
    #     # compress:
    #     file_zip = _sampler.filepath + _sampler.filename + '.zip'
    #     with zipfile.ZipFile(file_zip, 'w', zipfile.ZIP_DEFLATED) as f:
    #         f.write(file_path, arcname=_sampler.filename)
    #
    #     try:
    #         print('[DYNEX] SUBMITTING COMPUTE FILE FOR COST ESTIMATION...')
    #         response = self._post_request(url, opts, file_zip)
    #         jsondata = response.json()
    #         # error?
    #         if 'error' in jsondata:
    #             print("[ERROR]", jsondata['error'])
    #             raise Exception(jsondata['error'])
    #         # applicable block fee:
    #         price_per_block = jsondata['price_per_block']
    #         price_per_minute = jsondata['price_per_minute']
    #         job_type = jsondata['job_type']
    #         print('[DYNEX] COST OF COMPUTE:', '{:,}'.format(price_per_block / 1000000000), 'DNX PER BLOCK')
    #         print('[DYNEX] COST OF COMPUTE:', '{:,}'.format(price_per_minute / 1000000000), 'DNX PER MINUTE')
    #
    #     except requests.exceptions.HTTPError as errh:
    #         print("Http Error:", errh)
    #         raise SystemExit(errh)
    #     except requests.exceptions.ConnectionError as errc:
    #         print("Error Connecting:", errc)
    #         raise SystemExit(errc)
    #     except requests.exceptions.Timeout as errt:
    #         print("Timeout Error:", errt)
    #         raise SystemExit(errt)
    #     except requests.exceptions.RequestException as err:
    #         print("OOps: Something Else", err)
    #         raise SystemExit(err)
    #
    #     return price_per_block, price_per_minute, job_type

    def account_status(self) -> bool:
        """
        Shows the status of the Dynex SDK account as well as subscription information:

        .. code-block::

            ACCOUNT: <YOUR ACCOUNT IDENTIFICATION>
            API SUCCESSFULLY CONNECTED TO DYNEX
            -----------------------------------
            MAXIMUM NUM_READS: 100,000
            MAXIMUM ANNEALING_TIME: 10,000
            MAXIMUM JOB DURATION: 60 MINUTES
            COMPUTE:
            CURRENT AVG BLOCK FEE: 31.250005004 DNX
            USAGE:
            AVAILABLE BALANCE: 90.0 DNX
            USAGE TOTAL: 0.0 DNX

        """

        return self._check_api_status()
