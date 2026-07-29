package com.pollinate.ordermanagement.controller;

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
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * REST controller exposing order management endpoints.
 *
 * <p>Provides order creation and retrieval operations with pagination support.</p>
 */
@Slf4j
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Tag(name = "Orders", description = "Order management endpoints")
public class OrderController {

    private static final String LOG_PREFIX = "[Order Controller] - ";

    private final OrderService orderService;

    /**
     * Creates a new order from the provided items.
     *
     * <p>All referenced product IDs must exist; otherwise the order is rejected.</p>
     *
     * @param request the order creation request containing line items
     * @return the created order with calculated totals
     */
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    @Operation(summary = "Create a new order")
    public OrderResponse createOrder(@Valid @RequestBody final OrderRequest request) {
        log.info("{}POST /api/orders - Creating order with {} item(s)", LOG_PREFIX, request.items().size());
        return orderService.createOrder(request);
    }

    /**
     * Retrieves a single order by its ID.
     *
     * @param id the order ID
     * @return the order response with line items
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get an order by ID")
    public OrderResponse getOrder(@PathVariable final Long id) {
        log.info("{}GET /api/orders/{}", LOG_PREFIX, id);
        return orderService.getOrderById(id);
    }

    /**
     * Lists all orders with pagination support.
     *
     * @param pageable pagination parameters (page, size, sort)
     * @return a page of order responses
     */
    @GetMapping
    @Operation(summary = "List all orders with pagination")
    public Page<OrderResponse> getAllOrders(final Pageable pageable) {
        log.info("{}GET /api/orders?page={}&size={}", LOG_PREFIX, pageable.getPageNumber(), pageable.getPageSize());
        return orderService.getAllOrders(pageable);
    }
}
