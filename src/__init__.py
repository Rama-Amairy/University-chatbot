import logging

# Suppress specific loggers
suppress_loggers = [
    "dotenv",
    "HuggingFace",
    "requests",
    "urllib3",          
    "httpx",            
    "langchain",        
]

for logger_name in suppress_loggers:
    logging.getLogger(logger_name).setLevel(logging.ERROR)