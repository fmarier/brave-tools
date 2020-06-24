#!/usr/bin/env python3
# -*- mode: python -*-
#
# Parser for the Compact Policies in the now-obsolete P3P specification:
# https://www.w3.org/TR/P3P/#compact_policies
#
# Example usage:
#
#  ./p3p-parser.py "CAO DSP COR CUR ADM DEV TAI PSA PSD IVAi IVDi CONi TELo OTPi OUR DELi SAMi OTRi UNRi PUBi IND PHY ONL UNI PUR FIN COM NAV INT DEM CNT STA POL HEA PRE LOC GOV"

import argparse
import sys


ACCESS_TOKENS = {
    "NOI": "Web site does not collect identified data.",
    "ALL": "All Identified Data: access is given to all identified data.",
    "CAO": "Identified Contact Information and Other Identified Data: access is given to identified online and physical contact information as well as to certain other identified data.",
    "IDC": "Identifiable Contact Information: access is given to identified online and physical contact information (e.g., users can access things such as a postal address).",
    "OTI": "Other Identified Data: access is given to certain other identified data (e.g., users can access things such as their online account charges).",
    "NON": "None: no access to identified data is given.",
}

REMEDY_TOKENS = {
    "COR": "Errors or wrongful actions arising in connection with the privacy policy will be remedied by the service.",
    "MON": "If the service provider violates its privacy policy it will pay the individual an amount specified in the human readable privacy policy or the amount of damages.",
    "LAW": "Remedies for breaches of the policy statement will be determined based on the law referenced in the human readable description.",
}

PURPOSE_TOKENS = {
    "CUR": "Completion and Support of Activity For Which Data Was Provided: Information may be used by the service provider to complete the activity for which it was provided, whether a one-time activity such as returning the results from a Web search, forwarding an email message, or placing an order; or a recurring activity such as providing a subscription service, or allowing access to an online address book or electronic wallet.",
    "ADM": "Web Site and System Administration: Information may be used for the technical support of the Web site and its computer system. This would include processing computer account information, information used in the course of securing and maintaining the site, and verification of Web site activity by the site or its agents.",
    "DEV": "Research and Development: Information may be used to enhance, evaluate, or otherwise review the site, service, product, or market. This does not include personal information used to tailor or modify the content to the specific individual nor information used to evaluate, target, profile or contact the individual.",
    "TAI": "One-time Tailoring: Information may be used to tailor or modify content or design of the site where the information is used only for a single visit to the site and not used for any kind of future customization. For example, an online store might suggest other items a visitor may wish to purchase based on the items he has already placed in his shopping basket.",
    "PSA": "Pseudonymous Analysis: Information may be used to create or build a record of a particular individual or computer that is tied to a pseudonymous identifier, without tying identified data (such as name, address, phone number, or email address) to the record. This profile will be used to determine the habits, interests, or other characteristics of individuals for purpose of research, analysis and reporting, but it will not be used to attempt to identify specific individuals. For example, a marketer may wish to understand the interests of visitors to different portions of a Web site.",
    "PSD": "Pseudonymous Decision: Information may be used to create or build a record of a particular individual or computer that is tied to a pseudonymous identifier, without tying identified data (such as name, address, phone number, or email address) to the record. This profile will be used to determine the habits, interests, or other characteristics of individuals to make a decision that directly affects that individual, but it will not be used to attempt to identify specific individuals. For example, a marketer may tailor or modify content displayed to the browser based on pages viewed during previous visits.",
    "IVA": "Individual Analysis: Information may be used to determine the habits, interests, or other characteristics of individuals and combine it with identified data for the purpose of research, analysis and reporting. For example, an online Web site for a physical store may wish to analyze how online shoppers make offline purchases.",
    "IVD": "Individual Decision: Information may be used to determine the habits, interests, or other characteristics of individuals and combine it with identified data to make a decision that directly affects that individual. For example, an online store suggests items a visitor may wish to purchase based on items he has purchased during previous visits to the Web site.",
    "CON": "Contacting Visitors for Marketing of Services or Products: Information may be used to contact the individual, through a communications channel other than voice telephone, for the promotion of a product or service. This includes notifying visitors about updates to the Web site. This does not include a direct reply to a question or comment or customer service for a single transaction. In addition, this does not include marketing via customized Web content or banner advertisements embedded in sites the user is visiting.",
    "HIS": "Historical Preservation: Information may be archived or stored for the purpose of preserving social history as governed by an existing law or policy.",
    "TEL": "Contacting Visitors for Marketing of Services or Products Via Telephone: Information may be used to contact the individual via a voice telephone call for promotion of a product or service. This does not include a direct reply to a question or comment or customer service for a single transaction.",
    "OTP": "Other Uses: Information may be used in other ways not captured by the above definitions.",
}

RECIPIENT_TOKENS = {
    "OUR": "Ourselves and/or entities acting as our agents or entities for whom we are acting as an agent: An agent in this instance is defined as a third party that processes data only on behalf of the service provider for the completion of the stated purposes.",
    "DEL": "Delivery services possibly following different practices: Legal entities performing delivery services that may use data for purposes other than completion of the stated purpose. This should also be used for delivery services whose data practices are unknown.",
    "SAM": "Legal entities following our practices: Legal entities who use the data on their own behalf under equable practices.",
    "UNR": "Unrelated third parties: Legal entities whose data usage practices are not known by the original service provider.",
    "PUB": "Public fora: Public fora such as bulletin boards, public directories, or commercial CD-ROM directories.",
    "OTR": "Legal entities following different practices: Legal entities that are constrained by and accountable to the original service provider, but may use the data in a way not specified in the service provider's practices.",
}

RETENTION_TOKENS = {
    "NOR": "Information is not retained for more than a brief period of time necessary to make use of it during the course of a single online interaction. Information MUST be destroyed following this interaction and MUST NOT be logged, archived, or otherwise stored.",
    "STP": "For the stated purpose: Information is retained to meet the stated purpose.",
    "LEG": "As required by law or liability under applicable law: Information is retained to meet a stated purpose, but the retention period is longer because of a legal requirement or liability.",
    "BUS": "Determined by service provider's business practice: Information is retained under a service provider's stated business practices.",
    "IND": "Indefinitely: Information is retained for an indeterminate period of time.",
}

CATEGORY_TOKENS = {
    "PHY": "Physical Contact Information: Information that allows an individual to be contacted or located in the physical world -- such as telephone number or address.",
    "ONL": "Online Contact Information: Information that allows an individual to be contacted or located on the Internet -- such as email. Often, this information is independent of the specific computer used to access the network.",
    "UNI": "Unique Identifiers: Non-financial identifiers, excluding government-issued identifiers, issued for purposes of consistently identifying or recognizing the individual. These include identifiers issued by a Web site or service.",
    "PUR": "Purchase Information: Information actively generated by the purchase of a product or service, including information about the method of payment.",
    "FIN": "Financial Information: Information about an individual's finances including account status and activity information such as account balance, payment or overdraft history, and information about an individual's purchase or use of financial instruments including credit or debit card information. Information about a discrete purchase by an individual, as described in \"Purchase Information,\" alone does not come under the definition of \"Financial Information.\"",
    "COM": "Computer Information: Information about the computer system that the individual is using to access the network -- such as the IP number, domain name, browser type or operating system.",
    "NAV": "Navigation and Click-stream Data: Data passively generated by browsing the Web site -- such as which pages are visited, and how long users stay on each page.",
    "INT": "Interactive Data: Data actively generated from or reflecting explicit interactions with a service provider through its site -- such as queries to a search engine, or logs of account activity.",
    "DEM": "Demographic and Socioeconomic Data: Data about an individual's characteristics -- such as gender, age, and income.",
    "CNT": "Content : The words and expressions contained in the body of a communication -- such as the text of email, bulletin board postings, or chat room communications.",
    "STA": "State Management Mechanisms: Mechanisms for maintaining a stateful session with a user or automatically recognizing users who have visited a particular site or accessed particular content previously -- such as HTTP cookies.",
    "POL": "Political Information: Membership in or affiliation with groups such as religious organizations, trade unions, professional associations, political parties, etc.",
    "HEA": "Health Information: information about an individual's physical or mental health, sexual orientation, use or inquiry into health care services or products, and purchase of health care services or products.",
    "PRE": "Preference Data: Data about an individual's likes and dislikes -- such as favorite color or musical tastes.",
    "LOC": "Location Data: Information that can be used to identify an individual's current physical location and track them as their location changes -- such as GPS position data.",
    "GOV": "Government-issued Identifiers: Identifiers issued by a government for purposes of consistently identifying the individual.",
    "OTC": "Other: Other types of data not captured by the above definitions.",
}

REQUIRED_CODES = {
    "a": "always required",
    "i": "opt-in",
    "o": "opt-out",
}


# https://www.w3.org/TR/P3P/#required
def parse_required(required):
    if not required:
        # This is the default when no required attribute is present.
        required = 'a'

    if required not in REQUIRED_CODES:
        return 'ERROR: invalid required code'

    return REQUIRED_CODES[required]


def print_bullets(codes, explanations, include_required):
    for code in codes:
        token = code[0:3]

        extra_info = ''
        if include_required and token != 'OUR' and token != 'CUR':
            extra_info = " [%s]" % parse_required(code[3:])

        print()
        print("%s%s" % (explanations[token], extra_info))


# Access: https://www.w3.org/TR/P3P/#ACCESS
def explain_access(access):
    print()
    print("ACCESS TO INFORMATION")
    print()

    if len(access) > 1:
        print('ERROR: more than one access policy is specified: %s' % ", ".join(access))
    elif len(access) == 0:
        print('ERROR: no access policy')
    else:
        print(ACCESS_TOKENS[access[0]])


# Categories: https://www.w3.org/TR/P3P/#Categories
def explain_categories(categories):
    print("CATEGORIES OF DATA")
    print_bullets(categories, CATEGORY_TOKENS, False)


# Disputes: https://www.w3.org/TR/P3P/#DISPUTES
def explain_dispute(dispute):
    print()
    print("DISPUTE RESOLUTION PROCEDURE")
    print()

    if dispute:
        print("There are some dispute resolution procedures.")
    else:
        print("There is no dispute resolution procedure.")


def explain_prelude(test, non_identifiable):
    first_line = True
    # Test: https://www.w3.org/TR/P3P/#test
    if test:
        first_line = False
        print("The policy is just an example and must be ignored and considered invalid.")

    # Non-identifiable: https://www.w3.org/TR/P3P/#NON-IDENTIFIABLE
    if non_identifiable:
        if first_line:
            print()
            first_line = False

        print("Either no data is collected (including Web logs), or that the organization collecting the data will anonymize the data.")

    if not first_line:
        print()


# Purpose: https://www.w3.org/TR/P3P/#PURPOSE
def explain_purpose(purposes, non_identifiable):
    print()
    print("PURPOSES FOR DATA PROCESSING")

    if len(purposes) == 0:
        print()
        if non_identifiable:
            print('Not required for non-identifiable data.')
        else:
            print('ERROR: no purpose statement')

    print_bullets(purposes, PURPOSE_TOKENS, True)


# Recipient: https://www.w3.org/TR/P3P/#RECPNT
def explain_recipients(recipients, non_identifiable):
    print()
    print("RECIPIENTS OF DATA")

    if len(recipients) == 0:
        print()
        if non_identifiable:
            print('Not required for non-identifiable data.')
        else:
            print('ERROR: no recipient statement')

    print_bullets(recipients, RECIPIENT_TOKENS, True)


# Remedies: https://www.w3.org/TR/P3P/#REMEDIES
def explain_remedies(remedies):
    print()
    print("REMEDIES IN CASE OF A POLICY BREACH")
    print_bullets(remedies, REMEDY_TOKENS, False)


# Retention: https://www.w3.org/TR/P3P/#RETENTION
def explain_retention(retention, non_identifiable):
    print()
    print("RETENTION POLICY")
    print()

    if len(retention) > 1:
        print('ERROR: more than one retention policy is specified: %s' % ", ".join(retention))
    elif len(retention) == 0:
        if non_identifiable:
            print('Not required for non-identifiable data.')
        else:
            print('ERROR: no retention policy')
    else:
        print(RETENTION_TOKENS[retention[0]])


def explain_policy(policy):
    access = []
    categories = []
    dispute = False
    non_identifiable = False
    purposes = []
    recipients = []
    remedies = []
    retention = []
    test = False

    for word in policy.split():
        token = word[0:3]

        if token in ACCESS_TOKENS:
            access.append(word)
        elif token in CATEGORY_TOKENS:
            categories.append(word)
        elif token in PURPOSE_TOKENS:
            purposes.append(word)
        elif token in RECIPIENT_TOKENS:
            recipients.append(word)
        elif token in REMEDY_TOKENS:
            remedies.append(word)
        elif token in RETENTION_TOKENS:
            retention.append(word)
        elif token == 'DSP':
            dispute = True
        elif token == 'NID':
            non_identifiable = True
        elif token == 'TST':
            test = True
        else :
            print("ERROR: %s is an invalid token" % word)

    explain_prelude(test, non_identifiable)
    explain_categories(categories)
    explain_recipients(recipients, non_identifiable)
    explain_purpose(purposes, non_identifiable)
    explain_retention(retention, non_identifiable)
    explain_access(access)
    explain_remedies(remedies)
    explain_dispute(dispute)

    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('policy', type=str, nargs='?', default='',
                        help='the policy to explain (default: STDIN)')
    args = parser.parse_args()

    policy = args.policy
    if not policy:
        policy = sys.stdin.read().strip()

    return explain_policy(policy)


sys.exit(main())
