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
