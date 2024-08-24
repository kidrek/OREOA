import logging, os, re

# sources : https://www.tutorialspoint.com/file-searching-using-python

global donePaths
global result

donePaths = []
def find_directory(pattern, search_path):
   for paths,dirs,files in os.walk(search_path):
      if paths not in donePaths:
         if dirs:
            for ele2 in dirs:
               absPath = os.path.join(paths,ele2)
               logging.info(pattern)
               logging.info(absPath)
               if re.search(pattern, absPath, re.IGNORECASE):
                  logging.info("MATCH")
                  return absPath
               else:
                  find_directory(pattern, absPath)
                  # adding the paths to the list that got traversed 
                  donePaths.append(absPath)


def init(pattern, filepath):
   test = find_directory(pattern,filepath)
   logging.info(f"Resultat intermediaire : {test}")
   return test



"""
EVTX_LOCATION_PATTERN=['System32/winevt/Logs']
dir_evtx=[]
print('Test')
for pattern in EVTX_LOCATION_PATTERN:
   res = init(pattern, "/home/kidrek/Documents/scripts/PCSIRT/PCSIRT_sources/scans_output/collection-mlap-0dvjoxddca_mgsi_mg_com_fr-2024-08-12t12_36_13_02_00--copy-.zip_extracted")
   dir_evtx = dir_evtx + res
print(dir_evtx)
"""