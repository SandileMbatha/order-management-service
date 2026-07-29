# Order Management Service

A Spring Boot microservice for managing Products and Orders.

## Technology Stack

- **Java 21** with **Spring Boot 3.3.2**
- **H2** in-memory database
- **Spring Data JPA** for persistence
- **Spring Security** with API Key authentication
- **SpringDoc OpenAPI** for Swagger documentation
- **Lombok** to reduce boilerplate
- **Maven** for build management

## Schema Design

The database uses three tables with proper relational mapping:

```
products            orders              order_items
--------            ------              -----------
id (PK)             id (PK)             id (PK)
name                total_price         order_id (FK -> orders)
description         created_at          product_id (FK -> products)
price                                   quantity
created_at                              line_total
```

**Design decisions:**
- `order_items` is a join table that enables many-to-many between orders and products, with additional fields (quantity, line_total)
- `total_price` is stored on the order (denormalized) for query performance, calculated at creation time
- `line_total` is stored per item to preserve the price at time of order (product prices could change later)
- Timestamps use `@PrePersist` for automatic creation time

## How to Run

### Prerequisites
- Java 21
- Maven 3.x

### Start the Service
```bash
mvn clean spring-boot:run
```

The service starts on **http://localhost:8080**

### API Documentation (Swagger UI)
Open **http://localhost:8080/swagger-ui.html** in your browser.

### H2 Database Console
Open **http://localhost:8080/h2-console**
- JDBC URL: `jdbc:h2:mem:orderdb`
- Username: `sa`
- Password: *(empty)*

## Authentication

All API endpoints require an API key via the `X-API-Key` header:

```
X-API-Key: my-secret-api-key-2024
```

Swagger UI and H2 console are publicly accessible without authentication.

## API Endpoints

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/products` | Create a product |
| GET | `/api/products/{id}` | Get product by ID |
| GET | `/api/products?page=0&size=10` | List all products (paginated) |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders` | Create an order |
| GET | `/api/orders/{id}` | Get order by ID |
| GET | `/api/orders?page=0&size=10` | List all orders (paginated) |

### Example: Create a Product
```bash
curl -X POST http://localhost:8080/api/products \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-api-key-2024" \
  -d '{"name": "Laptop", "description": "A powerful laptop", "price": 999.99}'
```

### Example: Create an Order
```bash
curl -X POST http://localhost:8080/api/orders \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-api-key-2024" \
  -d '{"items": [{"productId": 1, "quantity": 2}]}'
```

## How to Run Tests

```bash
# Run all tests
mvn test

# Run unit tests only
mvn test -Dtest="*ServiceTest"

# Run integration tests only
mvn test -Dtest="*IntegrationTest"
```

## Project Structure

```
src/main/java/com/pollinate/ordermanagement/
├── OrderManagementApplication.java     # Entry point
├── config/
│   ├── ApiKeyAuthFilter.java           # API key authentication filter
│   ├── OpenApiConfig.java              # Swagger/OpenAPI configuration
│   └── SecurityConfig.java             # Spring Security configuration
├── controller/
│   ├── OrderController.java            # Order REST endpoints
│   └── ProductController.java          # Product REST endpoints
├── dto/
│   ├── OrderItemRequest.java           # Order item input
│   ├── OrderItemResponse.java          # Order item output
│   ├── OrderRequest.java               # Order creation input
│   ├── OrderResponse.java              # Order output
│   ├── ProductRequest.java             # Product creation input
│   └── ProductResponse.java            # Product output
├── entity/
│   ├── Order.java                      # Order JPA entity
│   ├── OrderItem.java                  # Order-Product join entity
│   └── Product.java                    # Product JPA entity
├── exception/
│   ├── GlobalExceptionHandler.java     # Centralized error handling
│   ├── InvalidOrderException.java      # Missing products exception
│   └── ResourceNotFoundException.java  # 404 exception
├── repository/
│   ├── OrderRepository.java
│   └── ProductRepository.java
└── service/
    ├── OrderService.java               # Order business logic
    └── ProductService.java             # Product business logic
```

## Assumptions

1. Products are simple entities (no inventory/stock tracking)
2. Product prices are fixed at order creation time (line_total preserves this)
3. Orders are immutable once created (no update/delete endpoints)
4. API key is configured in application.properties (in production, use a secrets manager)
5. Pagination defaults to page 0, size 20 (Spring Data defaults)
