#!/usr/bin/env python
from paasta_tools.paasta_cli.utils import execute_paasta_serviceinit_on_remote_master
from paasta_tools.paasta_cli.utils import figure_out_service_name
from paasta_tools.paasta_cli.utils import lazy_choices_completer
from paasta_tools.paasta_cli.utils import list_services
from paasta_tools.paasta_cli.utils import list_instances
from paasta_tools.utils import compose_job_id
from paasta_tools.utils import list_clusters


def add_subparser(subparsers):
    status_parser = subparsers.add_parser(
        'emergency-stop',
        description="Stop a PaaSTA service instance",
        help=("Stops a PaaSTA service instance by scaling it down to 0 instances (for Marathon apps)"
              " or by killing the tasks for any version of it and disabling it (for Chronos jobs)."))
    status_parser.add_argument(
        '-s', '--service',
        help="Service that you want to stop. Like 'example_service'.",
    ).completer = lazy_choices_completer(list_services)
    status_parser.add_argument(
        '-i', '--instance',
        help="Instance of the service that you want to stop. Like 'main' or 'canary'.",
        required=True,
    ).completer = lazy_choices_completer(list_instances)
    status_parser.add_argument(
        '-c', '--cluster',
        help="The PaaSTA cluster that has the service instance you want to stop. Like 'norcal-prod'.",
        required=True,
    ).completer = lazy_choices_completer(list_clusters)
    status_parser.set_defaults(command=paasta_emergency_stop)


def paasta_emergency_stop(args):
    """Performs an emergency stop on a given service instance on a given cluster

    Warning: This command does not permanently stop the service. The next time the service is updated
    (config change, or a deploy, or a bounce, etc.), those settings will override the emergency stop.

    If you want this stop to be permanant, adjust the relevant config file to reflect that.
    For example, this can be done for Marathon apps by setting 'instances: 0', or
    for Chronos jobs by setting 'disabled: True'. Alternatively, remove the config yaml entirely.
    """
    service = figure_out_service_name(args)
    print "Performing an emergency stop on %s..." % compose_job_id(service, args.instance)
    execute_paasta_serviceinit_on_remote_master('stop', args.cluster, service, args.instance)
    print "%s" % "\n".join(paasta_emergency_stop.__doc__.splitlines()[-7:])
    print "To start this service again asap, run:"
    print "paasta emergency-start --service %s --instance %s --cluster %s" % (service, args.instance, args.cluster)
