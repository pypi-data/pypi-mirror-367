# closedapi_test_pythonv2_4

Developer-friendly & type-safe Python SDK specifically catered to leverage *closedapi_test_pythonv2_4* API.

<div align="left">
    <a href="https://www.speakeasy.com/?utm_source=closedapi-test-pythonv2-4&utm_campaign=python"><img src="https://custom-icon-badges.demolab.com/badge/-Built%20By%20Speakeasy-212015?style=for-the-badge&logoColor=FBE331&logo=speakeasy&labelColor=545454" /></a>
    <a href="https://opensource.org/licenses/MIT">
        <img src="https://img.shields.io/badge/License-MIT-blue.svg" style="width: 100px; height: 28px;" />
    </a>
</div>


<br /><br />
> [!IMPORTANT]
> This SDK is not yet ready for production use. Delete this section before > publishing to a package manager.

<!-- Start Summary [summary] -->
## Summary

SDK Review: A test document for reviewing the SDK.

This document will show case as many of our features as possible in as little operations/models as possible.
This will then generate a SDK that we can more easily review than the test SDKs based on uber.yaml spec.

For more information about the API: [Speakeasy Docs](https://speakeasy.com/docs)
<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [closedapi_test_pythonv2_4](#closedapitestpythonv24)
  * [SDK Installation](#sdk-installation)
  * [IDE Support](#ide-support)
  * [SDK Example Usage](#sdk-example-usage)
  * [Authentication](#authentication)
  * [Available Resources and Operations](#available-resources-and-operations)
  * [Global Parameters](#global-parameters)
  * [Server-sent event streaming](#server-sent-event-streaming)
  * [Pagination](#pagination)
  * [File uploads](#file-uploads)
  * [Retries](#retries)
  * [Error Handling](#error-handling)
  * [Server Selection](#server-selection)
  * [Custom HTTP Client](#custom-http-client)
  * [Resource Management](#resource-management)
  * [Debugging](#debugging)
* [Development](#development)
  * [Maturity](#maturity)
  * [Contributions](#contributions)

<!-- End Table of Contents [toc] -->

<!-- Start SDK Installation [installation] -->
## SDK Installation

> [!TIP]
> To finish publishing your SDK to PyPI you must [run your first generation action](https://www.speakeasy.com/docs/github-setup#step-by-step-guide).


> [!NOTE]
> **Python version upgrade policy**
>
> Once a Python version reaches its [official end of life date](https://devguide.python.org/versions/), a 3-month grace period is provided for users to upgrade. Following this grace period, the minimum python version supported in the SDK will be updated.

The SDK can be installed with *uv*, *pip*, or *poetry* package managers.

### uv (Recommended)

*uv* is a fast Python package installer and resolver, designed as a drop-in replacement for pip and pip-tools. It's recommended for its speed and modern Python tooling capabilities.

```bash
uv add git+<UNSET>.git
```

### PIP

*PIP* is the default package installer for Python, enabling easy installation and management of packages from PyPI via the command line.

```bash
pip install git+<UNSET>.git
```

### Poetry

*Poetry* is a modern tool that simplifies dependency management and package publishing by using a single `pyproject.toml` file to handle project metadata and dependencies.

```bash
poetry add git+<UNSET>.git
```

### Shell and script usage with `uv`

You can use this SDK in a Python shell with [uv](https://docs.astral.sh/uv/) and the `uvx` command that comes with it like so:

```shell
uvx --from closedapi_test_pythonv2_4 python
```

It's also possible to write a standalone Python script without needing to set up a whole project like so:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "closedapi_test_pythonv2_4",
# ]
# ///

from speakeasy.new_openapi import SDK

sdk = SDK(
  # SDK arguments
)

# Rest of script here...
```

Once that is saved to a file, you can run it with `uv run script.py` where
`script.py` can be replaced with the actual file name.
<!-- End SDK Installation [installation] -->

<!-- Start IDE Support [idesupport] -->
## IDE Support

### PyCharm

Generally, the SDK will work well with most IDEs out of the box. However, when using PyCharm, you can enjoy much better integration with Pydantic by installing an additional plugin.

- [PyCharm Pydantic Plugin](https://docs.pydantic.dev/latest/integrations/pycharm/)
<!-- End IDE Support [idesupport] -->

<!-- Start SDK Example Usage [usage] -->
## SDK Example Usage

### Example 1

```python
# Synchronous Example
from speakeasy.new_openapi import SDK


with SDK() as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from speakeasy.new_openapi import SDK

async def main():

    async with SDK() as sdk:

        res = await sdk.post_file_async(request={
            "file": {
                "file_name": "example.file",
                "content": open("example.file", "rb"),
            },
        })

        # Handle response
        print(res)

asyncio.run(main())
```

### Example 2

```python
# Synchronous Example
from datetime import date
from decimal import Decimal
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK
from speakeasy.new_openapi.utils import parse_datetime


with SDK(
    deprecated_query_param1="some example query param",
    deprecated_query_param2="some example query param",
) as sdk:

    res = sdk.test_group.tag2.post_test(test2_request=speakeasy.new_openapi.Test2Request(
        obj=speakeasy.new_openapi.ExhaustiveObject(
            str_="example",
            bool_=True,
            integer=999999,
            int32=1,
            num=1.1,
            float32=8499.3,
            date_=date.fromisoformat("2024-10-12"),
            date_time=parse_datetime("2020-01-01T00:00:00Z"),
            anything="<value>",
            bool_opt=True,
            int_opt_null=999999,
            num_opt_null=1.1,
            int_enum=speakeasy.new_openapi.IntEnum.THIRD,
            int32_enum=speakeasy.new_openapi.Int32Enum.SIXTY_NINE,
            bigint=702830,
            decimal_str=Decimal("3858.6"),
            obj=speakeasy.new_openapi.SimpleObject(
                str_="example",
            ),
            map={
                "key": speakeasy.new_openapi.SimpleObject(
                    str_="example",
                ),
            },
            arr=[
                speakeasy.new_openapi.SimpleObject(
                    str_="example",
                ),
                speakeasy.new_openapi.SimpleObject(
                    str_="example",
                ),
            ],
            any=speakeasy.new_openapi.SimpleObject(
                str_="example",
            ),
            nullable_int_enum=speakeasy.new_openapi.NullableIntEnum.THIRD,
            nullable_string_enum=speakeasy.new_openapi.NullableStringEnum.SECOND,
            color="green",
            icon=speakeasy.new_openapi.Icon.TICK,
            hero_width=speakeasy.new_openapi.HeroWidth.FOUR_HUNDRED_AND_EIGHTY,
        ),
        type=speakeasy.new_openapi.Type.SUPER_TYPE1,
    ))

    assert res is not None

    # Handle response
    print(res)
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
from datetime import date
from decimal import Decimal
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK
from speakeasy.new_openapi.utils import parse_datetime

async def main():

    async with SDK(
        deprecated_query_param1="some example query param",
        deprecated_query_param2="some example query param",
    ) as sdk:

        res = await sdk.test_group.tag2.post_test_async(test2_request=speakeasy.new_openapi.Test2Request(
            obj=speakeasy.new_openapi.ExhaustiveObject(
                str_="example",
                bool_=True,
                integer=999999,
                int32=1,
                num=1.1,
                float32=8499.3,
                date_=date.fromisoformat("2024-10-12"),
                date_time=parse_datetime("2020-01-01T00:00:00Z"),
                anything="<value>",
                bool_opt=True,
                int_opt_null=999999,
                num_opt_null=1.1,
                int_enum=speakeasy.new_openapi.IntEnum.THIRD,
                int32_enum=speakeasy.new_openapi.Int32Enum.SIXTY_NINE,
                bigint=702830,
                decimal_str=Decimal("3858.6"),
                obj=speakeasy.new_openapi.SimpleObject(
                    str_="example",
                ),
                map={
                    "key": speakeasy.new_openapi.SimpleObject(
                        str_="example",
                    ),
                },
                arr=[
                    speakeasy.new_openapi.SimpleObject(
                        str_="example",
                    ),
                    speakeasy.new_openapi.SimpleObject(
                        str_="example",
                    ),
                ],
                any=speakeasy.new_openapi.SimpleObject(
                    str_="example",
                ),
                nullable_int_enum=speakeasy.new_openapi.NullableIntEnum.THIRD,
                nullable_string_enum=speakeasy.new_openapi.NullableStringEnum.SECOND,
                color="green",
                icon=speakeasy.new_openapi.Icon.TICK,
                hero_width=speakeasy.new_openapi.HeroWidth.FOUR_HUNDRED_AND_EIGHTY,
            ),
            type=speakeasy.new_openapi.Type.SUPER_TYPE1,
        ))

        assert res is not None

        # Handle response
        print(res)

asyncio.run(main())
```

### A custom readme heading

A custom usage description

```python
# Synchronous Example
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    query_param1="some example query param",
) as sdk:

    res = sdk.tag1.list_test1(query_param2=speakeasy.new_openapi.QueryParam2.ONE, page=100, header_param1="some example header param")

    while res is not None:
        # Handle items

        res = res.next()
```

</br>

The same SDK client can also be used to make asychronous requests by importing asyncio.
```python
# Asynchronous Example
import asyncio
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK

async def main():

    async with SDK(
        query_param1="some example query param",
    ) as sdk:

        res = await sdk.tag1.list_test1_async(query_param2=speakeasy.new_openapi.QueryParam2.ONE, page=100, header_param1="some example header param")

        while res is not None:
            # Handle items

            res = res.next()

asyncio.run(main())
```
<!-- End SDK Example Usage [usage] -->

<!-- Start Authentication [security] -->
## Authentication

### Per-Client Security Schemes

This SDK supports multiple security scheme combinations globally. You can choose from one of the alternatives by setting the `security` optional parameter when initializing the SDK client instance. The selected option will be used by default to authenticate with the API for all operations that support it.

#### Option1

The `Option1` alternative relies on the following scheme:

| Name                      | Type | Scheme     | Environment Variable                          |
| ------------------------- | ---- | ---------- | --------------------------------------------- |
| `username`<br/>`password` | http | HTTP Basic | `SPEAKEASY_USERNAME`<br/>`SPEAKEASY_PASSWORD` |

```python
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    security=speakeasy.new_openapi.Security(
        option1=speakeasy.new_openapi.SecurityOption1(
            username="<USERNAME>",
            password="<PASSWORD>",
        ),
    ),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

#### Option2

All of the following schemes must be satisfied to use the `Option2` alternative:

| Name          | Type   | Scheme      | Environment Variable    |
| ------------- | ------ | ----------- | ----------------------- |
| `bearer_auth` | http   | HTTP Bearer | `SPEAKEASY_BEARER_AUTH` |
| `api_key`     | apiKey | API key     | `SPEAKEASY_API_KEY`     |

```python
import os
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    security=speakeasy.new_openapi.Security(
        option2=speakeasy.new_openapi.SecurityOption2(
            bearer_auth="<YOUR_JWT>",
            api_key=os.getenv("SPEAKEASY_API_KEY", ""),
        ),
    ),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

#### Option3

The `Option3` alternative relies on the following scheme:

| Name     | Type   | Scheme       | Environment Variable |
| -------- | ------ | ------------ | -------------------- |
| `oauth2` | oauth2 | OAuth2 token | `SPEAKEASY_OAUTH2`   |

```python
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    security=speakeasy.new_openapi.Security(
        option3=speakeasy.new_openapi.SecurityOption3(
            oauth2="Bearer <YOUR_OAUTH2_TOKEN>",
        ),
    ),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

#### Option4

The `Option4` alternative relies on the following scheme:

| Name                  | Type | Scheme      | Environment Variable                      |
| --------------------- | ---- | ----------- | ----------------------------------------- |
| `app_id`<br/>`secret` | http | Custom HTTP | `SPEAKEASY_APP_ID`<br/>`SPEAKEASY_SECRET` |

```python
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    security=speakeasy.new_openapi.Security(
        option4=speakeasy.new_openapi.SecurityOption4(
            app_id="app-speakeasy-123",
            secret="MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI",
        ),
    ),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

#### Option5

The `Option5` alternative relies on the following scheme:

| Name          | Type   | Scheme       | Environment Variable    |
| ------------- | ------ | ------------ | ----------------------- |
| `mobile_auth` | oauth2 | OAuth2 token | `SPEAKEASY_MOBILE_AUTH` |

```python
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    security=speakeasy.new_openapi.Security(
        option5=speakeasy.new_openapi.SecurityOption5(
            mobile_auth="Bearer <YOUR_OAUTH2_TOKEN>",
        ),
    ),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

#### Option6

The `Option6` alternative relies on the following scheme:

| Name                            | Type   | Scheme                         | Environment Variable                                                          |
| ------------------------------- | ------ | ------------------------------ | ----------------------------------------------------------------------------- |
| `client_id`<br/>`client_secret` | oauth2 | OAuth2 Client Credentials Flow | `SPEAKEASY_CLIENT_ID`<br/>`SPEAKEASY_CLIENT_SECRET`<br/>`SPEAKEASY_TOKEN_URL` |

```python
import os
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    security=speakeasy.new_openapi.Security(
        option6=speakeasy.new_openapi.SecurityOption6(
            client_id=os.getenv("SPEAKEASY_CLIENT_ID", ""),
            client_secret=os.getenv("SPEAKEASY_CLIENT_SECRET", ""),
        ),
    ),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

#### Option7

The `Option7` alternative relies on the following scheme:

| Name      | Type   | Scheme  | Environment Variable |
| --------- | ------ | ------- | -------------------- |
| `api_key` | apiKey | API key | `SPEAKEASY_API_KEY`  |

```python
import os
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    security=speakeasy.new_openapi.Security(
        option7=speakeasy.new_openapi.SecurityOption7(
            api_key=os.getenv("SPEAKEASY_API_KEY", ""),
        ),
    ),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```
<!-- End Authentication [security] -->

<!-- Start Available Resources and Operations [operations] -->
## Available Resources and Operations

<details open>
<summary>Available methods</summary>

### [SDK](docs/sdks/sdk/README.md)

* [operation_with_leading_and_trailing_underscores_](docs/sdks/sdk/README.md#operation_with_leading_and_trailing_underscores_)
* [post_file](docs/sdks/sdk/README.md#post_file) - Post File
* [get_polymorphism](docs/sdks/sdk/README.md#get_polymorphism)
* [get_union_errors](docs/sdks/sdk/README.md#get_union_errors)
* [get_request_body_flattened_away](docs/sdks/sdk/README.md#get_request_body_flattened_away)
* [get_fully_flattened_request](docs/sdks/sdk/README.md#get_fully_flattened_request)
* [test_endpoint](docs/sdks/sdk/README.md#test_endpoint)
* [create_user](docs/sdks/sdk/README.md#create_user) - Create User
* [get_user](docs/sdks/sdk/README.md#get_user) - Get User
* [update_user](docs/sdks/sdk/README.md#update_user) - Update User
* [delete_user](docs/sdks/sdk/README.md#delete_user) - Delete User
* [login](docs/sdks/sdk/README.md#login) - Login
* [validate](docs/sdks/sdk/README.md#validate) - Validate
* [chat](docs/sdks/sdk/README.md#chat)
* [get_binary_default_response](docs/sdks/sdk/README.md#get_binary_default_response)
* [test_enum_formats](docs/sdks/sdk/README.md#test_enum_formats) - Test x-speakeasy-enums in different formats
* [binary_and_string_upload](docs/sdks/sdk/README.md#binary_and_string_upload)
* [get_error_in_union](docs/sdks/sdk/README.md#get_error_in_union)

### [tag1](docs/sdks/tag1/README.md)

* [~~deprecated1~~](docs/sdks/tag1/README.md#deprecated1) - Deprecated Operation :warning: **Deprecated** Use [get_request_body_flattened_away](docs/sdks/sdk/README.md#get_request_body_flattened_away) instead.
* [list_test1](docs/sdks/tag1/README.md#list_test1) - Get Test1

### [test_group](docs/sdks/testgroup/README.md)


#### [test_group.tag2](docs/sdks/tag2/README.md)

* [post_test](docs/sdks/tag2/README.md#post_test) - Post Test2

#### [test_group.tag3](docs/sdks/tag3/README.md)

* [post_test](docs/sdks/tag3/README.md#post_test) - Post Test2

</details>
<!-- End Available Resources and Operations [operations] -->

<!-- Start Global Parameters [global-parameters] -->
## Global Parameters

Certain parameters are configured globally. These parameters may be set on the SDK client instance itself during initialization. When configured as an option during SDK initialization, These global values will be used as defaults on the operations that use them. When such operations are called, there is a place in each to override the global value, if needed.

For example, you can set `queryParam1` to `"some example query param"` at SDK initialization and then you do not have to pass the same value on calls to operations like `get_request_body_flattened_away`. But if you want to do so you may, which will locally override the global setting. See the example code below for a demonstration.


### Available Globals

The following global parameters are available.
Global parameters can also be set via environment variable.

| Name                    | Type | Description                                                                        | Environment                       |
| ----------------------- | ---- | ---------------------------------------------------------------------------------- | --------------------------------- |
| query_param1            | str  | A long winded, multi-line description<br/>for the query parameter number one.<br/> | SPEAKEASY_QUERY_PARAM1            |
| deprecated_query_param1 | str  | A deprecated description                                                           | SPEAKEASY_DEPRECATED_QUERY_PARAM1 |
| deprecated_query_param2 | str  | The deprecated_query_param2 parameter.                                             | SPEAKEASY_DEPRECATED_QUERY_PARAM2 |
| lone_query_param        | str  | The lone_query_param parameter.                                                    | SPEAKEASY_LONE_QUERY_PARAM        |

### Example

```python
from speakeasy.new_openapi import SDK


with SDK(
    lone_query_param="<value>",
    query_param1="some example query param",
    deprecated_query_param1="some example query param",
    deprecated_query_param2="some example query param",
) as sdk:

    sdk.get_request_body_flattened_away()

    # Use the SDK ...

```
<!-- End Global Parameters [global-parameters] -->

<!-- Start Server-sent event streaming [eventstream] -->
## Server-sent event streaming

[Server-sent events][mdn-sse] are used to stream content from certain
operations. These operations will expose the stream as [Generator][generator] that
can be consumed using a simple `for` loop. The loop will
terminate when the server no longer has any events to send and closes the
underlying connection.  

The stream is also a [Context Manager][context-manager] and can be used with the `with` statement and will close the
underlying connection when the context is exited.

```python
from speakeasy.new_openapi import SDK


with SDK() as sdk:

    res = sdk.chat(request={
        "prompt": "What is the largest city in the world?",
    })

    with res as event_stream:
        for event in event_stream:
            # handle event
            print(event, flush=True)

```

[mdn-sse]: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events
[generator]: https://book.pythontips.com/en/latest/generators.html
[context-manager]: https://book.pythontips.com/en/latest/context_managers.html
<!-- End Server-sent event streaming [eventstream] -->

<!-- Start Pagination [pagination] -->
## Pagination

Some of the endpoints in this SDK support pagination. To use pagination, you make your SDK calls as usual, but the
returned response object will have a `Next` method that can be called to pull down the next group of results. If the
return value of `Next` is `None`, then there are no more pages to be fetched.

Here's an example of one such pagination call:
```python
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    query_param1="some example query param",
) as sdk:

    res = sdk.tag1.list_test1(query_param2=speakeasy.new_openapi.QueryParam2.ONE, page=100, header_param1="some example header param")

    while res is not None:
        # Handle items

        res = res.next()

```
<!-- End Pagination [pagination] -->

<!-- Start File uploads [file-upload] -->
## File uploads

Certain SDK methods accept file objects as part of a request body or multi-part request. It is possible and typically recommended to upload files as a stream rather than reading the entire contents into memory. This avoids excessive memory consumption and potentially crashing with out-of-memory errors when working with very large files. The following example demonstrates how to attach a file stream to a request.

> [!TIP]
>
> For endpoints that handle file uploads bytes arrays can also be used. However, using streams is recommended for large files.
>

```python
from speakeasy.new_openapi import SDK


with SDK() as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```
<!-- End File uploads [file-upload] -->

<!-- Start Retries [retries] -->
## Retries

Some of the endpoints in this SDK support retries. If you use the SDK without any configuration, it will fall back to the default retry strategy provided by the API. However, the default retry strategy can be overridden on a per-operation basis, or across the entire SDK.

To change the default retry strategy for a single API call, simply provide a `RetryConfig` object to the call:
```python
from speakeasy.new_openapi import SDK
from speakeasy.new_openapi.utils import BackoffStrategy, RetryConfig


with SDK() as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    },
        RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False))

    # Handle response
    print(res)

```

If you'd like to override the default retry strategy for all operations that support retries, you can use the `retry_config` optional parameter when initializing the SDK:
```python
from speakeasy.new_openapi import SDK
from speakeasy.new_openapi.utils import BackoffStrategy, RetryConfig


with SDK(
    retry_config=RetryConfig("backoff", BackoffStrategy(1, 50, 1.1, 100), False),
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```
<!-- End Retries [retries] -->

<!-- Start Error Handling [errors] -->
## Error Handling

[`SDKBaseError`](./src/speakeasy/new_openapi/models/sdkbaseerror.py) is the base class for all HTTP error responses. It has the following properties:

| Property           | Type             | Description                                                                             |
| ------------------ | ---------------- | --------------------------------------------------------------------------------------- |
| `err.message`      | `str`            | Error message                                                                           |
| `err.status_code`  | `int`            | HTTP response status code eg `404`                                                      |
| `err.headers`      | `httpx.Headers`  | HTTP response headers                                                                   |
| `err.body`         | `str`            | HTTP body. Can be empty string if no body is returned.                                  |
| `err.raw_response` | `httpx.Response` | Raw HTTP response                                                                       |
| `err.data`         |                  | Optional. Some errors may contain structured data. [See Error Classes](#error-classes). |

### Example
```python
from speakeasy.new_openapi import SDK, models


with SDK() as sdk:
    res = None
    try:

        res = sdk.get_union_errors(page=12)

        while res is not None:
            # Handle items

            res = res.next()


    except models.SDKBaseError as e:
        # The base class for HTTP error responses
        print(e.message)
        print(e.status_code)
        print(e.body)
        print(e.headers)
        print(e.raw_response)

        # Depending on the method different errors may be thrown
        if isinstance(e, models.ErrorsError):
            print(e.data.error)  # str
            print(e.data.code)  # int
```

### Error Classes
**Primary error:**
* [`SDKBaseError`](./src/speakeasy/new_openapi/models/sdkbaseerror.py): The base class for HTTP error responses.

<details><summary>Less common errors (12)</summary>

<br />

**Network errors:**
* [`httpx.RequestError`](https://www.python-httpx.org/exceptions/#httpx.RequestError): Base class for request errors.
    * [`httpx.ConnectError`](https://www.python-httpx.org/exceptions/#httpx.ConnectError): HTTP client was unable to make a request to a server.
    * [`httpx.TimeoutException`](https://www.python-httpx.org/exceptions/#httpx.TimeoutException): HTTP request timed out.


**Inherit from [`SDKBaseError`](./src/speakeasy/new_openapi/models/sdkbaseerror.py)**:
* [`ErrorsError`](./src/speakeasy/new_openapi/models/errorserror.py): Applicable to 5 of 22 methods.*
* [`BadRequestResponseError`](./src/speakeasy/new_openapi/models/badrequestresponseerror.py): Bad Request. Status code `400`. Applicable to 2 of 22 methods.*
* [`TaggedError1`](./src/speakeasy/new_openapi/models/taggederror1.py): Applicable to 2 of 22 methods.*
* [`TaggedError2`](./src/speakeasy/new_openapi/models/taggederror2.py): Something went wrong. Status code `4XX`. Applicable to 1 of 22 methods.*
* [`ErrorType1`](./src/speakeasy/new_openapi/models/errortype1.py): Internal Server Error. Status code `500`. Applicable to 1 of 22 methods.*
* [`ErrorType2`](./src/speakeasy/new_openapi/models/errortype2.py): Internal Server Error. Status code `500`. Applicable to 1 of 22 methods.*
* [`Test2ResponseError`](./src/speakeasy/new_openapi/models/test2responseerror.py): Internal Server Error. Status code `500`. Applicable to 1 of 22 methods.*
* [`ResponseValidationError`](./src/speakeasy/new_openapi/models/responsevalidationerror.py): Type mismatch between the response data and the expected Pydantic model. Provides access to the Pydantic validation error via the `cause` attribute.

</details>

\* Check [the method documentation](#available-resources-and-operations) to see if the error is applicable.
<!-- End Error Handling [errors] -->

<!-- Start Server Selection [server] -->
## Server Selection

### Select Server by Index

You can override the default server globally by passing a server index to the `server_idx: int` optional parameter when initializing the SDK client instance. The selected server will then be used as the default on the operations that use it. This table lists the indexes associated with the available servers:

| #   | Server                                     | Variables                 | Description                     |
| --- | ------------------------------------------ | ------------------------- | ------------------------------- |
| 0   | `http://localhost:35123`                   |                           | The default server.             |
| 1   | `http://{subdomain}.domain.com/v{version}` | `subdomain`<br/>`version` |                                 |
| 2   | `http://{HostName}:{PORT}`                 | `HostName`<br/>`PORT`     | A server with an enum variable. |

If the selected server has variables, you may override its default values through the additional parameters made available in the SDK constructor:

| Variable    | Parameter                 | Supported Values                      | Default       | Description                              |
| ----------- | ------------------------- | ------------------------------------- | ------------- | ---------------------------------------- |
| `subdomain` | `subdomain: str`          | str                                   | `"api"`       |                                          |
| `version`   | `version: str`            | str                                   | `"1"`         |                                          |
| `HostName`  | `host_name: str`          | str                                   | `"localhost"` | The hostname of the server.              |
| `PORT`      | `port: models.ServerPORT` | - `"80"`<br/>- `"8080"`<br/>- `"443"` | `"8080"`      | The port on which the server is running. |

#### Example

```python
from speakeasy.new_openapi import SDK


with SDK(
    server_idx=2,
    host_name="heavy-bowler.org"
    port="443"
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

### Override Server URL Per-Client

The default server can also be overridden globally by passing a URL to the `server_url: str` optional parameter when initializing the SDK client instance. For example:
```python
from speakeasy.new_openapi import SDK


with SDK(
    server_url="http://localhost:8080",
) as sdk:

    res = sdk.post_file(request={
        "file": {
            "file_name": "example.file",
            "content": open("example.file", "rb"),
        },
    })

    # Handle response
    print(res)

```

### Override Server URL Per-Operation

The server URL can also be overridden on a per-operation basis, provided a server list was specified for the operation. For example:
```python
import speakeasy.new_openapi
from speakeasy.new_openapi import SDK


with SDK(
    query_param1="some example query param",
) as sdk:

    res = sdk.tag1.list_test1(query_param2=speakeasy.new_openapi.QueryParam2.ONE, page=100, header_param1="some example header param", server_url="http://localhost:35123")

    while res is not None:
        # Handle items

        res = res.next()

```
<!-- End Server Selection [server] -->

<!-- Start Custom HTTP Client [http-client] -->
## Custom HTTP Client

The Python SDK makes API calls using the [httpx](https://www.python-httpx.org/) HTTP library.  In order to provide a convenient way to configure timeouts, cookies, proxies, custom headers, and other low-level configuration, you can initialize the SDK client with your own HTTP client instance.
Depending on whether you are using the sync or async version of the SDK, you can pass an instance of `HttpClient` or `AsyncHttpClient` respectively, which are Protocol's ensuring that the client has the necessary methods to make API calls.
This allows you to wrap the client with your own custom logic, such as adding custom headers, logging, or error handling, or you can just pass an instance of `httpx.Client` or `httpx.AsyncClient` directly.

For example, you could specify a header for every request that this sdk makes as follows:
```python
from speakeasy.new_openapi import SDK
import httpx

http_client = httpx.Client(headers={"x-custom-header": "someValue"})
s = SDK(client=http_client)
```

or you could wrap the client with your own custom logic:
```python
from speakeasy.new_openapi import SDK
from speakeasy.new_openapi.httpclient import AsyncHttpClient
import httpx

class CustomClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault, None
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[
            bool, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        request.headers["Client-Level-Header"] = "added by client"

        return await self.client.send(
            request, stream=stream, auth=auth, follow_redirects=follow_redirects
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )

s = SDK(async_client=CustomClient(httpx.AsyncClient()))
```
<!-- End Custom HTTP Client [http-client] -->

<!-- Start Resource Management [resource-management] -->
## Resource Management

The `SDK` class implements the context manager protocol and registers a finalizer function to close the underlying sync and async HTTPX clients it uses under the hood. This will close HTTP connections, release memory and free up other resources held by the SDK. In short-lived Python programs and notebooks that make a few SDK method calls, resource management may not be a concern. However, in longer-lived programs, it is beneficial to create a single SDK instance via a [context manager][context-manager] and reuse it across the application.

[context-manager]: https://docs.python.org/3/reference/datamodel.html#context-managers

```python
from speakeasy.new_openapi import SDK
def main():

    with SDK() as sdk:
        # Rest of application here...


# Or when using async:
async def amain():

    async with SDK() as sdk:
        # Rest of application here...
```
<!-- End Resource Management [resource-management] -->

<!-- Start Debugging [debug] -->
## Debugging

You can setup your SDK to emit debug logs for SDK requests and responses.

You can pass your own logger class directly into your SDK.
```python
from speakeasy.new_openapi import SDK
import logging

logging.basicConfig(level=logging.DEBUG)
s = SDK(debug_logger=logging.getLogger("speakeasy.new_openapi"))
```

You can also enable a default debug logger by setting an environment variable `SPEAKEASY_DEBUG` to true.
<!-- End Debugging [debug] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->

# Development

## Maturity

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning usage
to a specific package version. This way, you can install the same version each time without breaking changes unless you are intentionally
looking for the latest version.

## Contributions

While we value open-source contributions to this SDK, this library is generated programmatically. Any manual changes added to internal files will be overwritten on the next generation. 
We look forward to hearing your feedback. Feel free to open a PR or an issue with a proof of concept and we'll do our best to include it in a future release. 

### SDK Created by [Speakeasy](https://www.speakeasy.com/?utm_source=closedapi-test-pythonv2-4&utm_campaign=python)
