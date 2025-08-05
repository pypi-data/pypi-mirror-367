'''
| Author:   Ezio416
| Created:  2025-08-04
| Modified: 2025-08-05

- Variables that be changed and used project-wide
- You don't need to import this module - simply access these from the main module like `nadeo_api.<variable>`
'''

debug_logging:            bool = False
_last_request_timestamp:  int  = 0
wait_between_requests_ms: int  = 1000
