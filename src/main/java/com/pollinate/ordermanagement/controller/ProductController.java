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
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing product management endpoints.
 *
 * <p>Provides CRUD operations for the product catalog with pagination support.</p>
 */
@Slf4j
@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
@Tag(name = "Products", description = "Product management endpoints")
public class ProductController {

    private static final String LOG_PREFIX = "[Product Controller] - ";

    private final ProductService productService;

    /**
     * Creates a new product in the catalog.
     *
     * @param request the product creation request
     * @return the created product with generated ID
     */
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new product")
    public ProductResponse createProduct(@Valid @RequestBody final ProductRequest request) {
        log.info("{}POST /api/products - Creating product: {}", LOG_PREFIX, request.name());
        return productService.createProduct(request);
    }

    /**
     * Retrieves a single product by its ID.
     *
     * @param id the product ID
     * @return the product response
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get a product by ID")
    public ProductResponse getProduct(@PathVariable final Long id) {
        log.info("{}GET /api/products/{}", LOG_PREFIX, id);
        return productService.getProductById(id);
    }

    /**
     * Lists all products with pagination support.
     *
     * @param pageable pagination parameters (page, size, sort)
     * @return a page of product responses
     */
    @GetMapping
    @Operation(summary = "List all products with pagination")
    public Page<ProductResponse> getAllProducts(final Pageable pageable) {
        log.info("{}GET /api/products?page={}&size={}", LOG_PREFIX, pageable.getPageNumber(), pageable.getPageSize());
        return productService.getAllProducts(pageable);
    }
}
