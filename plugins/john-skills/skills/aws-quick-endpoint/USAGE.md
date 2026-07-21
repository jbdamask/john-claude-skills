# Pets API

**Endpoint:** `https://3kqc0btu03.execute-api.us-east-1.amazonaws.com/pets`
**Auth token:** `4959c96c-e100-4a8c-abaa-65b63437b5c0`

## Setup

```bash
TOKEN="4959c96c-e100-4a8c-abaa-65b63437b5c0"
URL="https://3kqc0btu03.execute-api.us-east-1.amazonaws.com/pets"
```

## Create a record

```bash
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "x-api-token: $TOKEN" \
  -d '{"name": "Max", "species": "dog", "breed": "Golden Retriever", "age": 5}' | python3 -m json.tool
```

Omit `id` and one is auto-generated. `created_at` and `updated_at` are added automatically.

## List all (paginated)

```bash
curl -s "$URL?limit=25" -H "x-api-token: $TOKEN" | python3 -m json.tool
```

If `next_token` appears in the response, pass it to get the next page:

```bash
curl -s "$URL?limit=25&next_token=<TOKEN_FROM_RESPONSE>" \
  -H "x-api-token: $TOKEN" | python3 -m json.tool
```

## Get one

```bash
curl -s "$URL/f2913219-379b-4266-af8b-e93dc8c4cf9b" -H "x-api-token: $TOKEN" | python3 -m json.tool
```

## Update

```bash
curl -s -X PUT "$URL/f2913219-379b-4266-af8b-e93dc8c4cf9b" \
  -H "Content-Type: application/json" \
  -H "x-api-token: $TOKEN" \
  -d '{"name": "Luna", "species": "cat", "age": 4}' | python3 -m json.tool
```

PUT is a full replace — send all fields you want to keep. `created_at` is preserved, `updated_at` is refreshed.

## Delete

```bash
curl -s -X DELETE "$URL/f2913219-379b-4266-af8b-e93dc8c4cf9b" -H "x-api-token: $TOKEN" | python3 -m json.tool
```

## Notes

- **CORS:** Enabled for all origins — safe to call from browser JavaScript
- **Limits:** Max body 10KB, max nesting depth 5, max 50 attributes per level
- **Pagination tokens** are HMAC-signed and tamper-proof

## Cleanup

**Warning:** This permanently deletes the DynamoDB table and all data.

```bash
aws cloudformation delete-stack --profile sandbox --stack-name quick-ep-pets-sandbox-20260319-143820
```
