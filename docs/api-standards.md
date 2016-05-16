# General
- API should be RESTful.
- API should strictly follow rules described in this document. Changes to this document are welcome but put it in a PR to review. Please consider carefully changes that affect current API result significantly.
- Each URL identifies a resource, which need to follow the format: `/api/<version>/<resource>/{id}.<response_type>` (ex: api/v1/officer/5512.json)
- Your API should be well-versioned. 
- For any published API, the changes should be minimized, removing or changing the structure is not welcome.
- You should follow the python/django/django-rest-framework's convention.
- Any API should be well-logged.
- For CPDBv2 backend, we support only json format.
- URL v. Header (from [1]):
  - If it changes the logic you write to handle the response, put it in the URL.
  - If it doesn’t change the logic for each response, like OAuth info, put it in the header.

# Naming:
- URLs should be a noun, not a verb.
- Use plural nouns only for consistency (no singular nouns).
- Resource uri should be named in `spinal-case`
- Field names should use `snake_case` and follow Python/Django convention.

# HTTP Request/Response
- HTTP methods should be used in the compliance with [HTTP/1.1](http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html) standard.

| HTTP METHOD | POST            | GET       | PUT         | DELETE |
| ----------- | --------------- | --------- | ----------- | ------ |
| /officers   | Create new officer | List officers | Bulk update | Delete all officers |
| /officers/1234  | Error           | Show officer detail   | If exists, update officers, if not error | Delete officer |
- Don't put values in your keys:
```javascript
# good
{
  'officers': [
    { 'id': '123': ...}
  ]
}
```
not
```javascript
# bad
{
  'officers': [
    'id': {
      'something'...
    }
  ]
}
```
- We should utilize the usage of HTTP status codes for semantic purpose and don't re-duplicate them into the json response body

# Practices
- Any API should be mocked and well-document with [apiary](https://apiary.io) before you start implementing them. Example code for Javascript (using `axios`) and Python (using `requests`) is needed for each API.
- For any api endpoint, please clearly define which methods the resources could be used.
- We should not have too deep resource, maximum should be two level nesting (resource/identifier/resource).
- For error message, we use this convention, the messages here is just the ones for user-only. For developer message on how they could start resolving the issues, we put them into the log (which we described in `general` already)
```javascript 
{
  'error': {
    'message': 'This is a message for end-user'
  }
}
```
- In order to filter, pagination, ordering, we use the convention of `django-rest-framework`:
  - Filter: we use model fields as query parameters. Ex: `/api/v1/officers?name=John`
  - Pagination: we use limit and offset with limit is the maximum items to return and offset is the starting position of the query. Ex: `/api/v1/officers?limit=100&offset=5`
  - Ordering: we use `ordering` as query parameter, following by field orderings, prefix the field name with '-' to specify reverse order. Ex: `api/v1/officers?ordering=name,-birth_year`

# References:
- [WhiteHouse's api standards](https://github.com/WhiteHouse/api-standards)
- [Django rest framework](http://www.django-rest-framework.org/)
- [Apigee api design ebook](https://pages.apigee.com/rs/apigee/images/api-design-ebook-2012-03.pdf)
