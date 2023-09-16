import time
import dungeons_and_trolls_client
from pprint import pprint
from dungeons_and_trolls_client.api import dungeons_and_trolls_api
from dungeons_and_trolls_client.model.dungeonsandtrolls_commands_batch import DungeonsandtrollsCommandsBatch
from dungeons_and_trolls_client.model.dungeonsandtrolls_commands_for_monsters import DungeonsandtrollsCommandsForMonsters
from dungeons_and_trolls_client.model.dungeonsandtrolls_coordinates import DungeonsandtrollsCoordinates
from dungeons_and_trolls_client.model.dungeonsandtrolls_game_state import DungeonsandtrollsGameState
from dungeons_and_trolls_client.model.dungeonsandtrolls_identifier import DungeonsandtrollsIdentifier
from dungeons_and_trolls_client.model.dungeonsandtrolls_identifiers import DungeonsandtrollsIdentifiers
from dungeons_and_trolls_client.model.dungeonsandtrolls_message import DungeonsandtrollsMessage
from dungeons_and_trolls_client.model.dungeonsandtrolls_registration import DungeonsandtrollsRegistration
from dungeons_and_trolls_client.model.dungeonsandtrolls_skill_use import DungeonsandtrollsSkillUse
from dungeons_and_trolls_client.model.dungeonsandtrolls_user import DungeonsandtrollsUser
from dungeons_and_trolls_client.model.rpc_status import RpcStatus
# Defining the host is optional and defaults to https://dt.garage-trip.cz
# See configuration.py for a list of all supported configuration parameters.
configuration = dungeons_and_trolls_client.Configuration()
configuration.host = ""

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiKeyAuth
configuration.api_key['ApiKeyAuth'] = ''

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiKeyAuth'] = 'Bearer'


# Enter a context with an instance of the API client
with dungeons_and_trolls_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = dungeons_and_trolls_api.DungeonsAndTrollsApi(api_client)
    body = DungeonsandtrollsIdentifiers(
        ids=[
            "ids_example",
        ],
    ) # DungeonsandtrollsIdentifiers | 

    try:
        # Buy Items identified by the provided ID for the Character bound to the logged user.
        api_response = api_instance.dungeons_and_trolls_game()
        pprint(api_response)
    except dungeons_and_trolls_api.ApiException as e:
        print("Exception when calling DungeonsAndTrollsApi->dungeons_and_trolls_game: %s\n" % e)