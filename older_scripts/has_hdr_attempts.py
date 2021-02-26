
'''not working, none of 'em'''

def get_shape(filename):
    
    sheet = open(filename , "rb")
    sample1 = sheet.read(1)
    sample2 = sheet.read(1024)
    
    try:
        hdr_csv1 = csv.Sniffer().has_header(sample1)
    except:
        hdr_csv1 = 'failed'
    try:
        hdr_csv2 = csv.Sniffer().has_header(sample2)
    except:
        hdr_csv2 = 'failed'
    try:
        hdr_bytes1 = sample1 not in '.-0123456789'
    except:
        hdr_bytes1 = 'failed'
    try:
        hdr_bytes2 = sample2 not in '.-0123456789'
    except:
        hdr_bytes2 = 'failed'
    try:
        hdr_bytes_even1 = evenodd_col(sheet)[0].read(1) not in '.-0123456789'
    except:
        hdr_bytes_even1 = 'failed'
    try:
        hdr_bytes_even2 = evenodd_col(sheet)[0].read(1024) not in '.-0123456789'
    except:
        hdr_bytes_even2 = 'failed'
    try:
        hdr_bytes_odd1 = evenodd_col(sheet)[1].read(1) not in '.-0123456789'
    except:
        hdr_bytes_odd1 ='failed'
    try:
        hdr_bytes_odd2 = evenodd_col(sheet)[1].read(1024) not in '.-0123456789'
    finally:
        hdr = None
    return df(tuple(zip(hdr_csv1, hdr_csv2, hdr_bytes1, hdr_bytes2,
                        hdr_bytes_even1, hdr_bytes_even2,
                        hdr_bytes_odd1, hdr_bytes_odd2)))
                        
def get_shape(filename):
    
    sheet = open(filename , "rb")
    sample1 = sheet.read(1)
    sample2 = sheet.read(1024)
    
    try:
        hdr_csv1 = csv.Sniffer().has_header(sample1)
    except:
        hdr_csv1 = 'failed'
    try:
        hdr_csv2 = csv.Sniffer().has_header(sample2)
    except:
        hdr_csv2 = 'failed'
    try:
        hdr_bytes1 = sample1 not in '.-0123456789'
    except:
        hdr_bytes1 = 'failed'
    try:
        hdr_bytes2 = sample2 not in '.-0123456789'
    except:
        hdr_bytes2 = 'failed'
    try:
        hdr_bytes_even1 = evenodd_col(sheet)[0].read(1) not in '.-0123456789'
    except:
        hdr_bytes_even1 = 'failed'
    try:
        hdr_bytes_even2 = evenodd_col(sheet)[0].read(1024) not in '.-0123456789'
    except:
        hdr_bytes_even2 = 'failed'
    try:
        hdr_bytes_odd1 = evenodd_col(sheet)[1].read(1) not in '.-0123456789'
    except:
        hdr_bytes_odd1 ='failed'
    try:
        hdr_bytes_odd2 = evenodd_col(sheet)[1].read(1024) not in '.-0123456789'
    finally:
        hdr = None
    return df(tuple(zip(hdr_csv1, hdr_csv2, hdr_bytes1, hdr_bytes2,
                        hdr_bytes_even1, hdr_bytes_even2,
                        hdr_bytes_odd1, hdr_bytes_odd2)))                        