
from bagpy import bagreader
from rosbag.bag import BagMessage
import rosbag
import pandas as pd
from io import StringIO
"""
Utility functions for working with ROS bags in memory.
This module provides a subclass of `bagreader` that allows for
message extraction without writing to disk, suitable for cloud environments.
This is particularly useful for environments like AWS Lambda where
disk I/O can be slow or limited.
This module is designed to work with ROS bags and provides methods
to extract messages by topic, convert them to pandas DataFrames,
and return them as CSV strings or bytes for easy upload to cloud storage.
"""


def slotvalues(m: BagMessage, slot: str):
    """
    Helper function to extract values and column names from message slots.
    Parameters
    ----------
    m : BagMessage
        The ROS bag message object.
    slot : str
        The slot name to extract values from.
    Returns
    -------
    tuple
        A tuple containing the values and the corresponding slot names.
    Raises
    ------
    AttributeError
        If the slot does not exist in the message.
    """
    vals = getattr(m, slot)
    try:
        slots = vals.__slots__
        varray = []
        sarray = []
        for s in slots:
            vnew, snew = slotvalues(vals, s)       
            if isinstance(snew, list):
                for i, snn in enumerate(snew):
                    sarray.append(slot + '.' + snn)
                    varray.append(vnew[i])
            elif isinstance(snew, str):
                sarray.append(slot + '.' + snew)
                varray.append(vnew)    
                
        return varray, sarray
    except AttributeError:
        return vals, slot

class MemoryBagReader(bagreader):
    """
    Subclass of bagreader that provides memory-based message extraction
    to avoid disk writes for cloud/lambda environments.
    """
    
    def __init__(self, bagfile: str, delimiter: str = ",", verbose: bool = False):
        """
        Initialize MemoryBagReader without creating data folders.
        
        Parameters
        ----------
        bagfile : str
            Path to the bag file
        delimiter : str
            Delimiter for CSV output (default: ",")
        verbose : bool
            Enable verbose output (default: False)
        """
        # Call parent init but prevent folder creation
        self.bagfile = bagfile
        self.delimiter = delimiter
        self.verbose = verbose
        
        # Extract filename and directory without creating folders
        slashindices = [i for i, ltr in enumerate(bagfile) if ltr == '/']
        
        if len(slashindices) > 0:
            self.filename = bagfile[slashindices[-1]:]
            self.dir = bagfile[slashindices[0]:slashindices[-1]]
        else:
            self.filename = bagfile
            self.dir = './'

        # Initialize the rosbag reader
        self.reader = rosbag.Bag(self.bagfile)

        # Get bag info
        info = self.reader.get_type_and_topic_info() 
        self.topic_tuple = info.topics.values()
        self.topics = info.topics.keys()

        self.message_types = []
        for t1 in self.topic_tuple: 
            self.message_types.append(t1.msg_type)

        self.n_messages = []
        for t1 in self.topic_tuple: 
            self.n_messages.append(t1.message_count)

        self.frequency = []
        for t1 in self.topic_tuple: 
            self.frequency.append(t1.frequency)

        self.topic_table = pd.DataFrame(
            list(zip(self.topics, self.message_types, self.n_messages, self.frequency)), 
            columns=['Topics', 'Types', 'Message Count', 'Frequency']
        )

        self.start_time = self.reader.get_start_time()
        self.end_time = self.reader.get_end_time()

        # Set datafolder path but don't create it
        self.datafolder = bagfile[0:-4]
        
        # Don't create the folder - this is the key difference from parent class
        if self.verbose:
            print(f"[INFO] MemoryBagReader initialized for {self.bagfile} without creating data folder")
    
    def message_by_topic_memory(self, topic: str) -> pd.DataFrame:
        """
        Extract messages from ROS bag by topic name without writing to disk.
        Returns a pandas DataFrame directly.
        
        This method closely follows the logic from the original bagreader.message_by_topic
        but creates a DataFrame directly instead of writing to CSV.
        
        Parameters
        ----------
        topic : str
            Topic from which to extract messages.
            
        Returns
        -------
        pandas.DataFrame
            DataFrame containing the extracted message data.
        """
        msg_list = []
        tstart = None
        tend = None
        time = []
        
        for topic_name, msg, t in self.reader.read_messages(topics=topic, start_time=tstart, end_time=tend):
            time.append(t)
            msg_list.append(msg)

        msgs = msg_list

        if len(msgs) == 0:
            if self.verbose:
                print(f"No data on the topic: {topic}")
            return pd.DataFrame()

        # Set column names from the slots - using the same logic as original bagreader
        cols = ["Time"]
        m0 = msgs[0]
        slots = m0.__slots__
        for s in slots:
            v, s_names = slotvalues(m0, s)
            if isinstance(v, tuple):
                snew_array = [] 
                p = list(range(0, len(v)))
                snew_array = [s_names + "_" + str(pelem) for pelem in p]
                s_names = snew_array
            
            if isinstance(s_names, list):
                for i, s1 in enumerate(s_names):
                    cols.append(s1)
            else:
                cols.append(s_names)
        
        # Create data rows - using the same logic as original bagreader
        data_rows = []
        for i, m in enumerate(msgs):
            slots = m.__slots__
            vals = []
            vals.append(time[i].secs + time[i].nsecs*1e-9)
            for s in slots:
                v, s_names = slotvalues(m, s)
                if isinstance(v, tuple):
                    snew_array = [] 
                    p = list(range(0, len(v)))
                    snew_array = [s_names + "_" + str(pelem) for pelem in p]
                    s_names = snew_array

                if isinstance(s_names, list):
                    for j, s1 in enumerate(s_names):
                        vals.append(v[j])
                else:
                    vals.append(v)
            data_rows.append(vals)
        
        # Create DataFrame directly
        df = pd.DataFrame(data_rows, columns=cols)
        return df
    
    def message_by_topic_csv_memory(self, topic: str) -> str:
        """
        Extract messages and return as CSV string in memory.
        
        Parameters
        ----------
        topic : str
            Topic from which to extract messages.
            
        Returns
        -------
        str
            CSV string representation of the data.
        """
        df = self.message_by_topic_memory(topic)
        if df.empty:
            return ""
        
        # Convert to CSV string
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, sep=self.delimiter)
        return csv_buffer.getvalue()
    
    def message_by_topic_bytes(self, topic: str) -> bytes:
        """
        Extract messages and return as bytes (for S3 upload).
        
        Parameters
        ----------
        topic : str
            Topic from which to extract messages.
            
        Returns
        -------
        bytes
            CSV data as bytes.
        """
        csv_string = self.message_by_topic_csv_memory(topic)
        return csv_string.encode('utf-8')
    
    def close(self):
        """Close the bag reader."""
        if hasattr(self, 'reader'):
            self.reader.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()