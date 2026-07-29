package com.pollinate.ordermanagement.service;

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
