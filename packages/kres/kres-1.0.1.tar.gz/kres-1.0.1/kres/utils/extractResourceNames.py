import json

from kres.utils.logger import Logger

class ExtractResourceNames:
    def __init__(self, body:json, fields:dict[str, str], log:str = "INFO") -> None:
        self.body   = body
        self.fields = fields
        self.logger = Logger(log)

    def extractResourcesFromContainers(self, containers: dict, resourceName: str) -> list[str]:
        secret    = self.fields.get('secrets', '')
        configmap = self.fields.get('configmaps', '')
        resources = []

        for container in containers:
            for env in container.get('env', []):
                valueFrom = env.get('valueFrom', {})
                self.logger.debug(f"Checking env valueFrom: {valueFrom}")
                
                if 'secretKeyRef' in valueFrom:
                    self.logger.debug(f"Checking secret: {valueFrom['secretKeyRef'].get('name')} against {secret}")

                    if valueFrom['secretKeyRef'].get('name') == secret:
                        self.logger.debug(f"Matched secret in env for container in resource {resourceName}")
                        resources.append(resourceName)
                        break

                if 'configMapKeyRef' in valueFrom:
                    self.logger.debug(f"Checking configmap: {valueFrom['configMapKeyRef'].get('name')} against {configmap}")

                    if valueFrom['configMapKeyRef'].get('name') == configmap:
                        self.logger.debug(f"Matched configmap in env for container in resource {resourceName}")
                        resources.append(resourceName)
                        break

            for env_from in container.get('envFrom', []):
                if 'secretRef' in env_from:
                    self.logger.debug(f"Checking envFrom secretRef: {env_from['secretRef'].get('name')} against {secret}")

                    if env_from['secretRef'].get('name') == secret:
                        self.logger.debug(f"Matched secret in envFrom for container in resource {resourceName}")
                        resources.append(resourceName)
                        break

                if 'configMapRef' in env_from:
                    self.logger.debug(f"Checking envFrom configMapRef: {env_from['configMapRef'].get('name')} against {configmap}")

                    if env_from['configMapRef'].get('name') == configmap:
                        self.logger.debug(f"Matched configmap in envFrom for container in resource {resourceName}")
                        resources.append(resourceName)
                        break
        
        self.logger.debug(f"Extracted resources from containers: {resources}")
        return resources

    def extractResourcesFromVolumes(self, volumes:dict, resourceName:str) -> list[str]:
        secret    = self.fields.get('secrets', '')
        configmap = self.fields.get('configmaps', '')
        resources = []

        for volume in volumes:
            self.logger.debug(f"Checking volume: {volume}")
            if volume.get('secret', {}).get('secretName') == secret:
                self.logger.debug(f"Matched secret in volume for resource {resourceName}")
                resources.append(resourceName)
                break

            if volume.get('configMap', {}).get('name') == configmap:
                self.logger.debug(f"Matched configmap in volume for resource {resourceName}")
                resources.append(resourceName)
                break

            projected_sources = volume.get('projected', {}).get('sources', [])
            for source in projected_sources:
                self.logger.debug(f"Checking projected source: {source}")
                if 'secret' in source and source['secret'].get('name') == secret:
                    self.logger.debug(f"Matched secret in projected volume for resource {resourceName}")
                    resources.append(resourceName)
                    break
                
                if 'configMap' in source and source['configMap'].get('name') == configmap:
                    self.logger.debug(f"Matched configmap in projected volume for resource {resourceName}")
                    resources.append(resourceName)
                    break
        
        self.logger.debug(f"Extracted resources from volumes: {resources}")
        return resources

    def extract(self) -> list[str]:
        resources = []
        self.logger.debug(f"Extracting from body keys: {self.body.keys()}")

        for item in self.body.get('items', []):
            metadata     = item.get('metadata', {})
            resourceName = metadata.get('name', '')
            self.logger.debug(f"Processing resource: {resourceName}")

            if 'template' in item.get('spec', {}):
                podSpec = item.get('spec', {}).get('template', {}).get('spec', {})
            else:
                podSpec = item.get('spec', {})

            containers     = podSpec.get('containers', [])
            resources.extend(self.extractResourcesFromContainers(containers, resourceName))

            initContainers = podSpec.get('initContainers', [])
            resources.extend(self.extractResourcesFromContainers(initContainers, resourceName))
            
            volumes        = podSpec.get('volumes', [])
            resources.extend(self.extractResourcesFromVolumes(volumes, resourceName))

        self.logger.info(f"Final list of resources referencing secrets/configmaps: {resources}")
        return resources