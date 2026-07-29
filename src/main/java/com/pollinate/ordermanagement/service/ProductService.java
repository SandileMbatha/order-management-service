package com.pollinate.ordermanagement.service;

import com.pollinate.ordermanagement.dto.ProductRequest;
import com.pollinate.ordermanagement.dto.ProductResponse;
import com.pollinate.ordermanagement.entity.Product;
import com.pollinate.ordermanagement.exception.ResourceNotFoundException;
import com.pollinate.ordermanagement.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Service responsible for product creation and retrieval operations.
 *
 * <p>This service manages the product catalog, providing:</p>
 * <ul>
 *   <li>Product creation with validation</li>
 *   <li>Individual product lookup by ID with caching</li>
 *   <li>Paginated listing of all products</li>
 * </ul>
 *
 * <p><strong>Caching:</strong> Individual product lookups are cached to reduce database load.
 * Cache is evicted when new products are created to maintain consistency.</p>
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ProductService {

    private static final String LOG_PREFIX = "[Product Service] - ";

    private final ProductRepository productRepository;

    /**
     * Creates a new product and persists it to the database.
     *
     * <p>Upon successful creation, the product cache is evicted to ensure
     * subsequent lookups return fresh data.</p>
     *
     * @param request the product creation request containing name, description, and price
     * @return the created product response with generated ID and timestamp
     */
    @Transactional
    @CacheEvict(value = "products", allEntries = true)
    public ProductResponse createProduct(final ProductRequest request) {
        final Product product = Product.builder()
                .name(request.name())
                .description(request.description())
                .price(request.price())
                .build();

        final Product saved = productRepository.save(product);
        log.info("{}Product created: id={}, name={}, price={}", LOG_PREFIX, saved.getId(), saved.getName(), saved.getPrice());
        return toResponse(saved);
    }

    /**
     * Retrieves a product by its unique identifier.
     *
     * <p>Results are cached by product ID to optimise repeated lookups.</p>
     *
     * @param id the product ID
     * @return the product response
     * @throws ResourceNotFoundException if no product exists with the given ID
     */
    @Transactional(readOnly = true)
    @Cacheable(value = "products", key = "#id")
    public ProductResponse getProductById(final Long id) {
        log.debug("{}Fetching product id={}", LOG_PREFIX, id);
        return productRepository.findById(id)
                .map(this::toResponse)
                .orElseThrow(() -> new ResourceNotFoundException("Product not found with id: " + id));
    }

    /**
     * Retrieves a paginated list of all products.
     *
     * @param pageable pagination parameters
     * @return a page of product responses
     */
    @Transactional(readOnly = true)
    public Page<ProductResponse> getAllProducts(final Pageable pageable) {
        log.debug("{}Listing products page={}, size={}", LOG_PREFIX, pageable.getPageNumber(), pageable.getPageSize());
        return productRepository.findAll(pageable).map(this::toResponse);
    }

    /**
     * Maps a Product entity to its response DTO representation.
     *
     * @param product the product entity
     * @return the mapped product response
     */
    private ProductResponse toResponse(final Product product) {
        return new ProductResponse(
                product.getId(),
                product.getName(),
                product.getDescription(),
                product.getPrice(),
                product.getCreatedAt()
        );
    }
}
