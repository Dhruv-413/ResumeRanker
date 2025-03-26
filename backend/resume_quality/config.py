WEIGHTS = {
    "required_skills": 0.3,
    "preferred_skills": 0.2,
    "experience": 0.15,
    "education": 0.1,
    "keywords": 0.05,
    "structure": 0.05,
    "projects": 0.05,
    "certifications": 0.1
}

SKILL_SYNONYMS = {
    "js": "javascript",
    "react.js": "react",
    "ai": "artificial intelligence",
    "ml": "machine learning",
    "py": "python",
    "c++": "cpp",
    "node.js": "node",
    "ts": "typescript",
    "dl": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "dbms": "database management systems",
    "sql": "structured query language",
    "nosql": "non-relational database",
    "ui": "user interface",
    "ux": "user experience",
    "k8s": "kubernetes",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "azure": "microsoft azure",
    "devops": "development operations",
    "qa": "quality assurance",
    "dsa": "data structures and algorithms",
    "data science": "ds",
    "pytorch": "torch",
    "tensorflow": "tf",
    "flask": "python flask",
    "django": "python django",
    "html5": "html",
    "css3": "css",
    "seo": "search engine optimization",
    "scrapy": "web scraping",
    "swift": "ios development",
    "kotlin": "android development",
    "flutter": "dart flutter",
    "php": "hypertext preprocessor",
    "go": "golang",
    "rust": "rustlang",
    "blockchain": "distributed ledger",
    "smart contracts": "ethereum development"
}

CERT_DATABASE = {
    "aws": [
        "AWS Certified Solutions Architect – Associate",
        "AWS Certified Solutions Architect – Professional",
        "AWS Certified Developer – Associate",
        "AWS Certified DevOps Engineer – Professional",
        "AWS Certified SysOps Administrator – Associate",
        "AWS Certified Advanced Networking – Specialty",
        "AWS Certified Security – Specialty",
        "AWS Certified Machine Learning – Specialty",
        "AWS Certified Data Analytics – Specialty",
        "AWS Certified Database – Specialty"
    ],
    "pmp": [
        "Project Management Professional (PMP)",
        "Certified Associate in Project Management (CAPM)",
        "Program Management Professional (PgMP)",
        "Portfolio Management Professional (PfMP)",
        "PMI Agile Certified Practitioner (PMI-ACP)",
        "PMI Risk Management Professional (PMI-RMP)",
        "PMI Scheduling Professional (PMI-SP)"
    ],
    "cisco": [
        "Cisco Certified Network Associate (CCNA)",
        "Cisco Certified Network Professional (CCNP)",
        "Cisco Certified Internetwork Expert (CCIE)",
        "Cisco Certified Design Associate (CCDA)",
        "Cisco Certified Design Professional (CCDP)",
        "Cisco Certified DevNet Associate",
        "Cisco Certified DevNet Professional"
    ],
    "google": [
        "Google Cloud Digital Leader",
        "Google Associate Cloud Engineer",
        "Google Professional Cloud Architect",
        "Google Professional Data Engineer",
        "Google Professional Cloud Developer",
        "Google Professional Cloud Network Engineer",
        "Google Professional Cloud Security Engineer",
        "Google Professional Collaboration Engineer",
        "Google Professional Machine Learning Engineer"
    ],
    "microsoft": [
        "Microsoft Certified: Azure Fundamentals",
        "Microsoft Certified: Azure Administrator Associate",
        "Microsoft Certified: Azure Developer Associate",
        "Microsoft Certified: Azure Solutions Architect Expert",
        "Microsoft Certified: Azure DevOps Engineer Expert",
        "Microsoft Certified: Azure Security Engineer Associate",
        "Microsoft Certified: Azure Data Scientist Associate",
        "Microsoft Certified: Azure AI Engineer Associate",
        "Microsoft Certified: Azure Data Engineer Associate",
        "Microsoft Certified: Azure IoT Developer Specialty"
    ],
    "compTIA": [
        "CompTIA A+",
        "CompTIA Network+",
        "CompTIA Security+",
        "CompTIA Cloud+",
        "CompTIA Linux+",
        "CompTIA Server+",
        "CompTIA CySA+ (Cybersecurity Analyst)",
        "CompTIA PenTest+",
        "CompTIA CASP+ (Advanced Security Practitioner)"
    ],
    "isc2": [
        "Certified Information Systems Security Professional (CISSP)",
        "Certified Cloud Security Professional (CCSP)",
        "Certified Authorization Professional (CAP)",
        "Certified Secure Software Lifecycle Professional (CSSLP)",
        "Systems Security Certified Practitioner (SSCP)",
        "Healthcare Information Security and Privacy Practitioner (HCISPP)"
    ],
    "isaca": [
        "Certified Information Systems Auditor (CISA)",
        "Certified Information Security Manager (CISM)",
        "Certified in Risk and Information Systems Control (CRISC)",
        "Certified in the Governance of Enterprise IT (CGEIT)"
    ],
    "scrum": [
        "Certified ScrumMaster (CSM)",
        "Certified Scrum Product Owner (CSPO)",
        "Certified Scrum Developer (CSD)",
        "Advanced Certified ScrumMaster (A-CSM)",
        "Advanced Certified Scrum Product Owner (A-CSPO)",
        "Certified Scrum Professional (CSP)"
    ],
    "six_sigma": [
        "Six Sigma Yellow Belt",
        "Six Sigma Green Belt",
        "Six Sigma Black Belt",
        "Six Sigma Master Black Belt"
    ],
    "prince2": [
        "PRINCE2 Foundation",
        "PRINCE2 Practitioner",
        "PRINCE2 Agile Foundation",
        "PRINCE2 Agile Practitioner"
    ],
    "itil": [
        "ITIL Foundation",
        "ITIL Practitioner",
        "ITIL Intermediate",
        "ITIL Expert",
        "ITIL Master"
    ],
    "vmware": [
        "VMware Certified Technical Associate (VCTA)",
        "VMware Certified Professional (VCP)",
        "VMware Certified Advanced Professional (VCAP)",
        "VMware Certified Design Expert (VCDX)"
    ],
    "red_hat": [
        "Red Hat Certified System Administrator (RHCSA)",
        "Red Hat Certified Engineer (RHCE)",
        "Red Hat Certified Architect (RHCA)"
    ],
    "oracle": [
        "Oracle Certified Associate (OCA)",
        "Oracle Certified Professional (OCP)",
        "Oracle Certified Master (OCM)"
    ],
    "salesforce": [
        "Salesforce Certified Administrator",
        "Salesforce Certified Advanced Administrator",
        "Salesforce Certified Platform App Builder",
        "Salesforce Certified Sales Cloud Consultant",
        "Salesforce Certified Service Cloud Consultant",
        "Salesforce Certified Technical Architect"
    ],
    "citrix": [
        "Citrix Certified Associate – Virtualization (CCA-V)",
        "Citrix Certified Professional – Virtualization (CCP-V)",
        "Citrix Certified Expert – Virtualization (CCE-V)"
    ],
    "palo_alto": [
        "Palo Alto Networks Certified Cybersecurity Associate (PCCSA)",
        "Palo Alto Networks Certified Network Security Administrator (PCNSA)",
        "Palo Alto Networks Certified Network Security Engineer (PCNSE)"
    ],
    "checkpoint": [
        "Check Point Certified Security Administrator (CCSA)",
        "Check Point Certified Security Expert (CCSE)",
        "Check Point Certified Master Architect (CCMA)"
    ],
    "juniper": [
        "Juniper Networks Certified Associate (JNCIA)",
        "Juniper Networks Certified Specialist (JNCIS)",
        "Juniper Networks Certified Professional (JNCIP)",
        "Juniper Networks Certified Expert (JNCIE)"
    ],
    "linux": [
        "Linux Professional Institute Certification Level 1 (LPIC-1)",
        "Linux Professional Institute Certification Level 2 (LPIC-2)",
        "Linux Professional Institute Certification Level 3 (LPIC-3)"
    ],
    "ceh": [
        "Certified Ethical Hacker (CEH)"
    ],
    "cissp": [
        "Certified Information Systems Security Professional (CISSP)"
    ],
    "cisa": [
        "Certified Information Systems Auditor (CISA)"
    ],
    "cism": [
        "Certified Information Security Manager (CISM)"
    ],
    "crisc": [
        "Certified in Risk and Information Systems Control (CRISC)"
    ],
    "cgeit": [
        "Certified in the Governance of Enterprise IT (CGEIT)"
    ],
    "aws_security": [
        "AWS Certified Security – Specialty"
    ],
    "aws_ml": [
        "AWS Certified Machine Learning – Specialty"
    ],
    "aws_data_analytics": [
        "AWS Certified Data Analytics – Specialty"
    ],
    "aws_database": [
        "AWS Certified Database – Specialty"
    ],
    "google_ml": [
        "Google Professional Machine Learning Engineer"
    ],
    "google_security": [
        "Google Professional Cloud Security Engineer"
    ],
    "google_network": [
        "Google Professional Cloud Network Engineer"
    ],
    "google_dev": [
        "Google Professional Cloud Developer"
    ],
    "nptel": [
        "NPTEL Certification in Data Science for Engineers",
        "NPTEL Certification in Programming in Java",
        "NPTEL Certification in Introduction to Machine Learning",
        "NPTEL Certification in Advanced Computer Architecture",
        "NPTEL Certification in Cloud Computing",
        "NPTEL Certification in Artificial Intelligence: Search Methods for Problem Solving",
        "NPTEL Certification in Deep Learning",
        "NPTEL Certification in Internet of Things",
        "NPTEL Certification in Blockchain and its Applications",
        "NPTEL Certification in Cyber Security",
        "NPTEL Certification in Software Engineering",
        "NPTEL Certification in Database Management System",
        "NPTEL Certification in Operating System Fundamentals",
        "NPTEL Certification in Computer Networks and Internet Protocol",
        "NPTEL Certification in Web Application Development",
        "NPTEL Certification in Mobile Application Development",
        "NPTEL Certification in Natural Language Processing",
        "NPTEL Certification in Big Data Computing",
        "NPTEL Certification in Foundations of Data Structures",
        "NPTEL Certification in Design and Analysis of Algorithms",
        "NPTEL Certification in Compiler Design",
        "NPTEL Certification in Digital Image Processing",
        "NPTEL Certification in Introduction to Industry 4.0 and Industrial Internet of Things",
        "NPTEL Certification in Cloud Computing and Distributed Systems",
        "NPTEL Certification in Introduction to Robotics",
        "NPTEL Certification in Computer Vision",
        "NPTEL Certification in Reinforcement Learning",
        "NPTEL Certification in Quantum Computing",
        "NPTEL Certification in Parallel Programming in OpenMP",
        "NPTEL Certification in Introduction to Soft Computing",
        "NPTEL Certification in Cryptography and Network Security",
        "NPTEL Certification in Social Networks",
        "NPTEL Certification in Information Security - IV",
        "NPTEL Certification in Data Mining",
        "NPTEL Certification in Introduction to Internet of Things",
        "NPTEL Certification in Cloud Computing",
        "NPTEL Certification in Blockchain and its Applications",
        "NPTEL Certification in Cyber Security",
        "NPTEL Certification in Software Engineering",
        "NPTEL Certification in Database Management System",
        "NPTEL Certification in Operating System Fundamentals",
        "NPTEL Certification in Computer Networks and Internet Protocol",
        "NPTEL Certification in Web Application Development",
        "NPTEL Certification in Mobile Application Development",
        "NPTEL Certification in Natural Language Processing",
        "NPTEL Certification in Big Data Computing",
        "NPTEL Certification in Foundations of Data Structures",
        "NPTEL Certification in Design and Analysis of Algorithms",
        "NPTEL Certification in Compiler Design",
        "NPTEL Certification in Digital Image Processing",
        "NPTEL Certification in Introduction to Industry 4.0 and Industrial Internet of Things",
        "NPTEL Certification in Cloud Computing and Distributed Systems",
        "NPTEL Certification in Introduction to Robotics",
        "NPTEL Certification in Computer Vision",
        "NPTEL Certification in Reinforcement Learning",
        "NPTEL Certification in Quantum Computing",
        "NPTEL Certification in Parallel Programming in OpenMP",
        "NPTEL Certification in Introduction to Soft Computing",
        "NPTEL Certification in Cryptography and Network Security",
        "NPTEL Certification in Social Networks",
        "NPTEL Certification in Information Security - IV",
        "NPTEL Certification in Data Mining"
        "Certification in Design and Analysis of Algorithms"
        "Elite Certificate in Data Structures & Algorithms (DSA)"
        ],
    }