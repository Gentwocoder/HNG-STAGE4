# API Documentation Access

## ✅ OpenAPI Schema Generated Successfully!

Your User Service API documentation is now available in multiple formats:

### 1. OpenAPI Schema File
**Location**: `/home/gentle/Documents/HNG-STAGE4/hngstage4/schema.yml`

This is a standard OpenAPI 3.0 specification file that can be:
- Imported into Postman
- Used with Swagger UI
- Shared with other services
- Used for client generation

### 2. Interactive Swagger UI Documentation
**URL**: `http://127.0.0.1:8000/api/schema/docs/`

Features:
- ✅ Interactive API testing
- ✅ Request/response examples
- ✅ Authentication support
- ✅ Try it out functionality

**To access**:
```bash
# Start the server
python manage.py runserver

# Open in browser
http://127.0.0.1:8000/api/schema/docs/
```

### 3. ReDoc Documentation
**URL**: `http://127.0.0.1:8000/api/docs/redoc/`

Features:
- ✅ Clean, responsive layout
- ✅ Three-panel design
- ✅ Search functionality
- ✅ Code samples in multiple languages

**To access**:
```bash
# Start the server
python manage.py runserver

# Open in browser
http://127.0.0.1:8000/api/docs/redoc/
```

### 4. Raw Schema Endpoint
**URL**: `http://127.0.0.1:8000/api/schema/`

Returns the OpenAPI schema in JSON/YAML format.

```bash
curl http://127.0.0.1:8000/api/schema/
```

## Regenerating the Schema

Whenever you make changes to your API, regenerate the schema:

```bash
cd /home/gentle/Documents/HNG-STAGE4/hngstage4
python manage.py spectacular --file schema.yml
```

## Using with Postman

1. Open Postman
2. Click **Import**
3. Choose the `schema.yml` file
4. All endpoints will be imported with examples

## Using with Other Tools

### Swagger Editor
1. Visit: https://editor.swagger.io/
2. Import `schema.yml`
3. Edit and validate your API

### Swagger Codegen
Generate client libraries:
```bash
# Install swagger-codegen
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate -i schema.yml -g python -o ./client-python

# Generate JavaScript client
openapi-generator-cli generate -i schema.yml -g javascript -o ./client-js
```

## Documentation Features

Your API documentation includes:

### ✅ All Endpoints
- Authentication (Register, Login, Logout, Token Refresh)
- User Profile (Get, Update, Change Password)
- Notification Preferences (Get, Update)
- Push Tokens (List, Create, Update, Delete)
- Health Check

### ✅ Request/Response Examples
- JSON schema for all requests
- Response codes (200, 201, 400, 401, 404, etc.)
- Error response examples

### ✅ Authentication
- JWT Bearer token authentication
- Security schemes documented
- Token usage examples

### ✅ Data Models
- User model
- UserProfile model
- NotificationPreference model
- PushToken model
- All serializers documented

## Quick Access Commands

```bash
# View schema in terminal
cat schema.yml

# Validate schema
python manage.py spectacular --file schema.yml --validate

# Generate with color output
python manage.py spectacular --color --file schema.yml

# Generate without validation
python manage.py spectacular --file schema.yml --fail-on-warn
```

## Schema Information

- **Format**: OpenAPI 3.0.3
- **API Version**: 1.0.0
- **Service**: User Service
- **Generated**: November 9, 2025
- **File Size**: ~13KB

## Available Documentation URLs

Once your server is running (`python manage.py runserver`):

| Documentation Type | URL | Description |
|-------------------|-----|-------------|
| Swagger UI | `http://127.0.0.1:8000/api/schema/docs/` | Interactive API docs |
| ReDoc | `http://127.0.0.1:8000/api/docs/redoc/` | Beautiful API docs |
| Raw Schema | `http://127.0.0.1:8000/api/schema/` | JSON/YAML schema |
| Schema File | `./schema.yml` | Downloaded file |

## Next Steps

1. **Start the server**:
   ```bash
   python manage.py runserver
   ```

2. **Open Swagger UI**:
   ```bash
   # Linux
   xdg-open http://127.0.0.1:8000/api/schema/docs/
   
   # macOS
   open http://127.0.0.1:8000/api/schema/docs/
   ```

3. **Test the endpoints** directly from the browser

4. **Share the documentation** with your team by sharing:
   - The `schema.yml` file
   - The Swagger UI URL (when deployed)
   - The ReDoc URL (when deployed)

## Tips

- 📝 The schema is automatically generated from your code
- 🔄 Regenerate after making API changes
- 📤 Export to share with frontend developers
- 🧪 Use Swagger UI for interactive testing
- 📚 Use ReDoc for readable documentation

---

**Your API is fully documented and ready for integration! 🎉**

Access the interactive docs at: `http://127.0.0.1:8000/api/schema/docs/`
