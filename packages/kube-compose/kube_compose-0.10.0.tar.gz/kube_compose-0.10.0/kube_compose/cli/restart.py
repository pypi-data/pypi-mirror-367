import click
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('service', type=str, required=False)
def restart(service, *, namespace, kubectl, deployments, **_):
  ''' Like `docker-compose restart` but effects the kubernetes deployed resources
  '''
  deploy = [deployments[service]] if service is not None else list(deployments.values())
  utils.run([
    *kubectl, 'rollout', 'restart',
    *(('-n', namespace) if namespace else tuple()),
    *deploy,
  ])
  utils.run([
    *kubectl, 'rollout', 'status',
    *(('-n', namespace) if namespace else tuple()),
    *deploy,
  ])
