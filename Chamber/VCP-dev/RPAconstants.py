# --------Packet Info------
# These will define the beginning of various data packets that can be sent/received
CMD_SWP_HEADER  = 0xCA # denotes the beginning of a sweep command
CMD_ADC_HEADER  = 0xCB # denotes beginnning of adcpol command
CMD_DAC_HEADER  = 0xCC    
CMD_IDN_HEADER  = 0xCD # denotes beginnning of idn packet
DATA_ADC_HEADER  = 0xDA # denotes beginning of data packet
DATA_SWP_HEADER = 0xDB
ERROR_HEADER  = 0xEE # denotes beginning of error message
ACK_HEADER  = 0xAA # denotes beginning of acknowledgement. Used to signify that a command, error, data has been received and understood
PACKET_FOOTER  = 0xED # denotes end of any of the above packets

# Error codes
ERROR_CHECKSUM_FAIL  = 0x01  # Packet checksum mismatch
ERROR_INVALID_FRAME  = 0x02  # Missing header/footer or buffer overflow
ERROR_INVALID_PARAMS  = 0x03  # Invalid sweep parameters (0 steps, etc)
ERROR_ADC_TIMEOUT  = 0x04  # ADC did not respond
ERROR_DAC_FAILURE  = 0x05  # DAC communication failed
ERROR_OTHER  = 0x06  # Some other problem

# Acknowledgement codes
ACK_READY  = 0x00  # Device initialized and ready
ACK_SWEEP_COMPLETE  = 0x01  # Sweep execution finished
ACK_COMMAND_RECEIVED  = 0x02  # Command parsed successfully
ACK_DAC_SET  = 0x03  # DAC setting finished

# Packet lengths
SWP_PKT_LEN = 10
ADC_PKT_LEN = 6
SHORT_PKT_LEN = 3