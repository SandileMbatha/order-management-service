package com.pollinate.ordermanagement.controller;

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
