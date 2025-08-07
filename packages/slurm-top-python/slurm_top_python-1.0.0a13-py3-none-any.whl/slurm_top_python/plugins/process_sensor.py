'''
    SLURM Job sensor plugin

    Generates the running SLURM jobs information
'''
import subprocess
import getpass
import datetime
import time
import logging
import re
from slurm_top_python.core import Plugin
from slurm_top_python.constants import (PRIVILEGED_USERS,
                             SYSTEM_USERS
                             )


class SlurmJobSensor(Plugin):
    def __init__(self, **kwargs):
        super(SlurmJobSensor, self).__init__(**kwargs)
        # there will be two parts of the returned value, one will be text and other graph
        # there can be many text (key,value) pairs to display corresponding to each key
        self.currentValue['text'] = {
            'running_jobs': 0,
            'pending_jobs': 0,
            'total_jobs': 0,
            'total_nodes': 0
        }
        # nested structure is used for keeping the info of jobs
        self.currentValue['table'] = []
        self._currentSystemUser = getpass.getuser()
        self.logger = logging.getLogger(__name__)

    def format_time(self, time_str):
        """Format time from SLURM time format to readable format"""
        if not time_str or time_str == 'UNLIMITED':
            return 'UNLIMITED'

        # Handle different time formats from SLURM
        # Format can be: days-hours:minutes:seconds, hours:minutes:seconds, minutes:seconds
        if '-' in time_str:
            days, hms = time_str.split('-', 1)
            if ':' in hms:
                h, m, s = hms.split(':')
                return f"{days}d {h:0>2}:{m:0>2}:{s:0>2}"
            else:
                return f"{days}d {hms}"
        elif time_str.count(':') == 2:
            h, m, s = time_str.split(':')
            return f"{h:0>2}:{m:0>2}:{s:0>2}"
        elif time_str.count(':') == 1:
            m, s = time_str.split(':')
            return f"00:{m:0>2}:{s:0>2}"
        else:
            return time_str

    def parse_memory(self, mem_str):
        """Parse memory string from SLURM format"""
        if not mem_str:
            return 0

        # Remove any suffix and convert to MB
        mem_str = mem_str.upper()
        if mem_str.endswith('K'):
            return float(mem_str[:-1]) / 1024
        elif mem_str.endswith('M'):
            return float(mem_str[:-1])
        elif mem_str.endswith('G'):
            return float(mem_str[:-1]) * 1024
        elif mem_str.endswith('T'):
            return float(mem_str[:-1]) * 1024 * 1024
        else:
            try:
                return float(mem_str) / (1024 * 1024)  # Assume bytes
            except:
                return 0

    def run_squeue_command(self):
        """Execute squeue command and return parsed output"""
        try:
            # Custom format to get detailed job information
            cmd = [
                # squeue -o "%i|%P|%j|%u|%t|%M|%l|%D|%C|%m|%R" --noheader
                'squeue',
                '-o',
                '%i|%P|%j|%u|%t|%M|%l|%D|%C|%m|%R',
                '--noheader'
            ]

            # If not a privileged user, only show jobs for current user
            # if self._currentSystemUser not in PRIVILEGED_USERS:
            #     cmd.extend(['--user', self._currentSystemUser])

            self.logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                self.logger.error(
                    f"squeue command failed with return code {result.returncode}: {result.stderr}")
                # If squeue fails, it might be because SLURM is not available or no jobs exist
                return []

            output_lines = result.stdout.strip().split(
                '\n') if result.stdout.strip() else []
            self.logger.info(f"squeue returned {len(output_lines)} lines")
            return output_lines

        except subprocess.TimeoutExpired:
            self.logger.error("Squeue command timed out")
            return []
        except FileNotFoundError:
            self.logger.error(
                "Squeue command not found - is SLURM installed?")
            return []
        except Exception as e:
            self.logger.error(f"Error running squeue: {str(e)}")
            return []

    def get_job_details(self, job_id):
        """Get additional job details using scontrol"""
        try:
            cmd = ['scontrol', 'show', 'job', str(job_id)]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                details = {}
                for line in result.stdout.split('\n'):
                    if '=' in line:
                        for item in line.split():
                            if '=' in item:
                                key, value = item.split('=', 1)
                                details[key] = value
                return details
            return {}
        except:
            return {}

    # overriding the update method
    def update(self):
        self.logger.info("Starting SLURM job sensor update")
        job_count = 0
        running_jobs = 0
        pending_jobs = 0
        total_nodes = 0
        job_info_list = []

        squeue_output = self.run_squeue_command()
        self.logger.info(f"Got {len(squeue_output)} lines from squeue")

        for line in squeue_output:
            if not line.strip():
                continue

            try:
                # New: parse 11 fields (no NODELIST)
                # Format: JOBID|PARTITION|NAME|USER|STATE|TIME|TIME_LIMIT|NODES|CPUS|MIN_MEMORY|REASON
                parts = line.split('|')
                if len(parts) < 11:
                    self.logger.warning(
                        f"Skipping line with insufficient parts: {line}")
                    continue

                job_info = {}
                job_info['id'] = parts[0].strip()
                job_info['partition'] = parts[1].strip()
                job_info['name'] = parts[2].strip()
                job_info['user'] = parts[3].strip()
                job_info['state'] = parts[4].strip().ljust(2)
                job_info['time'] = self.format_time(parts[5].strip())
                job_info['time_limit'] = self.format_time(parts[6].strip())
                job_info['nodes'] = parts[7].strip()
                job_info['cpus'] = parts[8].strip()
                job_info['memory'] = self.parse_memory(parts[9].strip())
                job_info['reason'] = parts[10].strip().replace("(", "").replace(")", "")

                # Count job states
                if job_info['state'] == 'R':
                    running_jobs += 1
                elif job_info['state'] == 'PD':
                    pending_jobs += 1

                # Add node count to total
                try:
                    total_nodes += int(job_info['nodes'])
                except:
                    pass

                if job_info['user'] not in SYSTEM_USERS:
                    SYSTEM_USERS.append(job_info['user'])

                job_info_list.append(job_info)
                job_count += 1

            except Exception as e:
                self.logger.warning(
                    f"Error parsing job line '{line}': {str(e)}")
                continue

        self.logger.info(f"Parsed {job_count} jobs successfully")

        # Sort jobs by job ID
        job_info_list.sort(key=lambda x: int(
            x['id']) if x['id'].isdigit() else 0)

        # Pad time fields for better alignment
        if job_info_list:
            time_len = max((len(job.get('time', ''))
                           for job in job_info_list), default=0)
            limit_len = max((len(job.get('time_limit', ''))
                            for job in job_info_list), default=0)

            for job in job_info_list:
                job['time'] = '{0: >{1}}'.format(job.get('time', ''), time_len)
                job['time_limit'] = '{0: >{1}}'.format(
                    job.get('time_limit', ''), limit_len)

        # Update the current values
        self.currentValue['table'] = job_info_list
        self.currentValue['text']['total_jobs'] = str(job_count)
        self.currentValue['text']['running_jobs'] = str(running_jobs)
        self.currentValue['text']['pending_jobs'] = str(pending_jobs)
        self.currentValue['text']['total_nodes'] = str(total_nodes)

        self.logger.info(
            f"Updated sensor with {job_count} jobs, {running_jobs} running, {pending_jobs} pending")


# Create the SLURM job sensor with appropriate interval
# SLURM jobs change less frequently than processes, so we can use a longer interval
slurm_job_sensor = SlurmJobSensor(
    name='Process', sensorType='table', interval=5)
