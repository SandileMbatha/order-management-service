package com.pollinate.ordermanagement.service;

import com.pollinate.ordermanagement.dto.OrderItemRequest;
import com.pollinate.ordermanagement.dto.OrderItemResponse;
import com.pollinate.ordermanagement.dto.OrderRequest;
import com.pollinate.ordermanagement.dto.OrderResponse;
import com.pollinate.ordermanagement.entity.Order;
import com.pollinate.ordermanagement.entity.OrderItem;
import com.pollinate.ordermanagement.entity.Product;
import com.pollinate.ordermanagement.exception.InvalidOrderException;
import com.pollinate.ordermanagement.exception.ResourceNotFoundException;
import com.pollinate.ordermanagement.repository.OrderRepository;
import com.pollinate.ordermanagement.repository.ProductRepository;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Service responsible for orchestrating order creation and retrieval.
 *
 * <p>This service handles the core business logic for orders, including:</p>
 * <ul>
 *   <li>Validating that all referenced products exist before order creation</li>
 *   <li>Calculating line totals and order total price</li>
 *   <li>Persisting orders with their associated line items</li>
 * </ul>
 *
 * <p><strong>Validation:</strong> If any product ID in the order request does not exist,
 * the entire order is rejected with a clear error indicating which product IDs are missing.</p>
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderService {

    private static final String LOG_PREFIX = "[Order Service] - ";

    private final OrderRepository orderRepository;
    private final ProductRepository productRepository;

    /**
     * Creates a new order by validating product availability, calculating totals, and persisting the order.
     *
     * <p>This method performs the following steps:</p>
     * <ol>
     *   <li>Collects all requested product IDs from the order items</li>
     *   <li>Fetches products in a single batch query for efficiency</li>
     *   <li>Validates all product IDs exist — rejects the order if any are missing</li>
     *   <li>Builds order items with calculated line totals (price × quantity)</li>
     *   <li>Calculates and sets the order total price</li>
     *   <li>Persists the order with cascaded order items</li>
     * </ol>
     *
     * @param request the order creation request containing item details
     * @return the created order response with calculated totals
     * @throws InvalidOrderException if any referenced product IDs do not exist
     */
    @Transactional
    public OrderResponse createOrder(final OrderRequest request) {
        log.info("{}Creating order with {} item(s)", LOG_PREFIX, request.items().size());

        final Set<Long> requestedIds = request.items().stream()
                .map(OrderItemRequest::productId)
                .collect(Collectors.toSet());

        final List<Product> products = productRepository.findAllById(requestedIds);
        final Map<Long, Product> productMap = products.stream()
                .collect(Collectors.toMap(Product::getId, product -> product));

        validateAllProductsExist(requestedIds, productMap);

        final Order order = buildOrder(request, productMap);
        final Order saved = orderRepository.save(order);

        log.info("{}Order created successfully: id={}, totalPrice={}, items={}",
                LOG_PREFIX, saved.getId(), saved.getTotalPrice(), saved.getItems().size());
        return toResponse(saved);
    }

    /**
     * Retrieves an order by its unique identifier.
     *
     * @param id the order ID
     * @return the order response
     * @throws ResourceNotFoundException if no order exists with the given ID
     */
    @Transactional(readOnly = true)
    public OrderResponse getOrderById(final Long id) {
        log.debug("{}Fetching order id={}", LOG_PREFIX, id);
        return orderRepository.findById(id)
                .map(this::toResponse)
                .orElseThrow(() -> new ResourceNotFoundException("Order not found with id: " + id));
    }

    /**
     * Retrieves a paginated list of all orders.
     *
     * @param pageable pagination parameters
     * @return a page of order responses
     */
    @Transactional(readOnly = true)
    public Page<OrderResponse> getAllOrders(final Pageable pageable) {
        log.debug("{}Listing orders page={}, size={}", LOG_PREFIX, pageable.getPageNumber(), pageable.getPageSize());
        return orderRepository.findAll(pageable).map(this::toResponse);
    }

    /**
     * Validates that all requested product IDs exist in the database.
     * Throws an exception with the list of missing IDs if validation fails.
     *
     * @param requestedIds the set of product IDs from the order request
     * @param productMap   the map of existing products keyed by ID
     * @throws InvalidOrderException if any product IDs are not found
     */
    private void validateAllProductsExist(final Set<Long> requestedIds, final Map<Long, Product> productMap) {
        final List<Long> missingIds = requestedIds.stream()
                .filter(id -> !productMap.containsKey(id))
                .sorted()
                .toList();

        if (!missingIds.isEmpty()) {
            log.warn("{}Order rejected - missing product IDs: {}", LOG_PREFIX, missingIds);
            throw new InvalidOrderException(missingIds);
        }
    }

    /**
     * Builds an Order entity from the request, calculating line totals and the order total.
     *
     * @param request    the order creation request
     * @param productMap the map of validated products
     * @return a fully constructed Order entity ready for persistence
     */
    private Order buildOrder(final OrderRequest request, final Map<Long, Product> productMap) {
        final Order order = Order.builder().build();
        BigDecimal totalPrice = BigDecimal.ZERO;

        for (final OrderItemRequest itemReq : request.items()) {
            final Product product = productMap.get(itemReq.productId());
            final BigDecimal lineTotal = product.getPrice().multiply(BigDecimal.valueOf(itemReq.quantity()));

            final OrderItem item = OrderItem.builder()
                    .product(product)
                    .quantity(itemReq.quantity())
                    .lineTotal(lineTotal)
                    .build();

            order.addItem(item);
            totalPrice = totalPrice.add(lineTotal);
        }

        order.setTotalPrice(totalPrice);
        return order;
    }

    /**
     * Maps an Order entity to its response DTO representation.
     *
     * @param order the order entity
     * @return the mapped order response
     */
    private OrderResponse toResponse(final Order order) {
        final List<OrderItemResponse> items = order.getItems().stream()
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
