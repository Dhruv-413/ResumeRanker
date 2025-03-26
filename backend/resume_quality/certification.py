import re
from .config import  CERT_DATABASE

def validate_certifications(text, required_certs):
    found_certs = []
    for cert_type, cert_names in CERT_DATABASE.items():
        for name in cert_names:
            if re.search(rf'\b{re.escape(name)}\b', text, re.IGNORECASE):
                found_certs.append(name)
    
    valid_certs = [cert for cert in found_certs if cert in required_certs]
    return {
        "found": found_certs,
        "valid": valid_certs,
        "score": len(valid_certs)/len(required_certs)*100 if required_certs else 100
    }

