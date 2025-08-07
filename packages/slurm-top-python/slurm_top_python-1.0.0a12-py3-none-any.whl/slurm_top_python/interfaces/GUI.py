# -*- coding: utf-8 -*-
"""
Graphical User Interface for slurm_top_python
"""

import npyscreen
import math
import drawille
import psutil
import logging
import weakref
import sys


from slurm_top_python.utils import ThreadJob
from slurm_top_python.constants import SYSTEM_USERS


# global flags defining actions, would like them to be object vars
TIME_SORT = False
MEMORY_SORT = False
JOB_ID_SORT = False
PROCESS_RELEVANCE_SORT = True
PREVIOUS_TERMINAL_WIDTH = None
PREVIOUS_TERMINAL_HEIGHT = None


class ProcessDetailsInfoBox(npyscreen.PopupWide):
    """
        This widget is used to who the detailed information about the selected process
        in the processes table. Curretly only the port information is shown for a selected
        process.
    `"""

    # Set them to fix the position
    SHOW_ATX = 0
    SHOW_ATY = 0
    DEFAULT_COLUMNS = PREVIOUS_TERMINAL_WIDTH

    def __init__(self, local_ports, process_pid, open_files):
        self._local_ports = local_ports
        self._process_pid = process_pid
        self._open_files = open_files
        super(ProcessDetailsInfoBox, self).__init__()

    def create(self, **kwargs):
        """
        Sub widgets [details_box_heading,details_box] are only shown in GUI if
        they are created in the create() method
        """
        super(ProcessDetailsInfoBox, self).create()

        self.logger = logging.getLogger(__name__)
        self.logger.info(
            "Showing the local ports {0} and files opened and are being used by the process with pid {1}".format(
                self._local_ports, str(self._process_pid)
            )
        )
        # logger.info("Showing the local ports {0} and files opened and are being used by the process with pid {1}".format(self._local_ports,str(self._process_pid)))
        #             self.details_box_heading = self.add(npyscreen.TitleText, name='No ports used by the process {0}'.format(str(self._process_pid)),)
        self.details_box_heading = self.add(
            npyscreen.TitleText,
            name="Showing info for process with PID {0}".format(str(self._process_pid)),
        )
        self.details_box = self.add(npyscreen.BufferPager)
        if len(self._local_ports) != 0 and len(self._open_files) != 0:
            self.details_box.values.extend(["System ports used by the process are:\n"])
            self.details_box.values.extend(self._local_ports)
            self.details_box.values.extend("\n")
            self.details_box.values.extend(["Files opened by this process are:\n"])
            self.details_box.values.extend("\n")
            self.details_box.values.extend(self._open_files)
        elif len(self._open_files) != 0:
            self.details_box.values.extend(["Files opened by this process are:\n"])
            self.details_box.values.extend(self._open_files)
            self.details_box.values.extend("\n")
            self.details_box.values.extend(
                ["The process is not using any System ports.\n"]
            )
        elif len(self._local_ports) != 0:
            self.details_box.values.extend(["System ports used by the process are:\n"])
            self.details_box.values.extend(self._local_ports)
            self.details_box.values.extend("\n")
            self.details_box.values.extend(["No files are opened by this process.\n"])
        else:
            self.details_box.values.extend(
                ["No system ports are used and no files are opened by this process.\n"]
            )
        self.details_box.display()

    def adjust_widgets(self):
        pass


class ProcessFilterInputBox(npyscreen.Popup):
    """
    Helper widget(input-box) that is used for filtering the processes list
    on the basis of entered filtering string in the widget
    """

    def create(self):
        super(ProcessFilterInputBox, self).create()
        self.filterbox = self.add(
            npyscreen.TitleText,
            name="Filter String:",
        )
        self.nextrely += 1
        self.statusline = self.add(npyscreen.Textfield, color="LABEL", editable=False)

    def updatestatusline(self):
        """
        This updates the status line that displays how many processes in the
        processes list are matching to the filtering string
        """
        self.owner_widget._filter = self.filterbox.value
        total_matches = self.owner_widget.filter_processes()
        if self.filterbox.value == None or self.filterbox.value == "":
            self.statusline.value = ""
        elif total_matches == 0:
            self.statusline.value = "(No Matches)"
        elif total_matches == 1:
            self.statusline.value = "(1 Match)"
        else:
            self.statusline.value = "(%s Matches)" % total_matches

    def adjust_widgets(self):
        """
        This method is called on any text change in filter box.
        """
        self.updatestatusline()
        self.statusline.display()


class CustomMultiLineAction(npyscreen.MultiLineAction):
    """
    Making custom MultiLineAction by adding the handlers
    """

    def __init__(self, *args, **kwargs):
        super(CustomMultiLineAction, self).__init__(*args, **kwargs)
        self.add_handlers(
            {
                "^N": self._sort_by_memory,
                "^T": self._sort_by_time,
                "^K": self._kill_process,
                "^Q": self._quit,
                "^R": self._reset,
                "^H": self._do_process_filtering_work,
                "^L": self._show_detailed_process_info,
                "^F": self._do_process_filtering_work,
                "^E": self._enter_directory,  # TODO: implement with squeue stuff
            }
        )
        self._filtering_flag = False
        self.logger = logging.getLogger(__name__)
        """
            Non-sorted processes table entries, practically this will never be 
            None beacuse the user will ask for a certain process info only 
            after chossing one from the processes table
        """
        self._uncurtailed_process_data = None

    def _get_selected_process_pid(self):
        """
        Parses the process pid from the selected line in the process
        table
        """
        previous_parsed_text = ""
        for _ in self.values[self.cursor_line].split():
            if _ in SYSTEM_USERS:
                selected_process_pid = int(previous_parsed_text)
                break
            else:
                previous_parsed_text = _
        return selected_process_pid

    def _get_local_ports_used_by_a_process(self, process_pid):
        """
        Given the process_id returns the list of local ports used by
        the process
        """
        for proc in self._uncurtailed_process_data:
            if proc["id"] == process_pid:
                return proc["local_ports"]

    def _get_list_of_open_files(self, process_pid):
        """
        Given the Process ID, return the list of all the open files
        """
        opened_files_by_proces = []
        p = psutil.Process(process_pid)
        for i in p.open_files():
            opened_files_by_proces.append(i[0])
        return opened_files_by_proces

    # TODO: implement this with squeue
    def _enter_directory(self):
        pass

    def _sort_by_time(self, *args, **kwargs):
        # frick .. that's why NPSManaged was required, i.e you can access the app instance within widgets
        self.logger.info("Sorting the process table by time")
        global TIME_SORT, MEMORY_SORT
        MEMORY_SORT = False
        TIME_SORT = True
        PROCESS_RELEVANCE_SORT = False

    def _sort_by_memory(self, *args, **kwargs):
        self.logger.info("Sorting the process table by memory")
        global TIME_SORT, MEMORY_SORT
        TIME_SORT = False
        MEMORY_SORT = True
        PROCESS_RELEVANCE_SORT = False

    def _reset(self, *args, **kwargs):
        self.logger.info("Resetting the process table")
        global TIME_SORT, MEMORY_SORT
        TIME_SORT = False
        MEMORY_SORT = False
        PROCESS_RELEVANCE_SORT = True
        self._filtering_flag = False

    def _do_process_filtering_work(self, *args, **kwargs):
        """
        Dynamically instantiate a process filtering box used
        to offload the process filtering work
        """
        self.process_filtering_helper = ProcessFilterInputBox()
        self.process_filtering_helper.owner_widget = weakref.proxy(self)
        self.process_filtering_helper.display()
        self.process_filtering_helper.edit()

    def _show_detailed_process_info(self, *args, **kwargs):
        """
        Display the extra process information. Extra information includes
        open ports and the opened files list
        """
        self.logger.info("Showing process details for the selected process")
        # This is not working, local_ports information is not getting passed in the
        # create method of self.logger = logging.getLogger(__name__)
        # self.process_details_view_helper = ProcessDetailsInfoBox(local_ports=['1','2','3'])
        process_pid = self._get_selected_process_pid()
        local_ports = self._get_local_ports_used_by_a_process(process_pid)
        open_files = self._get_list_of_open_files(process_pid)
        self.process_details_view_helper = ProcessDetailsInfoBox(
            local_ports, process_pid, open_files
        )
        self.process_details_view_helper.owner_widget = weakref.proxy(self)
        self.process_details_view_helper.display()
        self.process_details_view_helper.edit()

    # _kill_process takes *args, **kwargs
    def _kill_process(self, *args, **kwargs):
        # Get the PID of the selected process
        pid_to_kill = self._get_selected_process_pid()
        self.logger.info("Terminating process with pid {0}".format(pid_to_kill))
        try:
            # Handle NoSuchProcessError
            target = psutil.Process(int(pid_to_kill))
            target.terminate()
            self.logger.info("Terminated process with pid {0}".format(pid_to_kill))
        except:
            self.logger.info(
                "Not able to terminate process with pid: {0}".format(pid_to_kill),
                exc_info=True,
            )

    def _quit(self, *args, **kwargs):
        raise KeyboardInterrupt

    def filter_processes(self):
        """
        This method is used to filter the processes in the processes table on the
        basis of the filtering string entered in the filter box
        When the user presses OK in the input box widget the value of the processes
        table is set to **filtered** processes
        It returns the count of the processes matched to the filtering string
        """
        self.logger.info(
            "Filtering processes on the basis of filter : {0}".format(self._filter)
        )
        match_count = 0
        filtered_processes = []
        self._filtering_flag = True
        for val in self.values:
            if self._filter in str.lower(val):
                match_count += 1
                filtered_processes.append(val)
        self.values = filtered_processes
        return match_count

    def is_filtering_on(self):
        return self._filtering_flag

    def set_uncurtailed_process_data(self, processes_info):
        self._uncurtailed_process_data = processes_info


class MultiLineWidget(npyscreen.BoxTitle):
    """
    A framed widget containing multiline text
    """

    _contained_widget = npyscreen.MultiLineEdit


class MultiLineActionWidget(npyscreen.BoxTitle):
    """
    A framed widget containing multiline text
    """

    _contained_widget = CustomMultiLineAction


class WindowForm(npyscreen.FormBaseNew):
    """
    Frameless Form
    """

    def create(self, *args, **kwargs):
        super(WindowForm, self).create(*args, **kwargs)

    def while_waiting(self):
        pass


class slurm_top_pythonGUI(npyscreen.NPSApp):
    """
    GUI class for slurm_top_python (SLURM Job Manager).
    This controls the rendering of the main window and acts as the registering point
    for all other widgets
    """

    def __init__(self, statistics, stop_event, sensor_refresh_rates, theme):
        self.statistics = statistics
        self.stop_event = stop_event  # Global stop event
        self.update_thread = None  # thread for updating
        self.is_user_interacting = (
            False  # Flag to check if user is interacting (not used)
        )
        self.refresh_rate = min(
            sensor_refresh_rates.values()
        )  # GUI refresh rate should be minimum of all sensor refresh rates

        # Main form
        self.window = None
        self.theme = theme

        # Widgets
        self.basic_stats = None
        self.memory_chart = None
        self.cpu_chart = None
        self.jobs_table = None  # Changed from processes_table

        # Actions bar
        self.actions = None

        self.CHART_HEIGHT = None
        self.CHART_WIDTH = None
        self.cpu_array = None
        self.memory_array = None

        # logger
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"GUI initialized")

    def while_waiting(self):
        """
        Called periodically when user is not pressing any key
        """
        self.logger.info("Updating GUI due to no keyboard interrupt")
        """
            Earlier a thread job was being used to update the GUI
            in background but while_waiting is getting called after 10ms
            (keypress_timeout_default) so no more thread job is required
            Only issue is that when user is interacting constantly the GUI
            won't update
        """
        terminal_width, terminal_height = drawille.getTerminalSize()
        self.logger.info(
            "Equating terminal sizes, old {0}*{1} vs {2}*{3}".format(
                PREVIOUS_TERMINAL_WIDTH,
                PREVIOUS_TERMINAL_HEIGHT,
                terminal_width,
                terminal_height,
            )
        )

        # In case the terminal size is changed, try resizing the terminal and redrawing slurm_top_python
        if (
            terminal_width != PREVIOUS_TERMINAL_WIDTH
            or terminal_height != PREVIOUS_TERMINAL_HEIGHT
        ):
            self.logger.info("Terminal Size changed, updating the GUI")
            self.window.erase()
            self.draw()
            self.update()
        # In case the terminal size is not changed, don't redraw the GUI, just update the contents
        else:
            self.update()

    def update(self):
        """
        Update the form in background, this used to be called inside the ThreadJob
        and but now is getting called automatically in while_waiting
        """
        try:
            disk_info = self.statistics["Disk"]["text"]["/"]
            swap_info = self.statistics["Memory"]["text"]["swap_memory"]
            memory_info = self.statistics["Memory"]["text"]["memory"]
            # This now contains SLURM job stats
            jobs_info = self.statistics["Process"]["text"]
            system_info = self.statistics["System"]["text"]
            cpu_info = self.statistics["CPU"]["graph"]
            network_info = self.statistics["Network"]["text"]

            #### Overview information ####
            # Updated to show SLURM job information instead of processes/threads
            row1 = "Disk Usage (/) {4}{0: <6}/{1: >10} MB [{2: >2}%]{5}Total Jobs{4}{3: <8}".format(
                disk_info["used"],
                disk_info["total"],
                disk_info["percentage"],
                jobs_info["total_jobs"],
                " " * int(4 * self.X_SCALING_FACTOR),
                " " * int(9 * self.X_SCALING_FACTOR),
            )

            row2 = "Swap Memory    {4}{0: <6}/{1: >10} MB [{2: >2}%]{5}Running  {4}{3: <8}".format(
                swap_info["active"],
                swap_info["total"],
                swap_info["percentage"],
                jobs_info["running_jobs"],
                " " * int(4 * self.X_SCALING_FACTOR),
                " " * int(9 * self.X_SCALING_FACTOR),
            )

            row3 = "Main Memory    {4}{0: <6}/{1: >10} MB [{2: >2}%]{5}Pending  {4}{3: <8}".format(
                memory_info["active"],
                memory_info["total"],
                memory_info["percentage"],
                jobs_info["pending_jobs"],
                " " * int(4 * self.X_SCALING_FACTOR),
                " " * int(9 * self.X_SCALING_FACTOR),
            )
            
            # TODO: make the networkspeed and nodes aligned
            row4 = "Network Speed  {4}{0: >6}↓ {1: >6}↑ MB/s{5}Nodes    {4}{2: <8}".format(
                network_info["download_speed_in_mb"],
                network_info["upload_speed_in_mb"],
                jobs_info["total_nodes"],
                " " * int(4 * self.X_SCALING_FACTOR),
                " " * int(4 * self.X_SCALING_FACTOR),
                " " * int(9 * self.X_SCALING_FACTOR),
            )


            self.basic_stats.value = f"{row1}\n{row2}\n{row3}\n{row4}"
            # Lazy update to GUI
            self.basic_stats.display()
            self.basic_stats.update(clear=True)

            #### SLURM Jobs table ####
            # This now contains SLURM job data
            self._jobs_data = self.statistics["Process"]["table"]
            self.logger.info(f"Updated slurm job data: {self._jobs_data}")

            # check sorting flags
            global TIME_SORT, MEMORY_SORT, JOB_ID_SORT  # , STATE_SORT

            if MEMORY_SORT:
                sorted_jobs_data = sorted(
                    self._jobs_data, key=lambda k: k.get("memory", 0), reverse=True
                )
                self.logger.info("Memory sorting done for jobs table")
            elif TIME_SORT:
                sorted_jobs_data = sorted(
                    self._jobs_data, key=lambda k: k.get("time", ""), reverse=True
                )
                self.logger.info("Time sorting done for jobs table")
            # elif STATE_SORT:
            #     sorted_jobs_data = sorted(
            #         self._jobs_data, key=lambda k: k.get("state", "")
            #     )
            #     self.logger.info("State sorting done for jobs table")
            elif JOB_ID_SORT:
                sorted_jobs_data = sorted(
                    self._jobs_data,
                    key=lambda k: (
                        int(k.get("id", "0")) if k.get("id", "0").isdigit() else 0
                    ),
                )
                self.logger.info("Sorting on the basis of Job ID")
            else:
                sorted_jobs_data = self._jobs_data
                self.logger.info("Resetting the sorting behavior")

            # Format job data for display
            curtailed_jobs_data = []
            for job in sorted_jobs_data:
                nodelist_reason = (
                    f"{job.get('nodelist', '')} ({job.get('reason', '')})"
                    if job.get("reason")
                    else job.get("nodelist", "")
                )

                # Truncate nodelist_reason if too long (e.g., max 30 chars, adjust as needed)
                if len(nodelist_reason) > 20:
                    nodelist_reason = nodelist_reason[:27] + "..."

                # Format: Job ID - Partition - Name - User - State - Time - Nodes - Nodelist (Reason)
                job_line = "{0: <8} {7} {1: <12} {7} {2: <20} {7} {3: <10} {7} {4: <3} {7} {5: <12} {7} {6: <5} {7} {8}".format(
                    job.get("id", "")[:8],
                    job.get("partition", "")[:12],
                    (
                        (job.get("name", "")[:17] + "...")
                        if len(job.get("name", "")) > 20
                        else job.get("name", "")
                    ),
                    job.get("user", "")[:10],
                    job.get("state", ""),
                    job.get("time", "")[:12],
                    job.get("nodes", ""),
                    " " * int(1 * self.X_SCALING_FACTOR),
                    nodelist_reason.replace("(", "").replace(")", ""),
                )
                curtailed_jobs_data.append(job_line)

            if not self.jobs_table.entry_widget.is_filtering_on():
                self.jobs_table.entry_widget.values = curtailed_jobs_data
            # Set the jobs data dictionary to uncurtailed jobs data
            self.jobs_table.entry_widget.set_uncurtailed_process_data(self._jobs_data)
            self.jobs_table.entry_widget.display()
            self.jobs_table.entry_widget.update(clear=True)

            """ This will update all the lazy updates at once, instead of .display() [fast]
                .DISPLAY()[slow] is used to avoid glitches or gibberish text on the terminal
            """
            # self.window.DISPLAY()

        # catch the friggin KeyError caused to cumbersome point of reading the stats data structures
        except KeyError as e:
            self.logger.error(
                f"Some of the stats reading failed: {str(e)}", exc_info=True
            )
        except Exception as e:
            self.logger.error(f"Error updating GUI: {str(e)}", exc_info=True)

    def draw(self):
        # Setting the main window form
        self.window = WindowForm(parentApp=self, name="SLURM Job Manager")
        MIN_ALLOWED_TERMINAL_WIDTH = 104
        MIN_ALLOWED_TERMINAL_HEIGHT = 28

        # Setting the terminal dimensions by querying the underlying curses library
        self.logger.info(
            "Detected terminal size to be {0}".format(self.window.curses_pad.getmaxyx())
        )
        global PREVIOUS_TERMINAL_HEIGHT, PREVIOUS_TERMINAL_WIDTH
        max_y, max_x = self.window.curses_pad.getmaxyx()
        PREVIOUS_TERMINAL_HEIGHT = max_y
        PREVIOUS_TERMINAL_WIDTH = max_x

        # Also make slurm_top_python exists cleanly if screen is drawn beyond the lower limit
        if max_x < MIN_ALLOWED_TERMINAL_WIDTH or max_y < MIN_ALLOWED_TERMINAL_HEIGHT:
            self.logger.info(
                f"Terminal sizes than width = {MIN_ALLOWED_TERMINAL_WIDTH} and height = {MIN_ALLOWED_TERMINAL_HEIGHT}, exiting"
            )
            sys.stdout.write(
                "slurm_top_python does not support terminals with resolution smaller than 104*28. Please resize your terminal and try again."
            )
            raise KeyboardInterrupt

        # Minimum terminal size should be used for scaling
        # $ tput cols & $ tput lines can be used for getting the terminal dimensions
        # slurm_top_python won't be reponsive beyond (cols=104, lines=27)
        self.X_SCALING_FACTOR = float(max_x) / 104
        self.Y_SCALING_FACTOR = float(max_y) / 28

        #####      Defaults            #######
        LEFT_OFFSET = 1
        TOP_OFFSET = 1

        #####      Overview widget     #######
        OVERVIEW_WIDGET_REL_X = LEFT_OFFSET
        OVERVIEW_WIDGET_REL_Y = TOP_OFFSET
        OVERVIEW_WIDGET_HEIGHT = int(5 * self.Y_SCALING_FACTOR) - 1
        OVERVIEW_WIDGET_WIDTH = PREVIOUS_TERMINAL_WIDTH - 4
        self.logger.info(
            "Trying to draw Overview information box, x1 {0} x2 {1} y1 {2} y2 {3}".format(
                OVERVIEW_WIDGET_REL_X,
                OVERVIEW_WIDGET_REL_X + OVERVIEW_WIDGET_WIDTH,
                OVERVIEW_WIDGET_REL_Y,
                OVERVIEW_WIDGET_REL_Y + OVERVIEW_WIDGET_HEIGHT,
            )
        )
        self.basic_stats = self.window.add(
            MultiLineWidget,
            name="System Overview",
            relx=OVERVIEW_WIDGET_REL_X,
            rely=OVERVIEW_WIDGET_REL_Y,
            max_height=OVERVIEW_WIDGET_HEIGHT,
            max_width=OVERVIEW_WIDGET_WIDTH,
        )
        self.basic_stats.value = ""
        self.basic_stats.entry_widget.editable = False

        ######    SLURM Jobs Info widget  #########
        JOBS_INFO_WIDGET_REL_X = LEFT_OFFSET
        JOBS_INFO_WIDGET_REL_Y = OVERVIEW_WIDGET_REL_Y + OVERVIEW_WIDGET_HEIGHT
        JOBS_INFO_WIDGET_HEIGHT = int(20 * self.Y_SCALING_FACTOR)
        JOBS_INFO_WIDGET_WIDTH = OVERVIEW_WIDGET_WIDTH
        self.logger.info(
            "Trying to draw SLURM Jobs information box, x1 {0} x2 {1} y1 {2} y2 {3}".format(
                JOBS_INFO_WIDGET_REL_X,
                JOBS_INFO_WIDGET_REL_X + JOBS_INFO_WIDGET_WIDTH,
                JOBS_INFO_WIDGET_REL_Y,
                JOBS_INFO_WIDGET_REL_Y + JOBS_INFO_WIDGET_HEIGHT,
            )
        )

        self.jobs_table = self.window.add(
            MultiLineActionWidget,
            name="SLURM Jobs [ Job ID - Partition - Job Name - User - ST - Time - Nodes - Nodelist (Reason) ]",
            relx=JOBS_INFO_WIDGET_REL_X,
            rely=JOBS_INFO_WIDGET_REL_Y,
            max_height=JOBS_INFO_WIDGET_HEIGHT,
            max_width=JOBS_INFO_WIDGET_WIDTH,
        )

        ######   Actions widget  #########
        # By default this widget takes 3 lines and 1 line for text and 2 for the invisible boundary lines
        # So (tput lines - rely) should be at least 3
        ACTIONS_WIDGET_REL_X = LEFT_OFFSET
        ACTIONS_WIDGET_REL_Y = JOBS_INFO_WIDGET_REL_Y + JOBS_INFO_WIDGET_HEIGHT
        self.logger.info(
            "Trying to draw the actions box, x1 {0} y1 {1}".format(
                ACTIONS_WIDGET_REL_X, ACTIONS_WIDGET_REL_Y
            )
        )

        self.actions = self.window.add(
            MultiLineWidget,
            relx=ACTIONS_WIDGET_REL_X,
            rely=ACTIONS_WIDGET_REL_Y,
            name="Controls",
            max_height=max(4, int(1 * self.Y_SCALING_FACTOR)),
            max_width=JOBS_INFO_WIDGET_WIDTH,
        )

        self.actions.value = "^K: Cancel Job \t ^L: Job Info \t g: Go to Top \t ^Q: Quit \n^N: Memory Sort \t ^T: Time Sort \t ^S: State Sort \t ^I: Job ID Sort \t ^F: Filter \t ^M: My Jobs"
        self.actions.display()
        self.actions.editable = False

        # add subwidgets to the parent widget
        self.window.edit()

    def main(self):
        # npyscreen.setTheme(self.theme)
        npyscreen.setTheme(npyscreen.Themes.DefaultTheme)

        # time(ms) to wait for user interactions
        self.keypress_timeout_default = 10

        if self.refresh_rate < 1000:
            self.keypress_timeout_default = int(self.refresh_rate / 100)

        self.draw()
