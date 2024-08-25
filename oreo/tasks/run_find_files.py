import logging, os, shlex, subprocess


def find_files(pattern, search_path):
      fdfind_command = [
         'fdfind', 
         '-a', 
         '-i', 
         '-e', pattern,
         '--full-path', search_path,
         '-x', 'dirname', '{}'
      ]

      try: 
         result = (subprocess.check_output(
            shlex.join(fdfind_command) + ' | ' +
            shlex.join(['sort', '-n']) + '|' +
            shlex.join(['uniq']),
            shell=True
         ).decode('utf-8'))
      except subprocess.CalledProcessError as e:
         print(f"Error: {e.stderr}")
         raise e
      
      directories = []
      for dir in result.split('\n'):
         if len(dir) > 0:
            directories.append(dir)
      return directories


"""
EVTX_PATTERN='.evtx'
result = find_files(EVTX_PATTERN, "/home/kidrek/Documents/scripts/PCSIRT/PCSIRT_sources/scans_output/winevtsystem32--copy-.zip_extracted")
print(result)
"""