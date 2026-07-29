#!/usr/bin/env python3
"""Build the order-management-service with proper git history."""
import os, subprocess, pathlib

BASE = "/Users/SandileMbatha/Documents/MegahTZ/order-management-service"
os.chdir(BASE)

def write(path, content):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

def commit(files, msg):
    subprocess.run(["git", "add"] + files, check=True)
    subprocess.run(["git", "commit", "-m", msg], check=True)

# ============================================================
# COMMIT 1: Project initialization
# ============================================================
write(".gitignore", """target/
*.class
*.jar
*.war
*.log
.idea/
*.iml
.DS_Store
.mvn/
mvnw
mvnw.cmd
""")

write("pom.xml", """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.3.2</version>
        <relativePath/>
    </parent>

    <groupId>com.pollinate</groupId>
    <artifactId>order-management-service</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <name>Order Management Service</name>
    <description>Order Management Microservice - Technical Challenge</description>

    <properties>
        <java.version>21</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <excludes>
                        <exclude>
                            <groupId>org.projectlombok</groupId>
                            <artifactId>lombok</artifactId>
                        </exclude>
                    </excludes>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
""")

write("src/main/java/com/pollinate/ordermanagement/OrderManagementApplication.java", """package com.pollinate.ordermanagement;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class OrderManagementApplication {

    public static void main(String[] args) {
        SpringApplication.run(OrderManagementApplication.class, args);
    }
}
""")

write("src/main/resources/application.properties", """spring.application.name=order-management-service
server.port=8080

# H2 In-Memory Database
spring.datasource.url=jdbc:h2:mem:orderdb
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA / Hibernate
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true

# H2 Console (for development)
spring.h2.console.enabled=true
spring.h2.console.path=/h2-console
""")

commit([".gitignore", "pom.xml",
        "src/main/java/com/pollinate/ordermanagement/OrderManagementApplication.java",
        "src/main/resources/application.properties"],
       "Initialize Spring Boot project with Maven, H2, and JPA\n\n"
       "- Set up pom.xml with Spring Boot 3.3.2 and Java 21\n"
       "- Add web, data-jpa, validation, h2, and lombok dependencies\n"
       "- Configure H2 in-memory database in application.properties\n"
       "- Create main application entry point")
print("COMMIT 1 DONE")

# ============================================================
# COMMIT 2: Domain entities
# ============================================================
PKG = "src/main/java/com/pollinate/ordermanagement"

write(f"{PKG}/entity/Product.java", """package com.pollinate.ordermanagement.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "products")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String description;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
""")

write(f"{PKG}/entity/Order.java", """package com.pollinate.ordermanagement.entity;

import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "orders")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "total_price", nullable = false, precision = 12, scale = 2)
    private BigDecimal totalPrice;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    @Builder.Default
    private List<OrderItem> items = new ArrayList<>();

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    public void addItem(OrderItem item) {
        items.add(item);
        item.setOrder(this);
    }
}
""")

write(f"{PKG}/entity/OrderItem.java", """package com.pollinate.ordermanagement.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.*;
import java.math.BigDecimal;

@Entity
@Table(name = "order_items")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    @JsonIgnore
    private Order order;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @Column(nullable = false)
    private Integer quantity;

    @Column(name = "line_total", nullable = false, precision = 12, scale = 2)
    private BigDecimal lineTotal;
}
""")

write(f"{PKG}/repository/ProductRepository.java", """package com.pollinate.ordermanagement.repository;

import com.pollinate.ordermanagement.entity.Product;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<Product, Long> {
}
""")

write(f"{PKG}/repository/OrderRepository.java", """package com.pollinate.ordermanagement.repository;

import com.pollinate.ordermanagement.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<Order, Long> {
}
""")

commit([f"{PKG}/entity/Product.java", f"{PKG}/entity/Order.java", f"{PKG}/entity/OrderItem.java",
        f"{PKG}/repository/ProductRepository.java", f"{PKG}/repository/OrderRepository.java"],
       "Add domain entities and JPA repositories\n\n"
       "- Product entity with name, description, price fields\n"
       "- Order entity with total_price and one-to-many OrderItems\n"
       "- OrderItem join entity linking orders to products with quantity\n"
       "- Spring Data JPA repositories for Product and Order")
print("COMMIT 2 DONE")

# ============================================================
# COMMIT 3: DTOs and exception handling
# ============================================================
write(f"{PKG}/dto/ProductRequest.java", """package com.pollinate.ordermanagement.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import java.math.BigDecimal;

public record ProductRequest(
        @NotBlank(message = "Product name is required")
        String name,
        String description,
        @NotNull(message = "Price is required")
        @Positive(message = "Price must be positive")
        BigDecimal price
) {}
""")

write(f"{PKG}/dto/ProductResponse.java", """package com.pollinate.ordermanagement.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record ProductResponse(
        Long id,
        String name,
        String description,
        BigDecimal price,
        LocalDateTime createdAt
) {}
""")

write(f"{PKG}/dto/OrderItemRequest.java", """package com.pollinate.ordermanagement.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record OrderItemRequest(
        @NotNull(message = "Product ID is required")
        Long productId,
        @NotNull(message = "Quantity is required")
        @Positive(message = "Quantity must be positive")
        Integer quantity
) {}
""")

write(f"{PKG}/dto/OrderRequest.java", """package com.pollinate.ordermanagement.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public record OrderRequest(
        @NotEmpty(message = "Order must contain at least one item")
        @Valid
        List<OrderItemRequest> items
) {}
""")

write(f"{PKG}/dto/OrderItemResponse.java", """package com.pollinate.ordermanagement.dto;

import java.math.BigDecimal;

public record OrderItemResponse(
        Long productId,
        String productName,
        BigDecimal unitPrice,
        Integer quantity,
        BigDecimal lineTotal
) {}
""")

write(f"{PKG}/dto/OrderResponse.java", """package com.pollinate.ordermanagement.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

public record OrderResponse(
        Long id,
        BigDecimal totalPrice,
        LocalDateTime createdAt,
        List<OrderItemResponse> items
) {}
""")

write(f"{PKG}/exception/ResourceNotFoundException.java", """package com.pollinate.ordermanagement.exception;

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}
""")

write(f"{PKG}/exception/InvalidOrderException.java", """package com.pollinate.ordermanagement.exception;

import java.util.List;

public class InvalidOrderException extends RuntimeException {
    private final List<Long> missingProductIds;

    public InvalidOrderException(List<Long> missingProductIds) {
        super("Products not found with IDs: " + missingProductIds);
        this.missingProductIds = missingProductIds;
    }

    public List<Long> getMissingProductIds() {
        return missingProductIds;
    }
}
""")

write(f"{PKG}/exception/GlobalExceptionHandler.java", """package com.pollinate.ordermanagement.exception;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(ResourceNotFoundException ex) {
        log.warn("Resource not found: {}", ex.getMessage());
        return buildResponse(HttpStatus.NOT_FOUND, ex.getMessage());
    }

    @ExceptionHandler(InvalidOrderException.class)
    public ResponseEntity<Map<String, Object>> handleInvalidOrder(InvalidOrderException ex) {
        log.warn("Invalid order rejected: {}", ex.getMessage());
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("timestamp", LocalDateTime.now());
        body.put("status", HttpStatus.BAD_REQUEST.value());
        body.put("error", "Invalid Order");
        body.put("message", ex.getMessage());
        body.put("missingProductIds", ex.getMissingProductIds());
        return ResponseEntity.badRequest().body(body);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(MethodArgumentNotValidException ex) {
        Map<String, String> fieldErrors = ex.getBindingResult().getFieldErrors().stream()
                .collect(Collectors.toMap(FieldError::getField, FieldError::getDefaultMessage, (a, b) -> a));
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("timestamp", LocalDateTime.now());
        body.put("status", HttpStatus.BAD_REQUEST.value());
        body.put("error", "Validation Failed");
        body.put("fieldErrors", fieldErrors);
        return ResponseEntity.badRequest().body(body);
    }

    private ResponseEntity<Map<String, Object>> buildResponse(HttpStatus status, String message) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("timestamp", LocalDateTime.now());
        body.put("status", status.value());
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        return ResponseEntity.status(status).body(body);
    }
}
""")

commit([f"{PKG}/dto/", f"{PKG}/exception/"],
       "Add DTOs, validation, and global exception handling\n\n"
       "- Request/response records with Bean Validation annotations\n"
       "- ResourceNotFoundException for 404 responses\n"
       "- InvalidOrderException with missing product IDs for order rejection\n"
       "- GlobalExceptionHandler for consistent error responses")
print("COMMIT 3 DONE")

# ============================================================
# COMMIT 4: Service layer with business logic
# ============================================================
write(f"{PKG}/service/ProductService.java", """package com.pollinate.ordermanagement.service;

import com.pollinate.ordermanagement.dto.ProductRequest;
import com.pollinate.ordermanagement.dto.ProductResponse;
import com.pollinate.ordermanagement.entity.Product;
import com.pollinate.ordermanagement.exception.ResourceNotFoundException;
import com.pollinate.ordermanagement.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProductService {

    private final ProductRepository productRepository;

    @Transactional
    public ProductResponse createProduct(ProductRequest request) {
        Product product = Product.builder()
                .name(request.name())
                .description(request.description())
                .price(request.price())
                .build();

        Product saved = productRepository.save(product);
        log.info("Product created: id={}, name={}, price={}", saved.getId(), saved.getName(), saved.getPrice());
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public ProductResponse getProductById(Long id) {
        log.debug("Fetching product id={}", id);
        return productRepository.findById(id)
                .map(this::toResponse)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public Page<ProductResponse> getAllProducts(Pageable pageable) {
        log.debug("Listing products page={}, size={}", pageable.getPageNumber(), pageable.getPageSize());
        return productRepository.findAll(pageable).map(this::toResponse);
    }

    private ProductResponse toResponse(Product product) {
        return new ProductResponse(
                product.getId(),
                product.getName(),
                product.getDescription(),
                product.getPrice(),
                product.getCreatedAt()
        );
    }
}
""")

write(f"{PKG}/service/OrderService.java", """package com.pollinate.ordermanagement.service;

import com.pollinate.ordermanagement.dto.*;
import com.pollinate.ordermanagement.entity.Order;
import com.pollinate.ordermanagement.entity.OrderItem;
import com.pollinate.ordermanagement.entity.Product;
import com.pollinate.ordermanagement.exception.InvalidOrderException;
import com.pollinate.ordermanagement.exception.ResourceNotFoundException;
import com.pollinate.ordermanagement.repository.OrderRepository;
import com.pollinate.ordermanagement.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;

    @Transactional
    public OrderResponse createOrder(OrderRequest request) {
        log.info("Creating order with {} item(s)", request.items().size());

        // Collect requested product IDs
        Set<Long> requestedIds = request.items().stream()
                .map(OrderItemRequest::productId)
                .collect(Collectors.toSet());

        // Fetch all products in one query
        List<Product> products = productRepository.findAllById(requestedIds);
        Map<Long, Product> productMap = products.stream()
                .collect(Collectors.toMap(Product::getId, p -> p));

        // Validate all products exist
        List<Long> missingIds = requestedIds.stream()
                .filter(id -> !productMap.containsKey(id))
                .sorted()
                .toList();

        if (!missingIds.isEmpty()) {
            log.warn("Order rejected - missing product IDs: {}", missingIds);
            throw new InvalidOrderException(missingIds);
        }

        // Build the order
        Order order = Order.builder().build();
        BigDecimal totalPrice = BigDecimal.ZERO;

        for (OrderItemRequest itemReq : request.items()) {
            Product product = productMap.get(itemReq.productId());
            BigDecimal lineTotal = product.getPrice().multiply(BigDecimal.valueOf(itemReq.quantity()));

            OrderItem item = OrderItem.builder()
                    .product(product)
                    .quantity(itemReq.quantity())
                    .lineTotal(lineTotal)
                    .build();

            order.addItem(item);
            totalPrice = totalPrice.add(lineTotal);
        }

        order.setTotalPrice(totalPrice);
        Order saved = orderRepository.save(order);

        log.info("Order created: id={}, totalPrice={}, items={}", saved.getId(), totalPrice, saved.getItems().size());
        return toResponse(saved);
    }

    @Transactional(readOnly = true)
    public OrderResponse getOrderById(Long id) {
        log.debug("Fetching order id={}", id);
        return orderRepository.findById(id)
                .map(this::toResponse)
                .orElseThrow(() -> new ResourceNotFoundException("Order not found with id: " + id));
    }

    @Transactional(readOnly = true)
    public Page<OrderResponse> getAllOrders(Pageable pageable) {
        log.debug("Listing orders page={}, size={}", pageable.getPageNumber(), pageable.getPageSize());
        return orderRepository.findAll(pageable).map(this::toResponse);
    }

    private OrderResponse toResponse(Order order) {
        List<OrderItemResponse> items = order.getItems().stream()
                .map(item -> new OrderItemResponse(
                        item.getProduct().getId(),
                        item.getProduct().getName(),
                        item.getProduct().getPrice(),
                        item.getQuantity(),
                        item.getLineTotal()
                ))
                .toList();

        return new OrderResponse(order.getId(), order.getTotalPrice(), order.getCreatedAt(), items);
    }
}
""")

commit([f"{PKG}/service/"],
       "Add service layer with product and order business logic\n\n"
       "- ProductService: create, get by ID, list with pagination\n"
       "- OrderService: create with validation, price calculation\n"
       "- Order creation validates all product IDs exist before proceeding\n"
       "- Total price auto-calculated from product prices and quantities")
print("COMMIT 4 DONE")

# ============================================================
# COMMIT 5: REST controllers
# ============================================================
write(f"{PKG}/controller/ProductController.java", """package com.pollinate.ordermanagement.controller;

import com.pollinate.ordermanagement.dto.ProductRequest;
import com.pollinate.ordermanagement.dto.ProductResponse;
import com.pollinate.ordermanagement.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Products", description = "Product management endpoints")
public class ProductController {

    private final ProductService productService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new product")
    public ProductResponse createProduct(@Valid @RequestBody ProductRequest request) {
        log.info("POST /api/products - Creating product: {}", request.name());
        return productService.createProduct(request);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get a product by ID")
    public ProductResponse getProduct(@PathVariable Long id) {
        log.info("GET /api/products/{}", id);
        return productService.getProductById(id);
    }

    @GetMapping
    @Operation(summary = "List all products with pagination")
    public Page<ProductResponse> getAllProducts(Pageable pageable) {
        log.info("GET /api/products?page={}&size={}", pageable.getPageNumber(), pageable.getPageSize());
        return productService.getAllProducts(pageable);
    }
}
""")

write(f"{PKG}/controller/OrderController.java", """package com.pollinate.ordermanagement.controller;

import com.pollinate.ordermanagement.dto.OrderRequest;
import com.pollinate.ordermanagement.dto.OrderResponse;
import com.pollinate.ordermanagement.service.OrderService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Orders", description = "Order management endpoints")
public class OrderController {

    private final OrderService orderService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new order")
    public OrderResponse createOrder(@Valid @RequestBody OrderRequest request) {
        log.info("POST /api/orders - Creating order with {} item(s)", request.items().size());
        return orderService.createOrder(request);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get an order by ID")
    public OrderResponse getOrder(@PathVariable Long id) {
        log.info("GET /api/orders/{}", id);
        return orderService.getOrderById(id);
    }

    @GetMapping
    @Operation(summary = "List all orders with pagination")
    public Page<OrderResponse> getAllOrders(Pageable pageable) {
        log.info("GET /api/orders?page={}&size={}", pageable.getPageNumber(), pageable.getPageSize());
        return orderService.getAllOrders(pageable);
    }
}
""")

commit([f"{PKG}/controller/"],
       "Add REST controllers for Product and Order endpoints\n\n"
       "- ProductController: POST, GET by ID, GET all with pagination\n"
       "- OrderController: POST, GET by ID, GET all with pagination\n"
       "- Request validation with @Valid\n"
       "- Meaningful request logging on each endpoint")
print("COMMIT 5 DONE")

# ============================================================
# COMMIT 6: Spring Security with API Key authentication
# ============================================================
write(f"{PKG}/config/SecurityConfig.java", """package com.pollinate.ordermanagement.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Value("${api.security.key}")
    private String apiKey;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(new ApiKeyAuthFilter(apiKey), UsernamePasswordAuthenticationFilter.class)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/swagger-ui/**", "/v3/api-docs/**", "/swagger-ui.html").permitAll()
                .requestMatchers("/h2-console/**").permitAll()
                .requestMatchers("/actuator/**").permitAll()
                .anyRequest().authenticated()
            )
            .headers(headers -> headers.frameOptions(frame -> frame.disable()));

        return http.build();
    }
}
""")

write(f"{PKG}/config/ApiKeyAuthFilter.java", """package com.pollinate.ordermanagement.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

@RequiredArgsConstructor
public class ApiKeyAuthFilter extends OncePerRequestFilter {

    private static final String API_KEY_HEADER = "X-API-Key";
    private final String validApiKey;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        String apiKey = request.getHeader(API_KEY_HEADER);

        if (validApiKey.equals(apiKey)) {
            UsernamePasswordAuthenticationToken auth =
                    new UsernamePasswordAuthenticationToken("api-client", null, Collections.emptyList());
            SecurityContextHolder.getContext().setAuthentication(auth);
        }

        filterChain.doFilter(request, response);
    }
}
""")

# Update pom.xml to add security dependency
pom = pathlib.Path("pom.xml").read_text()
pom = pom.replace(
    """        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>""",
    """        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework.security</groupId>
            <artifactId>spring-security-test</artifactId>
            <scope>test</scope>
        </dependency>"""
)
pathlib.Path("pom.xml").write_text(pom)

# Add API key to properties
props = pathlib.Path("src/main/resources/application.properties").read_text()
props += "\n# Security\napi.security.key=my-secret-api-key-2024\n"
pathlib.Path("src/main/resources/application.properties").write_text(props)

commit(["pom.xml", "src/main/resources/application.properties",
        f"{PKG}/config/SecurityConfig.java", f"{PKG}/config/ApiKeyAuthFilter.java"],
       "Add API Key authentication with Spring Security\n\n"
       "- Custom ApiKeyAuthFilter validates X-API-Key header\n"
       "- All API endpoints require authentication\n"
       "- Swagger UI and H2 console paths are publicly accessible\n"
       "- Stateless session management (no cookies)")
print("COMMIT 6 DONE")

# ============================================================
# COMMIT 7: Swagger/OpenAPI documentation
# ============================================================
pom = pathlib.Path("pom.xml").read_text()
pom = pom.replace(
    """        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>""",
    """        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.6.0</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>"""
)
pathlib.Path("pom.xml").write_text(pom)

write(f"{PKG}/config/OpenApiConfig.java", """package com.pollinate.ordermanagement.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Order Management API")
                        .description("REST API for managing Products and Orders")
                        .version("1.0.0"))
                .addSecurityItem(new SecurityRequirement().addList("ApiKeyAuth"))
                .components(new Components()
                        .addSecuritySchemes("ApiKeyAuth", new SecurityScheme()
                                .type(SecurityScheme.Type.APIKEY)
                                .in(SecurityScheme.In.HEADER)
                                .name("X-API-Key")));
    }
}
""")

commit(["pom.xml", f"{PKG}/config/OpenApiConfig.java"],
       "Add Swagger/OpenAPI documentation\n\n"
       "- Add springdoc-openapi dependency for auto-generated docs\n"
       "- Configure OpenAPI with API key security scheme\n"
       "- Swagger UI available at /swagger-ui.html\n"
       "- API docs available at /v3/api-docs")
print("COMMIT 7 DONE")

# ============================================================
# COMMIT 8: Unit tests
# ============================================================
TPKG = "src/test/java/com/pollinate/ordermanagement"

write(f"{TPKG}/service/ProductServiceTest.java", """package com.pollinate.ordermanagement.service;

import com.pollinate.ordermanagement.dto.ProductRequest;
import com.pollinate.ordermanagement.dto.ProductResponse;
import com.pollinate.ordermanagement.entity.Product;
import com.pollinate.ordermanagement.exception.ResourceNotFoundException;
import com.pollinate.ordermanagement.repository.ProductRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductService productService;

    @Test
    void createProduct_shouldSaveAndReturnProduct() {
        ProductRequest request = new ProductRequest("Laptop", "A powerful laptop", new BigDecimal("999.99"));

        Product saved = Product.builder()
                .id(1L).name("Laptop").description("A powerful laptop")
                .price(new BigDecimal("999.99")).createdAt(LocalDateTime.now()).build();

        when(productRepository.save(any(Product.class))).thenReturn(saved);

        ProductResponse response = productService.createProduct(request);

        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.name()).isEqualTo("Laptop");
        assertThat(response.price()).isEqualByComparingTo("999.99");
        verify(productRepository).save(any(Product.class));
    }

    @Test
    void getProductById_shouldReturnProduct_whenExists() {
        Product product = Product.builder()
                .id(1L).name("Phone").price(new BigDecimal("499.99")).createdAt(LocalDateTime.now()).build();

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        ProductResponse response = productService.getProductById(1L);

        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.name()).isEqualTo("Phone");
    }

    @Test
    void getProductById_shouldThrowException_whenNotFound() {
        when(productRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> productService.getProductById(99L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("99");
    }

    @Test
    void getAllProducts_shouldReturnPagedResults() {
        Product product = Product.builder()
                .id(1L).name("Tablet").price(new BigDecimal("299.99")).createdAt(LocalDateTime.now()).build();
        Page<Product> page = new PageImpl<>(List.of(product));

        when(productRepository.findAll(any(PageRequest.class))).thenReturn(page);

        Page<ProductResponse> result = productService.getAllProducts(PageRequest.of(0, 10));

        assertThat(result.getContent()).hasSize(1);
        assertThat(result.getContent().get(0).name()).isEqualTo("Tablet");
    }
}
""")

write(f"{TPKG}/service/OrderServiceTest.java", """package com.pollinate.ordermanagement.service;

import com.pollinate.ordermanagement.dto.OrderItemRequest;
import com.pollinate.ordermanagement.dto.OrderRequest;
import com.pollinate.ordermanagement.dto.OrderResponse;
import com.pollinate.ordermanagement.entity.Order;
import com.pollinate.ordermanagement.entity.OrderItem;
import com.pollinate.ordermanagement.entity.Product;
import com.pollinate.ordermanagement.exception.InvalidOrderException;
import com.pollinate.ordermanagement.exception.ResourceNotFoundException;
import com.pollinate.ordermanagement.repository.OrderRepository;
import com.pollinate.ordermanagement.repository.ProductRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private OrderService orderService;

    @Test
    void createOrder_shouldCalculateTotalAndSave() {
        Product laptop = Product.builder().id(1L).name("Laptop").price(new BigDecimal("1000.00")).createdAt(LocalDateTime.now()).build();
        Product mouse = Product.builder().id(2L).name("Mouse").price(new BigDecimal("25.00")).createdAt(LocalDateTime.now()).build();

        when(productRepository.findAllById(any())).thenReturn(List.of(laptop, mouse));
        when(orderRepository.save(any(Order.class))).thenAnswer(invocation -> {
            Order order = invocation.getArgument(0);
            order.setId(1L);
            order.setCreatedAt(LocalDateTime.now());
            return order;
        });

        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(1L, 2),  // 2 laptops = 2000
                new OrderItemRequest(2L, 3)   // 3 mice = 75
        ));

        OrderResponse response = orderService.createOrder(request);

        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.totalPrice()).isEqualByComparingTo("2075.00");
        assertThat(response.items()).hasSize(2);
        verify(orderRepository).save(any(Order.class));
    }

    @Test
    void createOrder_shouldRejectWhenProductNotFound() {
        Product laptop = Product.builder().id(1L).name("Laptop").price(new BigDecimal("1000.00")).createdAt(LocalDateTime.now()).build();
        when(productRepository.findAllById(any())).thenReturn(List.of(laptop));

        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(1L, 1),
                new OrderItemRequest(99L, 1)
        ));

        assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(InvalidOrderException.class)
                .hasMessageContaining("99");
    }

    @Test
    void createOrder_shouldRejectWhenMultipleProductsMissing() {
        when(productRepository.findAllById(any())).thenReturn(List.of());

        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(10L, 1),
                new OrderItemRequest(20L, 1)
        ));

        assertThatThrownBy(() -> orderService.createOrder(request))
                .isInstanceOf(InvalidOrderException.class)
                .extracting(e -> ((InvalidOrderException) e).getMissingProductIds())
                .asList()
                .containsExactly(10L, 20L);
    }

    @Test
    void getOrderById_shouldReturnOrder_whenExists() {
        Product product = Product.builder().id(1L).name("Phone").price(new BigDecimal("500.00")).createdAt(LocalDateTime.now()).build();
        OrderItem item = OrderItem.builder().id(1L).product(product).quantity(1).lineTotal(new BigDecimal("500.00")).build();
        Order order = Order.builder().id(1L).totalPrice(new BigDecimal("500.00")).createdAt(LocalDateTime.now()).items(List.of(item)).build();

        when(orderRepository.findById(1L)).thenReturn(Optional.of(order));

        OrderResponse response = orderService.getOrderById(1L);

        assertThat(response.id()).isEqualTo(1L);
        assertThat(response.totalPrice()).isEqualByComparingTo("500.00");
    }

    @Test
    void getOrderById_shouldThrowException_whenNotFound() {
        when(orderRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> orderService.getOrderById(99L))
                .isInstanceOf(ResourceNotFoundException.class)
                .hasMessageContaining("99");
    }
}
""")

commit([f"{TPKG}/"],
       "Add unit tests for ProductService and OrderService\n\n"
       "- ProductServiceTest: create, get by ID, not found, pagination\n"
       "- OrderServiceTest: create with price calculation, reject missing products,\n"
       "  reject multiple missing products, get by ID, not found\n"
       "- Uses Mockito for repository mocking and AssertJ for assertions")
print("COMMIT 8 DONE")

# ============================================================
# COMMIT 9: Integration tests
# ============================================================
write(f"{TPKG}/controller/ProductControllerIntegrationTest.java", """package com.pollinate.ordermanagement.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pollinate.ordermanagement.dto.ProductRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class ProductControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private static final String API_KEY = "my-secret-api-key-2024";

    @Test
    void shouldCreateAndRetrieveProduct() throws Exception {
        ProductRequest request = new ProductRequest("Integration Test Product", "A test product", new BigDecimal("49.99"));

        String response = mockMvc.perform(post("/api/products")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Integration Test Product"))
                .andExpect(jsonPath("$.price").value(49.99))
                .andReturn().getResponse().getContentAsString();

        Long id = objectMapper.readTree(response).get("id").asLong();

        mockMvc.perform(get("/api/products/{id}", id)
                        .header("X-API-Key", API_KEY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Integration Test Product"));
    }

    @Test
    void shouldReturnNotFound_whenProductDoesNotExist() throws Exception {
        mockMvc.perform(get("/api/products/99999")
                        .header("X-API-Key", API_KEY))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.message").exists());
    }

    @Test
    void shouldReturnValidationError_whenNameMissing() throws Exception {
        ProductRequest request = new ProductRequest("", null, new BigDecimal("10.00"));

        mockMvc.perform(post("/api/products")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void shouldReturnUnauthorized_withoutApiKey() throws Exception {
        mockMvc.perform(get("/api/products"))
                .andExpect(status().isForbidden());
    }

    @Test
    void shouldListProductsWithPagination() throws Exception {
        mockMvc.perform(get("/api/products?page=0&size=5")
                        .header("X-API-Key", API_KEY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.pageable").exists())
                .andExpect(jsonPath("$.totalElements").exists());
    }
}
""")

write(f"{TPKG}/controller/OrderControllerIntegrationTest.java", """package com.pollinate.ordermanagement.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.pollinate.ordermanagement.dto.OrderItemRequest;
import com.pollinate.ordermanagement.dto.OrderRequest;
import com.pollinate.ordermanagement.dto.ProductRequest;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    private static final String API_KEY = "my-secret-api-key-2024";

    private Long productId;

    @BeforeEach
    void setUp() throws Exception {
        ProductRequest productRequest = new ProductRequest("Order Test Product", "For order tests", new BigDecimal("100.00"));

        String response = mockMvc.perform(post("/api/products")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(productRequest)))
                .andReturn().getResponse().getContentAsString();

        productId = objectMapper.readTree(response).get("id").asLong();
    }

    @Test
    void shouldCreateOrderAndCalculateTotal() throws Exception {
        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(productId, 3)  // 3 x 100 = 300
        ));

        String response = mockMvc.perform(post("/api/orders")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.totalPrice").value(300.00))
                .andExpect(jsonPath("$.items").isArray())
                .andExpect(jsonPath("$.items[0].quantity").value(3))
                .andReturn().getResponse().getContentAsString();

        Long orderId = objectMapper.readTree(response).get("id").asLong();

        mockMvc.perform(get("/api/orders/{id}", orderId)
                        .header("X-API-Key", API_KEY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(orderId));
    }

    @Test
    void shouldRejectOrder_whenProductDoesNotExist() throws Exception {
        OrderRequest request = new OrderRequest(List.of(
                new OrderItemRequest(99999L, 1)
        ));

        mockMvc.perform(post("/api/orders")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.missingProductIds").isArray())
                .andExpect(jsonPath("$.missingProductIds[0]").value(99999));
    }

    @Test
    void shouldRejectOrder_whenItemsEmpty() throws Exception {
        OrderRequest request = new OrderRequest(List.of());

        mockMvc.perform(post("/api/orders")
                        .header("X-API-Key", API_KEY)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void shouldListOrdersWithPagination() throws Exception {
        mockMvc.perform(get("/api/orders?page=0&size=5")
                        .header("X-API-Key", API_KEY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.pageable").exists());
    }
}
""")

commit([f"{TPKG}/controller/"],
       "Add integration tests for Product and Order controllers\n\n"
       "- Full Spring Boot context with H2 database\n"
       "- ProductControllerIntegrationTest: CRUD, validation, auth, pagination\n"
       "- OrderControllerIntegrationTest: create with total calc, reject missing\n"
       "  products, reject empty items, pagination\n"
       "- Verifies API key authentication enforcement")
print("COMMIT 9 DONE")

# ============================================================
# COMMIT 10: Caching and README
# ============================================================

# Enable caching in main app
app_path = f"{PKG}/OrderManagementApplication.java"
app_content = pathlib.Path(app_path).read_text()
app_content = app_content.replace(
    "import org.springframework.boot.autoconfigure.SpringBootApplication;",
    "import org.springframework.boot.autoconfigure.SpringBootApplication;\nimport org.springframework.cache.annotation.EnableCaching;"
)
app_content = app_content.replace("@SpringBootApplication", "@SpringBootApplication\n@EnableCaching")
pathlib.Path(app_path).write_text(app_content)

# Add caching to ProductService
svc_path = f"{PKG}/service/ProductService.java"
svc_content = pathlib.Path(svc_path).read_text()
svc_content = svc_content.replace(
    "import org.springframework.stereotype.Service;",
    "import org.springframework.cache.annotation.CacheEvict;\nimport org.springframework.cache.annotation.Cacheable;\nimport org.springframework.stereotype.Service;"
)
svc_content = svc_content.replace(
    "    @Transactional\n    public ProductResponse createProduct",
    "    @Transactional\n    @CacheEvict(value = \"products\", allEntries = true)\n    public ProductResponse createProduct"
)
svc_content = svc_content.replace(
    "    @Transactional(readOnly = true)\n    public ProductResponse getProductById",
    "    @Transactional(readOnly = true)\n    @Cacheable(value = \"products\", key = \"#id\")\n    public ProductResponse getProductById"
)
pathlib.Path(svc_path).write_text(svc_content)

# Add caching config to properties
props = pathlib.Path("src/main/resources/application.properties").read_text()
props += "\n# Caching\nspring.cache.type=simple\n"
pathlib.Path("src/main/resources/application.properties").write_text(props)

# Add spring-boot-starter-cache to pom
pom = pathlib.Path("pom.xml").read_text()
pom = pom.replace(
    """        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>""",
    """        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-cache</artifactId>
        </dependency>"""
)
pathlib.Path("pom.xml").write_text(pom)

commit(["pom.xml", "src/main/resources/application.properties",
        f"{PKG}/OrderManagementApplication.java", f"{PKG}/service/ProductService.java"],
       "Add simple caching for product lookups\n\n"
       "- Enable Spring Cache with @EnableCaching\n"
       "- Cache individual product lookups by ID\n"
       "- Evict product cache on create to maintain consistency\n"
       "- Add spring-boot-starter-cache dependency")
print("COMMIT 10 DONE")

# ============================================================
# COMMIT 11: README
# ============================================================
write("README.md", """# Order Management Service

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
curl -X POST http://localhost:8080/api/products \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: my-secret-api-key-2024" \\
  -d '{"name": "Laptop", "description": "A powerful laptop", "price": 999.99}'
```

### Example: Create an Order
```bash
curl -X POST http://localhost:8080/api/orders \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: my-secret-api-key-2024" \\
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
""")

commit(["README.md"],
       "Add comprehensive README with setup, API docs, and design notes\n\n"
       "- How to run the service and tests\n"
       "- Schema design decisions documented\n"
       "- API endpoint reference with curl examples\n"
       "- Project structure overview\n"
       "- Assumptions and design notes")
print("COMMIT 11 DONE")

print("\n=== ALL COMMITS DONE ===")

