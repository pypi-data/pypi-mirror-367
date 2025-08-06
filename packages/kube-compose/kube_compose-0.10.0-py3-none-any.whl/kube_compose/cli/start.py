import click
import itertools
from kube_compose.cli import cli
from kube_compose import utils

@cli.command()
@utils.require_binaries(kubectl='kubectl')
@utils.require_kube_compose_release
@click.argument('service', type=str, required=False)
def start(service, *, namespace, kubectl, docker_compose_config, deployments, **_):
  ''' Like `docker-compose start` but effects the kubernetes deployed resources
  '''
  if service is not None:
    replicas = docker_compose_config.get('services', {}).get(service, {}).get('deploy', {}).get('replicas', 1) or 1
    utils.run([
      *kubectl, 'scale',
      *(('-n', namespace) if namespace else tuple()),
      f"--replicas={replicas}",
      deployments[service],
    ])
  else:
    deploy_replicas = []
    for svc, deploy in deployments.items():
      replicas = docker_compose_config['services'][svc].get('deploy', {}).get('replicas', 1)
      deploy_replicas.append((replicas, deploy))
    for replicas, deploy in itertools.groupby(sorted(deploy_replicas), lambda key: key[0]):
      utils.run([
        *kubectl, 'scale',
        *(('-n', namespace) if namespace else tuple()),
        f"--replicas={replicas}",
        *[d for _, d in deploy],
      ])
