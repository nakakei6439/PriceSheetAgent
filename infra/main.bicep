targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Location for Azure OpenAI (GPT-4o対応リージョン: eastus, swedencentral, westus3 など)')
param openAiLocation string = 'eastus'

@description('Tags applied to all resources')
param tags object = {
  'azd-env-name': environmentName
}

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var rgName = 'rg-${environmentName}'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: tags
}

module main 'main-resources.bicep' = {
  name: 'main-resources'
  scope: rg
  params: {
    location: location
    openAiLocation: openAiLocation
    resourceToken: resourceToken
    tags: tags
  }
}

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output DOCUMENT_INTELLIGENCE_ENDPOINT string = main.outputs.documentIntelligenceEndpoint
output AZURE_OPENAI_ENDPOINT string = main.outputs.openAiEndpoint
output AZURE_OPENAI_GPT4O_DEPLOYMENT string = main.outputs.gpt4oDeploymentName
output AZURE_STORAGE_ACCOUNT_NAME string = main.outputs.storageAccountName
output AZURE_CONTAINER_APPS_ENVIRONMENT_NAME string = main.outputs.containerAppsEnvName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = main.outputs.containerRegistryEndpoint
output SERVICE_BACKEND_NAME string = main.outputs.backendAppName
output SERVICE_BACKEND_URI string = main.outputs.backendAppUri
