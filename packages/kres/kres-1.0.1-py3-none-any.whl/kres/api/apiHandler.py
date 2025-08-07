import json
import requests
from datetime import datetime

from kres.utils.readMemory           import ReadMemory
from kres.utils.logger               import Logger
from kres.utils.extractResourceNames import ExtractResourceNames

class APIHandler:
    def __init__(self, log: str = "INFO") -> None:
        self.log        = log
        self.logger     = Logger(self.log)
        self.readMemory = ReadMemory(log=self.log)
        self.payload    = None

    def getPayload(self) -> dict:
        if not self.payload:
            self.payload = self.generatePayload()

        self.logger.debug("Payload already generated, returning cached payload.")
        return self.payload

    def isKresApiRunning(self) -> bool:
        self.logger.debug("Checking if Kres API is running...")
        kresApiData = self.readMemory.readKresApiData()

        try:
            response = requests.get(f"http://localhost:{kresApiData['port']}/health")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to connect to Kres API: {e}")
            return False

        self.logger.debug(f"Kres API response status: {response.status_code}")
        return response.status_code == 200

    def isKubeApiRunning(self) -> bool:
        url = self.buildURL('/api')
        self.logger.debug(f"Checking if Kubernetes API is reachable...")

        self.getPayload()

        try:
            response = requests.get(
                url     = url,
                headers = self.payload.get('headers'),
                verify  = self.payload.get('caAuth')
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to connect to Kubernetes API: {e}")
            return False

        self.logger.debug(f"Kubernetes API response status: {response.status_code}")
        return response.status_code == 200

    def fetchDecryptedToken(self) -> str:
        kresApiData = self.readMemory.readKresApiData()

        self.logger.debug(f"Sending request to kres API at /decrypt to fetch decrypted token...")
        try:
            response = requests.get(
                url = f"http://localhost:{kresApiData['port']}/decrypt"
            )
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to connect to Kres API: {e}")
            raise e

        self.logger.debug(f"Received response with status code: {response.status_code}")

        if response.status_code == 200:
            self.logger.debug("Successfully fetched decrypted token from Kres API.")
            return response.json().get('token')
        else:
            self.logger.error(f"Failed to fetch decrypted token. Status code: {response.status_code}")
            raise Exception(f"Failed to fetch decrypted token. Status code: {response.status_code}")

    def generatePayload(self, accept: str = "application/json", contentType: str = "application/json") -> dict:
        self.logger.debug("Generating API payload...")
        json_data = self.readMemory.readJson()
        token     = self.fetchDecryptedToken()

        payload = {}
        payload['apiServer'] = json_data.get('apiServer')
        payload['caAuth']    = json_data.get('caAuth')
        payload['headers']   = {
            "Authorization": f"Bearer {token}",
            "Accept"      : accept,
            "Content-Type": contentType
        }

        self.logger.debug(f"Generated payload successfully")
        return payload

    def buildURL(self, path: str) -> str:
        self.getPayload()
        self.logger.debug(f"URL: {self.payload.get('apiServer')}{path}")
        return f"{self.payload.get('apiServer')}{path}"

    def checkResourceAccess(self, namespace: str, resource: str, verb: str) -> bool:
        url = self.buildURL(f'/apis/authorization.k8s.io/v1/selfsubjectaccessreviews')
        self.logger.debug(f"Constructed URL for access check: {url}")

        self.logger.debug(f"Checking access for resource '{resource}' in namespace '{namespace}' with verb '{verb}'...")

        headers = self.payload.get('headers')
        caAuth  = self.payload.get('caAuth')
        body    = {
            "kind"      : "SelfSubjectAccessReview",
            "apiVersion": "authorization.k8s.io/v1",
            "spec"      : {
                "resourceAttributes": {
                    "namespace": namespace,
                    "verb"    : verb,
                    "group"   : "",
                    "resource": resource
                }
            }
        }

        if resource in ['deployments', 'statefulsets']:
            body['spec']['resourceAttributes']['group'] = 'apps'
            self.logger.debug(f"Set group 'apps' for resource '{resource}'")

        self.logger.debug(f"Sending request with body: {json.dumps(body)}")

        try:
            response = requests.post(
                url     = url,
                headers = headers,
                json    = body,
                verify  = caAuth
            )
            self.logger.debug(f"Received response with status code: {response.status_code}")

            if response.status_code in [200, 201]:
                responseData = response.json()
                status       = responseData.get('status', {})
                allowed      = status.get('allowed', False)
                return allowed
            else:
                self.logger.error(f"Access check failed. HTTP {response.status_code}: {response.text}")
                raise Exception(f"Failed to check access for {resource} in namespace {namespace}. Status code: {response.status_code}")

        except requests.RequestException as e:
            self.logger.error(f"Error during access check request: {e}")
            raise e

    def restartResource(
        self,
        namespace : str,
        resource  : str,
        secret    : str,
        configmap : str,
        reason    : str,
        name      : str,
        allFlag   : bool
    ) -> None:
        if resource == 'deployments':
            url = self.buildURL(f'/apis/apps/v1/namespaces/{namespace}/deployments')
        elif resource == 'statefulsets':
            url = self.buildURL(f'/apis/apps/v1/namespaces/{namespace}/statefulsets')
        elif resource == 'pods':
            url = self.buildURL(f'/api/v1/namespaces/{namespace}/pods')

        self.logger.debug(f"Constructed URL for restarting resource: {url}")

        headers = self.payload.get('headers')
        caAuth  = self.payload.get('caAuth')

        if allFlag:
            self.logger.debug(f"Fetching all {resource} in namespace {namespace} to restart...")
            response = requests.get(
                url     = url,
                headers = headers,
                verify  = caAuth
            )
            self.logger.debug(f"Received response with status code: {response.status_code}")

            if response.status_code == 200:
                fields = {
                    'secrets'   : secret,
                    'configmaps': configmap
                }
                self.logger.debug(f"Extracting resource names from response with fields: {fields}")

                extractResourceNames = ExtractResourceNames(
                    body   = response.json(),
                    fields = fields,
                    log    = self.log
                )
                resources = extractResourceNames.extract()
                self.logger.info(f"Found {len(resources)} resources to restart.")

                for resourceName in resources:
                    if resource == 'pods':
                        self.restartPod(url, resourceName)
                    else:
                        self.restartController(url, resourceName, reason)
            else:
                self.logger.error(f"Failed to fetch {resource} in namespace {namespace}. Status code: {response.status_code}")
                raise Exception(f"Failed to fetch {resource} in namespace {namespace}. Status code: {response.status_code}")
        else:
            if resource == 'pods':
                self.restartPod(url, name)
            else:
                self.restartController(url, name, reason)

    def restartController(self, url: str, name: str, reason: str) -> None:
        url = f"{url}/{name}"
        self.logger.debug(f"Restarting controller at URL: {url} with name: {name} and reason: {reason}")

        restartTriggeredAt = datetime.now().isoformat()
        payload           = self.generatePayload(
            contentType = "application/strategic-merge-patch+json"
        )

        body = {
            "metadata": {
                "annotations": {
                    "kres.io/restart-reason"      : reason,
                    "kres.io/restart-triggered-at": str(restartTriggeredAt)
                }
            },
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kres.io/restart-reason"      : reason,
                            "kres.io/restart-triggered-at": str(restartTriggeredAt)
                        }
                    }
                }
            }
        }

        try:
            self.logger.debug(f"Sending PATCH request to {url} with body: {json.dumps(body)}")
            response = requests.patch(
                url     = url,
                headers = payload.get('headers'),
                json    = body,
                verify  = payload.get('caAuth')
            )
            self.logger.debug(f"Received response with status code: {response.status_code}")

            if response.status_code == 200:
                self.logger.info(f"Successfully restarted {name} with reason '{reason}'.")
            else:
                self.logger.error(f"Failed to restart {name}. Status code: {response.status_code}. Response: {response.text}")
                raise Exception(f"Failed to restart {name}. Status code: {response.status_code}. Response: {response.text}")
        except requests.RequestException as e:
            self.logger.error(f"Error during restart request: {e}")
            raise e

    def restartPod(self, url: str, name: str) -> None:
        url = f"{url}/{name}"
        self.logger.debug(f"Restarting controller at URL: {url} with name: {name}")

        payload = self.getPayload()

        try:
            self.logger.debug(f"Sending DELETE request to {url} for Pod {name}")
            response = requests.delete(
                url     = url,
                headers = payload.get('headers'),
                verify  = payload.get('caAuth')
            )
            self.logger.debug(f"Received response with status code: {response.status_code}")

            if response.status_code == 200:
                self.logger.info(f"Pod {name} deleted successfully. It will be recreated by the controller.")
            else:
                self.logger.error(f"Failed to delete Pod {name}. Status code: {response.status_code}. Response: {response.text}")
                raise Exception(f"Failed to delete Pod {name}. Status code: {response.status_code}. Response: {response.text}")

        except requests.RequestException as e:
            self.logger.error(f"Error during Pod deletion request: {e}")
            raise e