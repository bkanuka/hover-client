import argparse
from hover.client import HoverAPI, HoverClient

parser = argparse.ArgumentParser(description="Grabs all DNS records from hover, filters by the content of the DNS record then updates the content to a new value.")
parser.add_argument("--hover_username", required=True)
parser.add_argument("--hover_password", required=True)
parser.add_argument("--dry_run", action="store_true")
parser.add_argument("--search_term", required=True, help="The current domain that you want to replace all references to")
parser.add_argument("--replacement_domain", required=True, help="The replacement domain")
args = parser.parse_args()

hAPI = HoverAPI(username=args.hover_username, password=args.hover_password)

domain_names = hAPI.get_list_of_domains()

OUTPUT_PREFIX = "Repointing "

if args.dry_run:
    OUTPUT_PREFIX = "Would repoint "

for current_domain_name in domain_names:
    domain_client = HoverClient(username=args.hover_username, password=args.hover_password, domain_name=current_domain_name)

    dns_records = domain_client.get_all_records()

    for current_record in dns_records:

        if args.search_term in current_record["content"]:
            full_domain = current_record["name"] + "." + current_domain_name

            print OUTPUT_PREFIX + full_domain + " (" + current_record["id"] + " : " + current_record["content"] + ")"

            if not args.dry_run:
                domain_client.update_record_by_id(current_record["id"], args.replacement_domain)
