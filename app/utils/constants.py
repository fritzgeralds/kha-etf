CONTACT_ROLE = [
    'CASE MANAGER',
    'PHARM D',
    'SOCIAL WORKER',
    'PROVIDER',
    'OTHER'
]

DISENROLLMENT_REASON = {
    'WM': 'Member is well-managed and not in need of services',
    'DP': 'Member declined to participate',
    'UE': 'Unable to engage the Member',
    'UBE': 'Unsafe behavior or environment',
    'EXP': 'Member is deceased',
    'NE': 'Member is not enrolled in Medi-Cal at MCP',
    'OH': 'Member’s Medi-Cal eligibility is on hold or termed',
    'CAP': 'Provider does not have capacity for new Members',
    'ERR': 'Member information is incorrect',
    'OTH': 'Other reason as further specified',
    'SC': 'Successfully Completed',
    'DNC': 'Data not collected'
}

ATTEMPT_RESULT = [
    'CONTACTED - CALL WAS COMPLETED',
    'UTC(UNABLE TO CONTACT) - ATTEMPTS HAVE BEEN MADE TO CONTACT CLIENT WITHOUT SUCCESS'
]

ATTEMPT_UNSUCCESFUL_DISPOSITION = [
    'NO ANSWER',
    'VOICEMAIL',
    'LEFT MESSAGE WITH 3RD PARTY',
    'WRONG PHONE NUMBER',
    'DISCONNECTED NUMBER',
    'BUSY SIGNAL'
]

ATTEMPT_SUCCESFUL_DISPOSITION = [
    'DECLINED SERVICES',
    'WELL MANAGED',
    'DUPLICATIVE PROGRAM',
    'UNSAFE BEHAVIOR/ENVIRONMENT',
    'KHS DISENROLLED',
    'Program Enrolled',
    'Program Ineligible'
]
