# SDK

This is the Clavata SDK for Python.

## Usage

The SDK is quite simple to use. First it needs to be imported (assuming of course that you're using this as an external package):

```python
from clavata_sdk import ClavataClient
```

Next, you'll need a Clavata API key to instantiate the client:

```python
api_key = "YOUR_API_KEY"

# Now instantiate the client with your API key:
client = ClavataClient(host="gateway.app.clavata.ai", port=443, auth_token=api_key)
```

> If you prefer, the `auth_token` parameter can be omitted and the API key can be set via the environment. To do this simply set the `CLAVATA_API_KEY` environment variable.

Finally, you can call various methods on the client with the generated request and response models:

```python
# Async request
response = client.create_job(CreateJobRequest(name="my-job", ...))

# Streaming request
async for response in client.evaluate(EvaluateRequest(name="my-job", ...)):
    print(response)
```

## Dealing with Refusal Errors

Under certain circumstances, the Clavata API may refuse to evaluate a piece of content. Reasons include:

- The content (image) was found in a database of known CSAM material
- The content (image) is in a format that is not currently supported (webp, png, jpg supported as of publishing)
- The content is corrupt, incomplete or otherwise invalid

When the API refuses, an exception will be raised by the SDK. Because exceptions may also be raised for other reasons (i.e., network errors, invalid requests, etc), the SDK provides a distinct error type that both helps you tell when an error is due to a refusal, and also allows you to get more information about why the request was refused.

The `EvaluationRefusedError` type will only be raised if an evaluation was refused for one of the reasons mentioned above.

When a refusal occurs, the response from the API is processed to hydrate this error with information on which pieces of content included in the request were refused, and why each one was refused (if there was more than one piece of content in the request which was refused).

The simplest way to examine refusals is to look at the `refusals` attribute on the error type. It will always be a list containing one entry for each piece of content that was refused. Each entry is of type `RefusedContent` and includes a `reason` as well as the `content_hash` that identifies the piece of content.

```python
try:
    client.evaluate(...)
except EvaluationRefusedError as err:
    print("Refused content: ", err.refusals)
```

The error type also comes with a number of additional properties that are useful if you don't want to have to iterate over the entire list of refusals (for example, if you only sent 1 piece of content in the request). These properties are

- `top_reason`: Returns the "most important" reason for the refusal, with CSAM > UNSUPPORTED_FORMAT > INVALID_CONTENT.
- `most_common_reason`: If there are many refusals, returns the most common reason among them. In math terms, the "mode".
- `first_reason`: Always returns the first reason in the list, regardless of how many refusals there were.

You can also access all the content that was refused in a flattened list by using the `refused_content_hashes` property on the error type.

```python
try:
    client.evaluate(...)
except EvaluationRefusedError as err:
    print("Refused content: ", err.refusals)

    # Get the first refusal reason
    print("First refusal reason: ", err.first_reason)

    # Get all the content that was refused
    print("Refused hashes: ", err.refused_content_hashes)
```

Finally, the refusal "reasons" are implemented as a python enum, allowing you to easily compare the "reason" in the error to the canonical "reason" values to determine why the content was refused (and then what action to take).

```python
from clavata_sdk import RefusalReason, EvaluationRefusedError
try:
    client.evaluate(...)
except EvaluationRefusedError as err:
    if err.first_reason == RefusalReason.CSAM:
        # Now you know that CSAM was found. Act accordingly.
    # etc ...
```

