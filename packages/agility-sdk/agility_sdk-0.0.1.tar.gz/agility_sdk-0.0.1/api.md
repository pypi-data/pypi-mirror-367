# Assistants

Types:

```python
from agility.types import (
    Assistant,
    AssistantWithConfig,
    AssistantListResponse,
    AssistantRetrieveRunMetadataResponse,
)
```

Methods:

- <code title="post /api/assistants/">client.assistants.<a href="./src/agility/resources/assistants/assistants.py">create</a>(\*\*<a href="src/agility/types/assistant_create_params.py">params</a>) -> <a href="./src/agility/types/assistant.py">Assistant</a></code>
- <code title="get /api/assistants/{assistant_id}">client.assistants.<a href="./src/agility/resources/assistants/assistants.py">retrieve</a>(assistant_id) -> <a href="./src/agility/types/assistant_with_config.py">AssistantWithConfig</a></code>
- <code title="put /api/assistants/{assistant_id}">client.assistants.<a href="./src/agility/resources/assistants/assistants.py">update</a>(assistant_id, \*\*<a href="src/agility/types/assistant_update_params.py">params</a>) -> <a href="./src/agility/types/assistant_with_config.py">AssistantWithConfig</a></code>
- <code title="get /api/assistants/">client.assistants.<a href="./src/agility/resources/assistants/assistants.py">list</a>(\*\*<a href="src/agility/types/assistant_list_params.py">params</a>) -> <a href="./src/agility/types/assistant_list_response.py">SyncMyOffsetPage[AssistantListResponse]</a></code>
- <code title="delete /api/assistants/{assistant_id}">client.assistants.<a href="./src/agility/resources/assistants/assistants.py">delete</a>(assistant_id) -> None</code>
- <code title="get /api/assistants/{assistant_id}/historical_run_metadata/{run_id}">client.assistants.<a href="./src/agility/resources/assistants/assistants.py">retrieve_run_metadata</a>(run_id, \*, assistant_id) -> <a href="./src/agility/types/assistant_retrieve_run_metadata_response.py">AssistantRetrieveRunMetadataResponse</a></code>

## AccessKeys

Types:

```python
from agility.types.assistants import AccessKey
```

Methods:

- <code title="post /api/assistants/{assistant_id}/access_keys/">client.assistants.access_keys.<a href="./src/agility/resources/assistants/access_keys.py">create</a>(assistant_id, \*\*<a href="src/agility/types/assistants/access_key_create_params.py">params</a>) -> <a href="./src/agility/types/assistants/access_key.py">AccessKey</a></code>
- <code title="get /api/assistants/{assistant_id}/access_keys/">client.assistants.access_keys.<a href="./src/agility/resources/assistants/access_keys.py">list</a>(assistant_id, \*\*<a href="src/agility/types/assistants/access_key_list_params.py">params</a>) -> <a href="./src/agility/types/assistants/access_key.py">SyncMyOffsetPage[AccessKey]</a></code>

# KnowledgeBases

Types:

```python
from agility.types import KnowledgeBaseWithConfig, KnowledgeBaseListResponse
```

Methods:

- <code title="post /api/knowledge_bases/">client.knowledge_bases.<a href="./src/agility/resources/knowledge_bases/knowledge_bases.py">create</a>(\*\*<a href="src/agility/types/knowledge_base_create_params.py">params</a>) -> <a href="./src/agility/types/knowledge_base_with_config.py">KnowledgeBaseWithConfig</a></code>
- <code title="get /api/knowledge_bases/{knowledge_base_id}">client.knowledge_bases.<a href="./src/agility/resources/knowledge_bases/knowledge_bases.py">retrieve</a>(knowledge_base_id) -> <a href="./src/agility/types/knowledge_base_with_config.py">KnowledgeBaseWithConfig</a></code>
- <code title="put /api/knowledge_bases/{knowledge_base_id}">client.knowledge_bases.<a href="./src/agility/resources/knowledge_bases/knowledge_bases.py">update</a>(knowledge_base_id, \*\*<a href="src/agility/types/knowledge_base_update_params.py">params</a>) -> <a href="./src/agility/types/knowledge_base_with_config.py">KnowledgeBaseWithConfig</a></code>
- <code title="get /api/knowledge_bases/">client.knowledge_bases.<a href="./src/agility/resources/knowledge_bases/knowledge_bases.py">list</a>(\*\*<a href="src/agility/types/knowledge_base_list_params.py">params</a>) -> <a href="./src/agility/types/knowledge_base_list_response.py">SyncMyOffsetPage[KnowledgeBaseListResponse]</a></code>
- <code title="delete /api/knowledge_bases/{knowledge_base_id}">client.knowledge_bases.<a href="./src/agility/resources/knowledge_bases/knowledge_bases.py">delete</a>(knowledge_base_id) -> None</code>

## Sources

Types:

```python
from agility.types.knowledge_bases import Source, SourceStatusResponse
```

Methods:

- <code title="post /api/knowledge_bases/{knowledge_base_id}/sources/">client.knowledge_bases.sources.<a href="./src/agility/resources/knowledge_bases/sources/sources.py">create</a>(knowledge_base_id, \*\*<a href="src/agility/types/knowledge_bases/source_create_params.py">params</a>) -> <a href="./src/agility/types/knowledge_bases/source.py">Source</a></code>
- <code title="get /api/knowledge_bases/{knowledge_base_id}/sources/{source_id}">client.knowledge_bases.sources.<a href="./src/agility/resources/knowledge_bases/sources/sources.py">retrieve</a>(source_id, \*, knowledge_base_id) -> <a href="./src/agility/types/knowledge_bases/source.py">Source</a></code>
- <code title="put /api/knowledge_bases/{knowledge_base_id}/sources/{source_id}">client.knowledge_bases.sources.<a href="./src/agility/resources/knowledge_bases/sources/sources.py">update</a>(source_id, \*, knowledge_base_id, \*\*<a href="src/agility/types/knowledge_bases/source_update_params.py">params</a>) -> <a href="./src/agility/types/knowledge_bases/source.py">Source</a></code>
- <code title="get /api/knowledge_bases/{knowledge_base_id}/sources/">client.knowledge_bases.sources.<a href="./src/agility/resources/knowledge_bases/sources/sources.py">list</a>(knowledge_base_id, \*\*<a href="src/agility/types/knowledge_bases/source_list_params.py">params</a>) -> <a href="./src/agility/types/knowledge_bases/source.py">SyncMyOffsetPage[Source]</a></code>
- <code title="delete /api/knowledge_bases/{knowledge_base_id}/sources/{source_id}">client.knowledge_bases.sources.<a href="./src/agility/resources/knowledge_bases/sources/sources.py">delete</a>(source_id, \*, knowledge_base_id) -> None</code>
- <code title="get /api/knowledge_bases/{knowledge_base_id}/sources/{source_id}/status">client.knowledge_bases.sources.<a href="./src/agility/resources/knowledge_bases/sources/sources.py">status</a>(source_id, \*, knowledge_base_id) -> <a href="./src/agility/types/knowledge_bases/source_status_response.py">SourceStatusResponse</a></code>
- <code title="post /api/knowledge_bases/{knowledge_base_id}/sources/{source_id}/sync">client.knowledge_bases.sources.<a href="./src/agility/resources/knowledge_bases/sources/sources.py">sync</a>(source_id, \*, knowledge_base_id) -> object</code>

### Documents

Types:

```python
from agility.types.knowledge_bases.sources import Document
```

Methods:

- <code title="get /api/knowledge_bases/{knowledge_base_id}/sources/{source_id}/documents/{document_id}">client.knowledge_bases.sources.documents.<a href="./src/agility/resources/knowledge_bases/sources/documents.py">retrieve</a>(document_id, \*, knowledge_base_id, source_id) -> <a href="./src/agility/types/knowledge_bases/sources/document.py">Document</a></code>
- <code title="get /api/knowledge_bases/{knowledge_base_id}/sources/{source_id}/documents/">client.knowledge_bases.sources.documents.<a href="./src/agility/resources/knowledge_bases/sources/documents.py">list</a>(source_id, \*, knowledge_base_id, \*\*<a href="src/agility/types/knowledge_bases/sources/document_list_params.py">params</a>) -> <a href="./src/agility/types/knowledge_bases/sources/document.py">SyncMyOffsetPage[Document]</a></code>

# Users

Types:

```python
from agility.types import User
```

Methods:

- <code title="get /api/users/{user_id}">client.users.<a href="./src/agility/resources/users/users.py">retrieve</a>(user_id) -> <a href="./src/agility/types/user.py">User</a></code>

## APIKey

Types:

```python
from agility.types.users import APIKeyRetrieveResponse
```

Methods:

- <code title="get /api/users/{user_id}/api-key">client.users.api_key.<a href="./src/agility/resources/users/api_key.py">retrieve</a>(user_id) -> str</code>
- <code title="post /api/users/{user_id}/api-key/refresh">client.users.api_key.<a href="./src/agility/resources/users/api_key.py">refresh</a>(user_id) -> <a href="./src/agility/types/user.py">User</a></code>

# Threads

Types:

```python
from agility.types import Thread
```

Methods:

- <code title="post /api/threads/">client.threads.<a href="./src/agility/resources/threads/threads.py">create</a>() -> <a href="./src/agility/types/thread.py">Thread</a></code>
- <code title="get /api/threads/{thread_id}">client.threads.<a href="./src/agility/resources/threads/threads.py">retrieve</a>(thread_id) -> <a href="./src/agility/types/thread.py">Thread</a></code>
- <code title="get /api/threads/">client.threads.<a href="./src/agility/resources/threads/threads.py">list</a>(\*\*<a href="src/agility/types/thread_list_params.py">params</a>) -> <a href="./src/agility/types/thread.py">SyncMyOffsetPage[Thread]</a></code>
- <code title="delete /api/threads/{thread_id}">client.threads.<a href="./src/agility/resources/threads/threads.py">delete</a>(thread_id) -> None</code>

## Messages

Types:

```python
from agility.types.threads import Message
```

Methods:

- <code title="post /api/threads/{thread_id}/messages/">client.threads.messages.<a href="./src/agility/resources/threads/messages.py">create</a>(thread_id, \*\*<a href="src/agility/types/threads/message_create_params.py">params</a>) -> <a href="./src/agility/types/threads/message.py">Message</a></code>
- <code title="get /api/threads/{thread_id}/messages/{message_id}">client.threads.messages.<a href="./src/agility/resources/threads/messages.py">retrieve</a>(message_id, \*, thread_id) -> <a href="./src/agility/types/threads/message.py">Message</a></code>
- <code title="get /api/threads/{thread_id}/messages/">client.threads.messages.<a href="./src/agility/resources/threads/messages.py">list</a>(thread_id, \*\*<a href="src/agility/types/threads/message_list_params.py">params</a>) -> <a href="./src/agility/types/threads/message.py">SyncMyOffsetPage[Message]</a></code>
- <code title="delete /api/threads/{thread_id}/messages/{message_id}">client.threads.messages.<a href="./src/agility/resources/threads/messages.py">delete</a>(message_id, \*, thread_id) -> None</code>

## Runs

Types:

```python
from agility.types.threads import Run
```

Methods:

- <code title="post /api/threads/{thread_id}/runs/">client.threads.runs.<a href="./src/agility/resources/threads/runs.py">create</a>(thread_id, \*\*<a href="src/agility/types/threads/run_create_params.py">params</a>) -> <a href="./src/agility/types/threads/run.py">Run</a></code>
- <code title="get /api/threads/{thread_id}/runs/{run_id}">client.threads.runs.<a href="./src/agility/resources/threads/runs.py">retrieve</a>(run_id, \*, thread_id) -> <a href="./src/agility/types/threads/run.py">Run</a></code>
- <code title="delete /api/threads/{thread_id}/runs/{run_id}">client.threads.runs.<a href="./src/agility/resources/threads/runs.py">delete</a>(run_id, \*, thread_id) -> None</code>
- <code title="post /api/threads/{thread_id}/runs/stream">client.threads.runs.<a href="./src/agility/resources/threads/runs.py">stream</a>(thread_id, \*\*<a href="src/agility/types/threads/run_stream_params.py">params</a>) -> object</code>

# Integrations

Types:

```python
from agility.types import (
    GcSv0Integration,
    Integration,
    S3V0Integration,
    IntegrationCreateResponse,
    IntegrationRetrieveResponse,
    IntegrationListResponse,
)
```

Methods:

- <code title="post /api/integrations/">client.integrations.<a href="./src/agility/resources/integrations/integrations.py">create</a>(\*\*<a href="src/agility/types/integration_create_params.py">params</a>) -> <a href="./src/agility/types/integration_create_response.py">IntegrationCreateResponse</a></code>
- <code title="get /api/integrations/{integration_id}">client.integrations.<a href="./src/agility/resources/integrations/integrations.py">retrieve</a>(integration_id) -> <a href="./src/agility/types/integration_retrieve_response.py">IntegrationRetrieveResponse</a></code>
- <code title="get /api/integrations/">client.integrations.<a href="./src/agility/resources/integrations/integrations.py">list</a>(\*\*<a href="src/agility/types/integration_list_params.py">params</a>) -> <a href="./src/agility/types/integration_list_response.py">SyncMyOffsetPage[IntegrationListResponse]</a></code>
- <code title="delete /api/integrations/{integration_id}">client.integrations.<a href="./src/agility/resources/integrations/integrations.py">delete</a>(integration_id) -> None</code>

## Available

Types:

```python
from agility.types.integrations import IntegrationTypeDef, AvailableListResponse
```

Methods:

- <code title="get /api/integrations/available">client.integrations.available.<a href="./src/agility/resources/integrations/available.py">list</a>() -> <a href="./src/agility/types/integrations/available_list_response.py">AvailableListResponse</a></code>

## Rbac

Methods:

- <code title="post /api/integrations/rbac/{integration_id}/verify">client.integrations.rbac.<a href="./src/agility/resources/integrations/rbac.py">verify</a>(integration_id) -> <a href="./src/agility/types/integration.py">Integration</a></code>
