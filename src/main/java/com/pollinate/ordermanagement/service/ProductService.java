package com.pollinate.ordermanagement.service;

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
